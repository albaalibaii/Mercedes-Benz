# Reto 2 · Feature engineering — Explicación

> Documento de apoyo al notebook [`Reto2_Features.ipynb`](Reto2_Features.ipynb) y al código [`features.py`](features.py).
> Explica qué es cada cosa, por qué se hace así y por qué elegimos cada decisión.

---

## 0. ¿Qué es el *feature engineering*?

Una **feature** (variable o característica) es cada dato que le damos al modelo para describir a un cliente: su edad,
cuántos coches tiene, si son eléctricos…

El ***feature engineering*** es el trabajo de **elegir y preparar** esas variables. K-Means no entiende de negocio: solo
mide **distancias** entre clientes a partir de números. Las variables que le demos determinan **qué significa "parecerse"**.

- Si le damos el país, agrupará por país.
- Si le damos el número de identificación, agrupará por algo sin sentido.
- Si una variable tiene valores enormes (euros) y otra pequeños (0 a 1), la de euros dominará.

Por eso este reto es donde más se decide **qué tipo de segmentos saldrán**.

---

## 1. El punto de partida: cinco decisiones que vienen del Reto 1

1. **Una fila por cliente.** El fichero tiene una fila por relación cliente–vehículo. Agregamos para que cada cliente
   cuente una sola vez y acabe en un único segmento.
2. **El país no puede segmentar.** Suiza y Austria tienen niveles de renta muy distintos. Si el modelo ve el país o el
   poder adquisitivo en euros, los segmentos serán "suizos" y "austriacos", algo que ya sabemos y que no ayuda a hacer
   campañas. Por eso:
   - `country_code` **no entra** en el modelo;
   - el poder adquisitivo y las visitas al taller se miden **comparando a cada cliente con los de su país**.
3. **La telemetría no entra.** Falta por motivos estructurales (eléctricos, no propietarios, coches antiguos). Usarla
   como "cliente conectado" mezclaría esas tres cosas y penalizaría a los dueños de eléctricos. Solo se usa para describir.
4. **Poder adquisitivo por habitante, no por hogar.** El de por hogar sube en las zonas rurales solo porque los hogares
   son más grandes (Reto 1, apartado 6.2).
5. **Los datos externos de salud y seguridad vial se añaden, pero no segmentan.** Se unen a cada cliente para
   describirlo (apartado 4 bis).

---

## 2. Las 12 features del modelo

| Feature | Qué mide | ¿Derivada? | Por qué sirve para segmentar |
|---|---|---|---|
| `age_range` | Tramo de edad | No | Etapa vital: condiciona el coche, el canal y la oferta |
| `finance_leasing_status` | Relación con la financiación: nunca → antes → leasing → leasing y contado | No | Palanca directa para ofertas de renovación |
| `n_vehiculos_historico` | Cuántos Mercedes ha tenido | **Sí** | Fidelidad acumulada |
| `n_vehiculos_actuales` | Cuántos tiene conectados hoy | No | Tamaño de la relación actual (0 = inactivo; 2 o más = multi-vehículo) |
| `meses_cliente` | Meses de relación con la marca | No | Antigüedad como cliente |
| `antiguedad_vehiculo` | Años de su coche actual | **Sí** | Cercanía a la renovación: un coche de 6 años o más es candidato a cambio |
| `gama_max` | Nivel de la gama más alta que ha tenido (1 a 4) | **Sí** | Posicionamiento premium |
| `pct_electrificado` | % de sus coches híbridos enchufables o eléctricos | **Sí** | Afinidad con la electrificación (campañas EQ) |
| `pct_furgoneta` | % de sus coches que son furgonetas | **Sí** | Uso profesional o familiar grande |
| `n_canales_consentidos` | Por cuántos canales acepta comunicaciones (0 a 3) | **Sí** | Si se le puede contactar |
| `poder_adquisitivo_pct_pais` | Riqueza **por habitante** de su zona, **comparada con su país** | **Sí** | Capacidad de compra sin que el país domine ni el tamaño del hogar la infle |
| `visitas_taller_pct_pais` | Visitas al taller en garantía **comparadas con su país** | **Sí** | Uso del taller: base para planes de mantenimiento |

Una **feature derivada** es una variable que **no está en el fichero** y la creamos a partir de otras. El reto pedía al
menos una; hemos creado **8**.

### Por qué estas y no otras

Seguimos tres criterios:

1. **Que describa al cliente**, no a su zona o al sistema.
2. **Que sea útil para marketing**: cada feature responde a una pregunta comercial (¿le toca renovar? ¿es premium? ¿le
   interesa lo eléctrico? ¿se le puede contactar?).
3. **Que no esté sesgada ni repetida**: nada que dependa del país o de cómo se registró el dato, y nada que diga lo mismo
   que otra feature.

---

## 3. Cómo se construye cada feature derivada

- **`antiguedad_vehiculo`** (la sugerida en el reto): años entre la matriculación y la **fecha de referencia** del fichero.
  Como fecha de referencia usamos la matriculación más reciente del dataset (2 de octubre de 2026), no la fecha de hoy,
  para que el cálculo no cambie según el día en que se ejecute. Si el cliente tiene varios coches, tomamos el **actual más
  reciente**; si no tiene ninguno actual, su coche más reciente.
- **`gama_max`**: asignamos a cada clase de modelo un nivel:
  - 1 = compacto (A, B, CLA, GLA, GLB, EQA, EQB, smart, Citan);
  - 2 = medio (C, GLC, CLE, EQC, Vito, Sprinter…);
  - 3 = alto (E, GLE, EQE, CLS…);
  - 4 = lujo o deportivo (S, G, EQS, SL, AMG GT, Maybach…).

  Cuando falta la clase (modelos nuevos), la deducimos del nombre comercial ("GLC 400 4MATIC" → GLC → nivel 2).
  Usamos el **máximo** porque refleja hasta dónde ha llegado el cliente en la gama.
- **`pct_electrificado`**: un coche cuenta como electrificado si es híbrido enchufable o eléctrico. Como el tipo de motor
  falta en el 44 % de las filas, lo deducimos del nombre: "EQ…" (eléctricos), "… e" y "… de" (híbridos enchufables) o
  "electric".
- **`n_vehiculos_historico`** y **`pct_furgoneta`**: se cuentan las filas de cada cliente.
- **`n_canales_consentidos`**: teléfono + email + correo postal (cada uno vale 1 si da permiso).
- **`poder_adquisitivo_pct_pais`** y **`visitas_taller_pct_pais`**: se calcula el **percentil dentro del país** (ver abajo).

### ¿Qué es un percentil y por qué lo usamos?

El **percentil** dice qué posición ocupa un valor dentro de un grupo, de 0 a 1. Un percentil de 0,80 significa "por
encima del 80 % de su grupo".

**Ejemplo con el poder adquisitivo:**

- Un austriaco y un suizo que viven en zonas con 45.000 € por habitante tienen el mismo valor en euros.
- Pero el austriaco vive en una de las zonas **más ricas de Austria**: está por encima de prácticamente todos los
  austriacos (percentil ≈ 1). El suizo vive en una zona **por debajo de lo normal en Suiza**: solo supera al 19 % de los
  suizos (percentil ≈ 0,19).

Para una campaña local, lo relevante es la posición **dentro de su mercado**. Además, al usar percentiles por país, la
variable ya no distingue países: en ambos va de 0 a 1 con la misma distribución.

**Ejemplo con las visitas al taller:** el 52 % de los austriacos tiene 0 visitas frente al 23 % de los suizos, con coches
de antigüedad parecida. Es una diferencia de registro. Con el percentil, comparamos a cada cliente con los de su país y
esa diferencia desaparece.

**¿Y los clientes sin dato de poder adquisitivo?** Reciben **0,5**, que es exactamente la **mediana de su país**
(la decisión tomada en el Reto 1).

### Diferencias de país que sí mantenemos

- **Leasing**: el 29 % de los suizos tiene leasing activo frente al 13 % de los austriacos. El leasing está muy extendido
  en Suiza: es comportamiento **real** y muy útil comercialmente (renovaciones), así que no lo corregimos.
- **Electrificación**: 26 % en Austria frente a 16 % en Suiza. También es real.

---

## 4. Variables que dejamos fuera del modelo (pero usamos para describir)

| Variable | Por qué fuera |
|---|---|
| País | Los segmentos separarían países |
| Poder adquisitivo en euros, población, hogares | En euros depende del país. Población y hogares miden el tamaño de la zona, no al cliente |
| Poder adquisitivo **por hogar** | Mide en parte el tamaño del hogar: sube en el campo porque los hogares son más grandes, no más ricos |
| Datos de zona (accidentes, % graves, mortalidad, distancia al hospital) | Describen la zona, no al cliente (ver 4 bis) |
| Género | Es **inferido** (no lo declaró el cliente), falta en el 17 %, y segmentar por género inferido es poco fiable y delicado |
| B2B (empresa) | Solo el 1,8 % de las relaciones: crearía un segmento minúsculo. Las flotas ya se ven con el nº de vehículos |
| Telemetría | Nulo estructural (ver Reto 1) |
| Consentimientos por separado | El email lo tiene el 98 %, así que no diferencia. Se resume en el nº de canales |
| Modelo, nombre comercial, combustible, motor | Demasiados valores o repetidos: se resumen en gama, % electrificado y % furgoneta |
| Identificadores | No aportan información |

Que no entren en el modelo **no significa que se tiren**: en el Reto 4 se usan para **describir** cada segmento (por
ejemplo, "este segmento tiene un 70 % de suizos" o "conduce trayectos largos").

### 4 bis. Los datos externos de zona: se añaden, pero no segmentan

El primer paso del pipeline une a cada cliente, por **país + código postal**, cuatro datos oficiales de **la zona donde
vive** (construidos en el notebook Extra): accidentes por 1.000 habitantes, % de accidentes graves, mortalidad
estandarizada (solo Austria) y distancia al hospital. También su percentil dentro del país.

**¿Por qué no entran en el K-Means?**
1. **Describen a los vecinos, no al cliente.** Todos los clientes de un distrito austriaco (~80.000 habitantes) tienen
   el mismo valor. Segmentar con él sería suponer que cada persona es como la media de su zona (**falacia ecológica**).
2. **No existen igual en los dos países.** La mortalidad solo está en Austria: rellenarla en Suiza crearía una variable
   que en realidad separa países.
3. **Lo probamos.** En el Reto 4 repetimos el K-Means con ellos: salen los mismos segmentos y el silhouette empeora; si
   se les da más peso, los segmentos pasan a ser "urbano" y "rural".

Se usan para **entender** los datos (Reto 1) y **describir** los segmentos (Reto 4).

---

## 5. La preparación: el *pipeline*

### ¿Qué es un pipeline?

Un **pipeline** es una cadena de pasos que se ejecutan siempre en el mismo orden: los datos entran crudos por un lado y
salen listos para el modelo por el otro. Lo implementamos con `Pipeline` de scikit-learn en `features.py`.

**¿Por qué no hacerlo a mano, paso a paso?**

- **Reproducibilidad**: cualquier miembro del equipo obtiene exactamente el mismo resultado con dos líneas de código.
- **Sin errores de copia**: los Retos 3 y 4 importan el mismo pipeline, en vez de repetir el código.
- **Es lo que pide el reto.**

```python
from features import cargar_datos, construir_pipeline
X = construir_pipeline().fit_transform(cargar_datos())   # 173.456 clientes × 12 features
```

### Los tres pasos

```
datos crudos (302.850 filas)
   │
   ├─ 1. agregar      → 1 fila por cliente + features derivadas
   ├─ 2. recortar     → topes a los valores extremos
   └─ 3. preprocesar  → imputar nulos, codificar categorías, logaritmo y escalado
   │
matriz para K-Means (173.456 × 12, sin nulos)
```

#### Paso 1 · Agregar

Convierte las relaciones cliente–vehículo en una fila por cliente y calcula las features derivadas (apartado 3).

#### Paso 2 · Recortar extremos (*winsorización*)

Unos pocos clientes tienen valores extremos: un cliente con 561 coches, coches de casi 40 años… K-Means calcula
**medias** (los centros de los clusters), y las medias son muy sensibles a los extremos: un solo cliente con 561 coches
puede arrastrar a todo un segmento.

**Solución:** poner un **tope** y que los valores por encima pasen a valer el tope.

| Variable | Tope | Clientes afectados | Interpretación |
|---|---|---|---|
| `n_vehiculos_historico` | 10 | 1.706 | "10 o más" |
| `n_vehiculos_actuales` | 5 | 765 | "5 o más" |
| `antiguedad_vehiculo` | 20 años | 5 | "20 años o más" |
| `meses_cliente` | 120 | 0 | Límite de seguridad |

**¿Por qué no eliminarlos?** Porque son clientes reales e importantes (flotas). Con el tope siguen en el análisis,
identificados como "muchos vehículos", pero sin distorsionar a los demás.

#### Paso 3 · Preprocesar

Cada tipo de variable recibe un tratamiento distinto, dentro de un `ColumnTransformer` (una herramienta que aplica un
tratamiento diferente a cada grupo de columnas):

| Grupo | Variables | Tratamiento |
|---|---|---|
| Categorías ordenadas | `age_range`, `finance_leasing_status` | Imputar con la moda → codificación ordinal → escalado |
| Conteos con cola larga | `n_vehiculos_historico`, `n_vehiculos_actuales` | Imputar con la mediana → logaritmo → escalado |
| Numéricas | El resto | Imputar con la mediana → escalado |

**a) Imputación.** En esta fase quedan muy pocos nulos (por ejemplo, la antigüedad del coche de 1.348 clientes sin
ninguna fecha). Se rellenan con la **mediana**, por la asimetría explicada en el Reto 1. Aunque casi no haya nulos, el
paso está en el pipeline para que nunca falle con datos nuevos.

**b) Codificación de categorías.** K-Means solo entiende números, así que hay que convertir los textos. Hay dos formas
habituales:

- **One-hot**: una columna 0/1 por cada valor ("¿es 25-34?", "¿es 35-44?"…). Sirve para categorías **sin orden** (colores,
  países).
- **Ordinal**: un número por cada valor, respetando el orden (<25 = 0, 25-34 = 1, … 65+ = 5).

Elegimos **ordinal** porque nuestras dos categorías **sí tienen orden**:

- la edad: un cliente de 35-44 está "entre" uno de 25-34 y uno de 45-54;
- la financiación: nunca → antes → solo leasing → leasing y contado (de menor a mayor relación).

Con one-hot, el modelo creería que "25-34" está igual de lejos de "35-44" que de "65+", y perderíamos el orden.
Además, añadiría 10 columnas binarias que tienden a dominar K-Means.

**c) Logaritmo.** El número de vehículos es muy asimétrico: casi todos tienen 1, unos pocos tienen muchos. El
logaritmo (`log1p`, que es log(1 + x) para poder aplicarlo al 0) **comprime** los valores altos: pasar de 1 a 2 coches
pesa más que pasar de 9 a 10. Así es como lo vería un analista: tener un segundo coche es un cambio de perfil, tener el
décimo no tanto.

**d) Escalado estándar.** Es el paso más importante para K-Means. Cada variable se transforma para que tenga **media 0
y desviación 1**:

```
valor escalado = (valor − media) / desviación típica
```

**¿Por qué es imprescindible?** K-Means mide distancias. Sin escalar:

- la antigüedad como cliente va de 0 a 120 meses;
- el % electrificado va de 0 a 1.

Una diferencia de 10 meses (pequeña) pesaría 10 veces más que la diferencia entre "nada eléctrico" y "todo eléctrico"
(enorme). Tras escalar, todas las variables "hablan el mismo idioma": un valor de +2 significa "dos desviaciones por
encima de la media", sea cual sea la variable.

---

## 6. Comprobaciones finales

- **Sin nulos**: la matriz final tiene 173.456 clientes × 12 features y 0 nulos.
- **Sin sesgo de país**: comparamos la media de cada feature entre Austria y Suiza (en unidades escaladas). El poder
  adquisitivo y las visitas al taller dan una diferencia de **0,00**. Las únicas diferencias apreciables son las de
  mercado que decidimos mantener (leasing y electrificación).
- **Sin redundancias**: la correlación más alta entre dos features es **0,52** (meses como cliente y visitas al taller,
  lógico porque más años implican más visitas). Ninguna pareja dice lo mismo, así que cada feature aporta información
  distinta.

---

## 7. Glosario rápido

| Término | Significado |
|---|---|
| Feature | Cada variable que describe a un cliente para el modelo |
| Feature derivada | Variable creada por nosotros a partir de otras |
| Percentil | Posición de un valor dentro de su grupo, de 0 a 1 |
| Imputar | Rellenar un dato que falta |
| Codificación ordinal | Convertir categorías ordenadas en números que respetan el orden |
| One-hot | Convertir cada categoría en una columna 0/1 |
| Logaritmo (log1p) | Transformación que comprime los valores grandes |
| Winsorización | Poner topes a los valores extremos |
| Escalado estándar | Transformar cada variable a media 0 y desviación 1 |
| Pipeline | Cadena de pasos de preparación que se ejecuta siempre igual |
