# Fuentes de los datos externos

> Todos los datos que **no** vienen del CSV del reto (`datos_reto_mercedes_benz_malackathon.csv`) salen de las fuentes
> oficiales de esta página. Para cada una se indica quién la publica, qué dataset es exactamente, el enlace de descarga,
> el periodo, las condiciones de uso y dónde se usa en el proyecto.

---

## Resumen

| # | Dato | Organismo | País | Periodo | Fichero del repo que lo contiene |
|---|---|---|---|---|---|
| 1 | Accidentes con heridos y su gravedad por distrito | Statistik Austria | AT | 2025 | `datos_externos_por_cp.csv` |
| 2 | Mortalidad estandarizada por edad por distrito | Statistik Austria | AT | 2023-2025 | `datos_externos_por_cp.csv` |
| 3 | Lista de municipios con sus códigos postales | Statistik Austria | AT | vigente | (solo para unir) |
| 4 | Centro geográfico de cada municipio | Statistik Austria | AT | 2023 | (solo para distancias) |
| 5 | Directorio de hospitales | Ministerio de Sanidad de Austria | AT | 18-09-2026 | `datos_externos_por_cp.csv` |
| 6 | Accidentes con heridos geolocalizados | ASTRA (Oficina Federal de Carreteras) | CH | 2021-2025 | `datos_externos_por_cp.csv` |
| 7 | Directorio de localidades con código postal | swisstopo | CH | vigente | (solo para unir) |
| 8 | Indicadores y sedes de los hospitales | BAG (Oficina Federal de Salud Pública) | CH | 2023 | `datos_externos_por_cp.csv` |
| 9 | Limitación en las actividades por salud, por edad y sexo | Eurostat (EU-SILC) | AT y CH | 2023 | `datos_salud_edad_sexo.csv` |
| 10 | Problemas lumbares, cervicales y artrosis, por edad y sexo | Eurostat (EHIS) | AT | 2019 | `datos_salud_edad_sexo.csv` |

Los ficheros brutos (1-8) se descargan en la carpeta `datos_externos/`, que **no se sube a git**. Al repositorio solo se
suben las dos tablas ya resumidas (`datos_externos_por_cp.csv` y `datos_salud_edad_sexo.csv`), que es lo que usan los
notebooks.

---

## Seguridad vial y salud por zona (notebook `Extra_SaludSeguridadVial`)

### 1. Accidentes de tráfico en Austria

- **Organismo:** Statistik Austria (oficina estadística de Austria).
- **Publicación:** *Straßenverkehrsunfälle 2025*, informe anual. Se usan las tablas del anexo por distrito político:
  **tabla 90** (accidentes, fallecidos, heridos graves y leves) y **tabla 91** (accidentes por tipo de vía, para quitar
  autopistas y autovías).
- **Enlace:** <https://www.statistik.at/fileadmin/publications/Strassenverkehrsunfaelle2025.pdf>
- **Por qué del PDF:** Statistik Austria publica los puntos de accidente solo como mapa, sin descarga masiva; las cifras
  por distrito están en el anexo del informe. Comprobación: la suma de los 116 distritos da el total oficial de Austria
  (37.825 accidentes).
- **Condiciones de uso:** Statistik Austria, reutilización con cita de la fuente (CC BY 4.0).
- **Indicadores que produce:** accidentes por 1.000 habitantes (sin autopistas) y % de víctimas graves o mortales.

### 2. Mortalidad en Austria

- **Organismo:** Statistik Austria, portal de datos abiertos (OGD).
- **Dataset:** tasas semanales de mortalidad **estandarizadas por edad** por distrito político
  (`OGD_rate_kalwobez_GEST_KALWOCHE_STR_BZ_100`).
- **Enlace:** <https://data.statistik.gv.at/data/OGD_rate_kalwobez_GEST_KALWOCHE_STR_BZ_100.csv>
- **Periodo usado:** 2023-2025 (se excluyen 2020-2022 por la COVID).
- **Condiciones de uso:** CC BY 4.0, citando a Statistik Austria.

### 3. Municipios y códigos postales de Austria

- **Organismo:** Statistik Austria.
- **Dataset:** lista de municipios ordenada por código de municipio, con el código postal del ayuntamiento y los demás
  códigos postales del municipio (*Gemeindeliste nach Kennziffer*).
- **Enlace:** <https://www.statistik.at/verzeichnis/reglisten/gemliste_knz.csv>
- **Uso:** traducir el código postal del cliente a municipio y distrito.
- **Condiciones de uso:** CC BY 4.0, citando a Statistik Austria.

### 4. Centro geográfico de los municipios de Austria

- **Organismo:** Statistik Austria, servicio de geodatos abiertos.
- **Dataset:** puntos centrales de los municipios a 1-1-2023 (`STATISTIK_AUSTRIA_GEM_MP_20230101`).
- **Enlace:** <https://www.statistik.gv.at/gs-open/GEODATA/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=GEODATA:STATISTIK_AUSTRIA_GEM_MP_20230101&outputFormat=application/json>
- **Uso:** calcular la distancia en línea recta de cada municipio al hospital más cercano.
- **Condiciones de uso:** CC BY 4.0, citando a Statistik Austria.

### 5. Hospitales de Austria

- **Organismo:** Bundesministerium für Soziales, Gesundheit, Pflege und Konsumentenschutz (Ministerio de Sanidad).
- **Dataset:** *Krankenanstalten-Verzeichnis* (directorio de hospitales), versión del 18-09-2026. Se usan los hospitales
  del sector de agudos de tipo general (Eurostat HP 1.1).
- **Enlace:** <https://www.sozialministerium.gv.at/dam/jcr:0a2c1fb9-68c3-4355-bf22-ff0d11c0186e/KA-Verzeichnis%202026-09-18.xlsx>
- **Condiciones de uso:** el Ministerio lo ofrece como descarga pública "para su procesamiento posterior" y no indica
  una licencia concreta; advierte de que no garantiza que esté completo o actualizado. Se cita como fuente.

### 6. Accidentes de tráfico en Suiza

- **Organismo:** ASTRA – Bundesamt für Strassen (Oficina Federal de Carreteras), publicado en geo.admin.ch.
- **Dataset:** *Strassenverkehrsunfälle mit Personenschaden* (accidentes con heridos, geolocalizados), todos los años.
- **Enlace:** <https://data.geo.admin.ch/ch.astra.unfaelle-personenschaeden_alle/unfaelle-personenschaeden_alle/unfaelle-personenschaeden_alle_2056.csv.zip>
- **Periodo usado:** 2021-2025, sin autopistas ni autovías.
- **Condiciones de uso:** datos abiertos de la administración suiza; uso libre citando la fuente (opendata.swiss).

### 7. Localidades y códigos postales de Suiza

- **Organismo:** swisstopo – Oficina Federal de Topografía.
- **Dataset:** *Amtliches Ortschaftenverzeichnis mit Postleitzahl* (directorio oficial de localidades con código postal,
  municipio, % de direcciones y coordenadas).
- **Enlace:** <https://data.geo.admin.ch/ch.swisstopo-vd.ortschaftenverzeichnis_plz/ortschaftenverzeichnis_plz/ortschaftenverzeichnis_plz_4326.csv.zip>
- **Uso:** traducir el código postal a municipio y coordenadas.
- **Condiciones de uso:** geodatos abiertos de swisstopo; uso libre citando la fuente.

### 8. Hospitales de Suiza

- **Organismo:** BAG – Bundesamt für Gesundheit (Oficina Federal de Salud Pública).
- **Dataset:** *Kennzahlen der Schweizer Spitäler 2023* (indicadores de los hospitales suizos), hojas de hospitales y de
  sedes. Se usan los hospitales generales (tipología BFS K111-K123).
- **Enlace:** <https://opendata.bagnet.ch/?r=/download&path=L0taUC9renAyMy9renAyM19kYXRhLnhsc3g%3D>
  (ficha en opendata.swiss: <https://ckan.opendata.swiss/perma/kzp23@bundesamt-fur-gesundheit-bag>)
- **Condiciones de uso:** opendata.swiss, uso libre con obligación de citar la fuente.

---

## Salud y ergonomía por edad y sexo (Reto 1, apartado 6.3, y Reto 4, apartado 9)

Se descargan con la función `construir_tabla_salud` de `features.py`, a través de la API oficial de Eurostat, y se
guardan en `datos_salud_edad_sexo.csv`.

### 9. Limitación en las actividades por salud (Austria y Suiza)

- **Organismo:** Eurostat, a partir de la encuesta europea de ingresos y condiciones de vida (**EU-SILC**), en la que
  participan Austria y Suiza.
- **Dataset:** `hlth_silc_06` — *Self-perceived long-standing limitations in usual activities due to health problem by
  sex, age and labour status*.
- **Filtros:** año 2023 · población total · limitación "moderada o grave" (`SM_SEV`) y "grave" (`SEV`) · por sexo y por
  tramo de edad (16-24, 25-34, 35-44, 45-54, 55-64, 65+).
- **Enlace de la API:** <https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_06?format=JSON&lang=EN&geo=AT&geo=CH&unit=PC&wstatus=POP&lev_limit=SM_SEV&lev_limit=SEV&time=2023>
- **Ficha del dataset:** <https://ec.europa.eu/eurostat/databrowser/view/hlth_silc_06/default/table>
- **Condiciones de uso:** reutilización libre citando la fuente (política de reutilización de Eurostat, CC BY 4.0).

### 10. Problemas lumbares, cervicales y artrosis (Austria)

- **Organismo:** Eurostat, a partir de la Encuesta Europea de Salud por Entrevista (**EHIS**, 3.ª ola).
- **Dataset:** `hlth_ehis_cd1e` — *Self-reported chronic diseases by type of disease, sex, age and educational
  attainment level*.
- **Filtros:** año 2019 · Austria · todos los niveles educativos · enfermedades `LW_CHR_BACK` (lumbar), `NECK` (cervical)
  y `ARTHRO` (artrosis) · por sexo y por tramo de edad (15-24 … 65+).
- **Enlace de la API:** <https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_ehis_cd1e?format=JSON&lang=EN&geo=AT&unit=PC&isced11=TOTAL&time=2019&hlth_pb=LW_CHR_BACK&hlth_pb=NECK&hlth_pb=ARTHRO>
- **Ficha del dataset:** <https://ec.europa.eu/eurostat/databrowser/view/hlth_ehis_cd1e/default/table>
- **Por qué solo Austria:** Suiza no participa en la EHIS. Su encuesta propia (Schweizerische Gesundheitsbefragung 2022)
  no publica estos problemas por edad y sexo en una tabla descargable, así que no se inventan valores para Suiza.
- **Condiciones de uso:** reutilización libre citando la fuente (política de reutilización de Eurostat, CC BY 4.0).

**Cómo se usan:** a cada cliente se le asigna la prevalencia de su país, tramo de edad y sexo. Si el género es
desconocido, se usa el total de ambos sexos. El resultado es una **probabilidad esperada**, no un dato de salud del
cliente.

---

## Otros nombres que aparecen en los documentos

- **Equipamiento de los coches** (Active Brake Assist, PRE-SAFE®, 4MATIC, KEYLESS-GO, EASY-PACK, ENERGIZING, AIRMATIC,
  cámara de 360°, Active Parking Assist, Mercedes me connect…): son denominaciones comerciales de Mercedes-Benz. Su
  disponibilidad depende del modelo y del mercado.
- **Reglamento General de Seguridad de la UE** (julio de 2024), citado para los coches sin asistentes obligatorios:
  Reglamento (UE) 2019/2144.

---

## Cómo citar

En presentaciones e informes basta con indicar, junto a cada gráfico o cifra que use estos datos:

> Fuente: Statistik Austria; Bundesministerium für Soziales, Gesundheit, Pflege und Konsumentenschutz; ASTRA;
> swisstopo; BAG; Eurostat (EU-SILC 2023, EHIS 2019). Elaboración propia con datos de clientes de Mercedes-Benz.
