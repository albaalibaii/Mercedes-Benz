"""Pipeline de preparación de features para el clustering de clientes (Reto 2).

Uso:
    from features import cargar_datos, construir_pipeline, FEATURES
    df = cargar_datos()
    pipe = construir_pipeline()
    X = pipe.fit_transform(df)                             # matriz escalada, 1 fila por cliente
    clientes = pipe.named_steps["agregar"].transform(df)   # tabla de cliente sin escalar (para perfilar)
"""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OrdinalEncoder, StandardScaler

RUTA_DATOS = "datos_reto_mercedes_benz_malackathon.csv"

ORDEN_EDAD = ["<25", "25-34", "35-44", "45-54", "55-64", "65+"]
ORDEN_FINANCIACION = ["never_active", "was_active", "active_FL_only", "active_FL_and_CASH"]

# Nivel de gama por clase de modelo: 1 compacto · 2 medio · 3 alto · 4 lujo/deportivo
GAMA_POR_CLASE = {
    "A-Class": 1, "B-Class": 1, "B-/GLA-/GLB-Class": 1, "GLA-Class": 1, "CLA-Class": 1,
    "A-Class/CLA-Class": 1, "EQA-/EQB-Class": 1, "fortwo / forfour": 1, "Citan": 1,
    "C-Class": 2, "GLC-Class": 2, "EQC-Class": 2, "CLE-Class": 2, "CLK-Class": 2,
    "SLK-Class": 2, "SLK-/SLC-Class": 2, "X-Class": 2,
    "V-Class / Vito": 2, "Viano/Vito": 2, "Sprinter": 2,
    "E-Class": 3, "E-Class Coupé/Cabriolet": 3, "GLE-Class": 3, "GLE-/GLS-Class": 3,
    "M-Class": 3, "M-/GL-Class": 3, "M-/GL-/GLE-/GLS-Class": 3, "EQE-Class": 3,
    "CLS-Class": 3, "R-Class": 3,
    "S-Class": 4, "S-Class Coupé/Cabriolet": 4, "CL-Class": 4, "G-Class": 4, "EQS-Class": 4,
    "SL-Class": 4, "AMG GT": 4, "AMG GT 4-Door": 4, "SLS AMG": 4, "AMG ONE": 4,
    "SLR McLaren": 4, "Maybach": 4,
}
# Respaldo para model_class nulo (modelos nuevos): primera palabra de vehicle_type sin "AMG"
GAMA_POR_PREFIJO = {
    "A": 1, "B": 1, "CLA": 1, "GLA": 1, "GLB": 1, "EQA": 1, "EQB": 1,
    "C": 2, "GLC": 2, "CLE": 2, "EQC": 2,
    "E": 3, "GLE": 3, "EQE": 3, "CLS": 3,
    "S": 4, "GLS": 4, "G": 4, "EQS": 4, "SL": 4, "GT": 4,
}
ELECTRIFICADO_POR_NOMBRE = r"^EQ|\d\s?e(?:\s|$)|\sde(?:\s|$)|electric"

# Features que entran en K-Means, agrupadas por el tratamiento que reciben
CAT_ORDINALES = ["age_range", "finance_leasing_status"]
NUM_LOG = ["n_vehiculos_historico", "n_vehiculos_actuales"]
NUM = ["meses_cliente", "antiguedad_vehiculo", "gama_max", "pct_electrificado",
       "pct_furgoneta", "n_canales_consentidos", "tiene_telemetria", "poder_adquisitivo_pct_pais",
       "visitas_taller_pct_pais"]
FEATURES = CAT_ORDINALES + NUM_LOG + NUM

# Topes para que unos pocos clientes extremos (flotas, coches clásicos) no dominen K-Means
TOPES = {"n_vehiculos_historico": 10, "n_vehiculos_actuales": 5,
         "antiguedad_vehiculo": 20, "meses_cliente": 120}

COLS_TELEMETRIA = ["trip_distance_average", "trip_distance_median", "operating_hours_total",
                   "fuel_consumption_average", "speed_average", "speed_median"]


def cargar_datos(ruta=RUTA_DATOS):
    return pd.read_csv(ruta, low_memory=False)


def _gama(df):
    gama = df["model_class"].map(GAMA_POR_CLASE)
    prefijo = df["vehicle_type"].str.replace(r"^AMG\s+", "", regex=True).str.split().str[0]
    return gama.fillna(prefijo.map(GAMA_POR_PREFIJO))


def _electrificado(df):
    por_motor = df["engine_concept"].isin(["PLUGIN_HYBRID", "ELECTRIC"])
    por_nombre = df["vehicle_type"].str.contains(ELECTRIFICADO_POR_NOMBRE, regex=True, na=False)
    conocido = df["engine_concept"].notna()
    return np.where(conocido, por_motor, por_nombre)


def agregar_clientes(df):
    """Relación cliente–vehículo (1 fila por vehículo) → 1 fila por cliente con features derivadas.

    Devuelve también columnas de perfilado (país, género, telemetría...) que NO entran en el modelo.
    """
    reg = pd.to_datetime(df["date_of_first_registration"], errors="coerce")
    fecha_ref = reg.max()
    v = pd.DataFrame({
        "client_id": df["client_id"],
        "antiguedad": (fecha_ref - reg).dt.days / 365.25,
        "actual": df["is_current_vehicle"],
        "gama": _gama(df),
        "electrificado": _electrificado(df).astype(float),
        "furgoneta": (df["product_group"] == "T").astype(float),
        "amg": df["vehicle_type"].str.startswith("AMG", na=False).astype(float),
        "b2b": (df["role_type"] == "B2B").astype(float),
        "visitas": df["workshop_visits_warranty_goodwill"],
        "telemetria": df[COLS_TELEMETRIA].notna().any(axis=1).astype(float),
        **{c: df[c] for c in COLS_TELEMETRIA},
    })
    # Antigüedad del vehículo "de referencia": el actual más reciente; si no tiene actual, el más reciente
    v["antig_actual"] = v["antiguedad"].where(v["actual"])
    g = v.groupby("client_id", sort=False)
    veh = pd.DataFrame({
        "n_vehiculos_historico": g.size(),
        "antiguedad_vehiculo": g["antig_actual"].min().fillna(g["antiguedad"].min()),
        "gama_max": g["gama"].max(),
        "pct_electrificado": g["electrificado"].mean(),
        "pct_furgoneta": g["furgoneta"].mean(),
        "visitas_taller_por_vehiculo": g["visitas"].mean(),
        "tiene_telemetria": g["telemetria"].max(),
        "pct_amg": g["amg"].mean(),
        "es_b2b": g["b2b"].max(),
        **{c: g[c].median() for c in COLS_TELEMETRIA},
    })

    # Atributos de cliente: constantes entre sus filas (verificado en el Reto 1) → primera fila
    cli = df.drop_duplicates("client_id").set_index("client_id")
    out = pd.DataFrame({
        "age_range": cli["age_range"],
        "finance_leasing_status": cli["finance_leasing_status"],
        "meses_cliente": cli["months_as_mb_customer"],
        "n_vehiculos_actuales": cli["currently_connected_vehicles"],
        "n_canales_consentidos": cli[["consent_phone_communication_channel",
                                      "consent_epost_communication_channel",
                                      "consent_post_communication_channel"]].sum(axis=1),
        # Poder adquisitivo relativo a su país (percentil 0-1); nulo → mediana del país (0.5)
        "poder_adquisitivo_pct_pais": cli.groupby("country_code")["purchasing_power_per_household_eur"]
                                         .rank(pct=True).fillna(0.5),
        # Solo perfilado
        "country_code": cli["country_code"],
        "gender_derived": cli["gender_derived"].fillna("unknown"),
        "poder_adquisitivo_hogar_eur": cli["purchasing_power_per_household_eur"],
        "consent_phone": cli["consent_phone_communication_channel"],
        "consent_email": cli["consent_epost_communication_channel"],
        "consent_post": cli["consent_post_communication_channel"],
    }).join(veh)
    # Visitas al taller relativas a su país: AT y CH registran las visitas en garantía de forma muy
    # distinta (52 % vs 23 % de clientes con 0 visitas con coches de la misma antigüedad)
    out["visitas_taller_pct_pais"] = out.groupby("country_code")["visitas_taller_por_vehiculo"].rank(pct=True)
    out.index.name = "client_id"
    return out


def recortar_extremos(clientes):
    """Aplica los TOPES superiores (winsorización) a las features del modelo."""
    clientes = clientes.copy()
    for col, tope in TOPES.items():
        clientes[col] = clientes[col].clip(upper=tope)
    return clientes


def construir_pipeline():
    ordinales = Pipeline([
        ("imputar", SimpleImputer(strategy="most_frequent")),
        ("codificar", OrdinalEncoder(categories=[ORDEN_EDAD, ORDEN_FINANCIACION])),
        ("escalar", StandardScaler()),
    ])
    logaritmicas = Pipeline([
        ("imputar", SimpleImputer(strategy="median")),
        ("log", FunctionTransformer(np.log1p, feature_names_out="one-to-one")),
        ("escalar", StandardScaler()),
    ])
    numericas = Pipeline([
        ("imputar", SimpleImputer(strategy="median")),
        ("escalar", StandardScaler()),
    ])
    preprocesar = ColumnTransformer([
        ("ord", ordinales, CAT_ORDINALES),
        ("log", logaritmicas, NUM_LOG),
        ("num", numericas, NUM),
    ], remainder="drop", verbose_feature_names_out=False)
    return Pipeline([
        ("agregar", FunctionTransformer(agregar_clientes)),
        ("recortar", FunctionTransformer(recortar_extremos)),
        ("preprocesar", preprocesar),
    ]).set_output(transform="pandas")


# Modelo final elegido en el Reto 3 (reutilizado en el Reto 4 para obtener los mismos clusters)
K_FINAL = 6
SEMILLA = 42


def ajustar_kmeans(X, k=K_FINAL):
    return KMeans(n_clusters=k, n_init=10, random_state=SEMILLA).fit(X)
