# Extra · Salud y seguridad vial por zona — Explicación

> Documento de apoyo al notebook [`Extra_SaludSeguridadVial.ipynb`](Extra_SaludSeguridadVial.ipynb). Explica qué datos
> externos se han usado, cómo se han unido a nuestro CSV, qué correlaciones aparecen y qué acciones proponemos para
> Mercedes-Benz.

---

## 0. La idea

Nuestro CSV dice mucho del cliente y su coche, pero nada del **entorno** en el que conduce. Hay datos públicos oficiales
sobre ese entorno (cuántos accidentes hay en su zona, lo graves que son, la salud de la población, lo lejos que queda el
hospital) que se pueden unir a nuestros clientes a través del **código postal**.

El objetivo es responder: **¿se relaciona el entorno de salud y seguridad vial con el tipo de cliente y de coche
Mercedes?** Y, si es así, **¿qué acciones de producto o servicio tiene sentido proponer?**

### Tres principios

1. **Describimos zonas, no personas.** Un indicador de zona no dice nada de la salud de un cliente concreto. Inferir la
   salud de una persona sería un dato de categoría especial protegido (art. 9 del RGPD en Austria; la ley de protección de
   datos suiza es similar).
2. **Se usa para priorizar, no para excluir.** El indicador decide dónde y qué comunicar, nunca a quién negar una oferta
   ni el precio.
3. **Cada país con su vara de medir.** Austria y Suiza miden distinto. Igual que hicimos con el poder adquisitivo (Reto 2),
   cada zona se compara **dentro de su país** (percentil).

---

## 1. Los datos externos

| Indicador | Austria 🇦🇹 | Suiza 🇨🇭 |
|---|---|---|
| **Accidentes con heridos** | Statistik Austria, informe anual 2025 (tablas por distrito en PDF) | ASTRA (oficina federal de carreteras), 267.761 accidentes geolocalizados 2011-2025 |
| **Gravedad** | Fallecidos y heridos graves por distrito | Accidentes con fallecidos o heridos graves |
| **Salud de la zona** | Mortalidad estandarizada por edad, por distrito (Statistik Austria) | No se publica por debajo del cantón |
| **Hospitales** | Listado oficial del Ministerio de Sanidad | Indicadores de hospitales 2023 (BAG, oficina federal de salud) |
| **Código postal → zona** | Lista oficial de municipios con sus códigos postales | Directorio oficial de localidades (swisstopo) |

Todas son **fuentes oficiales de libre uso**. Statistik Austria usa la licencia CC BY 4.0 (hay que citar la fuente); las
fuentes suizas siguen las condiciones de opendata.swiss. El notebook las descarga solo si no existen; los ficheros brutos
no se suben a git, pero sí la **tabla final por código postal** (`datos_externos_por_cp.csv`), para que el equipo pueda
usarla sin descargar nada.

---

## 2. Cómo se une cada fuente con nuestro CSV

Nuestro CSV tiene `country_code` y `zipcode`. El reto es llevar cada indicador hasta el código postal.

### Austria: código postal → municipio → distrito

La lista oficial de municipios trae el código postal del ayuntamiento y los demás códigos postales del municipio. Los 3
primeros dígitos del código de municipio son el **distrito** (*Bezirk*), que es el nivel de los accidentes y la
mortalidad.

**Detalles que hubo que resolver:**

| Problema | Solución |
|---|---|
| Un mismo código postal pertenece a varios municipios (304 casos que cruzan distritos) | Se asigna al municipio cuyo ayuntamiento usa ese código; si hay varios, primero la ciudad estatutaria. Sin esta regla, las ciudades de Steyr y Wels se quedaban sin población |
| **Viena** figura como un único municipio, pero los accidentes vienen por sus 23 distritos | El código postal vienés indica el distrito: 1**09**0 = distrito 9 |
| En la geometría de municipios, Viena aparece dividida en 23 códigos distintos | Al calcular distancias, cada código postal vienés se lleva a su distrito. Sin esto, el 29 % de los clientes austriacos se quedaba sin distancia al hospital |

### Suiza: código postal → municipio

El directorio de localidades da, para cada código postal, el municipio (número BFS), el porcentaje de direcciones y las
coordenadas. Cada accidente suizo trae el número de su municipio, así que el cruce es directo. Si un código postal abarca
varios municipios (1.222 casos), se asigna al que tiene **más direcciones**.

---

## 3. Cómo se construye cada indicador

### Accidentes por 1.000 habitantes

- **Austria:** Statistik Austria publica los puntos de accidente solo como mapa, sin descarga. Pero el anexo del informe
  anual tiene las tablas por distrito, y se extraen del PDF.
  - El PDF separa los miles con espacios ("1 196"), así que no es obvio dónde acaba un número y empieza el siguiente.
    Cada fila se reconstruye probando las particiones posibles y quedándose con la que **cumple las sumas** de la tabla
    (fallecidos + heridos = víctimas…).
  - **Comprobación:** la suma de los 116 distritos da exactamente **37.825**, el total oficial de Austria.
- **Suiza:** media anual de los accidentes de **2021-2025**. Se usan cinco años para que los municipios pequeños no
  dependan de un año con más o menos suerte.
- **Se excluyen autopistas y autovías.** Un accidente en la autopista se cuenta en el municipio que atraviesa, aunque los
  implicados vivan a 200 km. Si no se descontaran, los pueblos pequeños con autopista parecerían peligrosísimos.
- **Población:** se toma de **nuestro propio CSV**. Sumada, da 9,09 millones en Austria y 8,95 en Suiza, prácticamente la
  población oficial, así que es un denominador fiable.

### % de víctimas graves

Proporción de fallecidos y heridos graves sobre el total. Mide **lo graves** que son los accidentes, no cuántos hay. Los
accidentes en carretera son menos frecuentes que en ciudad, pero mucho más graves.

### Mortalidad estandarizada por edad (solo Austria)

- **Estandarizada por edad** significa que se corrige el hecho de que un distrito tenga más población mayor. Si no, los
  distritos envejecidos parecerían "menos sanos" solo por su edad.
- Se promedian los años **2023-2025**. Se excluyen 2020-2022 para que la COVID no distorsione la comparación, y 2026
  porque está incompleto.
- Detalle: las semanas sin fallecidos no aparecen en el fichero. Exigir 52 semanas eliminaba injustamente a los distritos
  pequeños; esas semanas cuentan como 0.

### Distancia al hospital de agudos

- **Solo hospitales generales de agudos** (los que atienden urgencias), no clínicas de rehabilitación ni psiquiátricas.
- Distancia **en línea recta** entre centros de zona. En un valle alpino el trayecto real es más largo, así que es una
  aproximación.

### Valores extremos que tienen explicación

| Caso | Explicación |
|---|---|
| Distrito 1 de Viena: 17 accidentes por 1.000 habitantes | Vive poca gente pero circula muchísima. La tasa por habitante sobreestima el riesgo de los centros urbanos |
| Lienz, Reutte (AT) y Zernez (CH): tasas altas | Zonas alpinas con mucho turismo y puertos de montaña |
| Rust (AT): mortalidad 15,5 ‰ | Solo ~2.000 habitantes: con tan poca población, unos pocos fallecimientos mueven mucho la tasa |
| Municipios suizos de menos de 1.000 habitantes | Se dejan sin tasa, porque sería ruido |

Por estos extremos usamos la **correlación de Spearman**, que trabaja con posiciones (rangos) y no se deja arrastrar por
valores raros.

---

## 4. Resultados

### Cobertura

El 88 % de los clientes austriacos y el 90-93 % de los suizos reciben los indicadores. Los que no, no tienen código postal
(Reto 1) o viven en municipios suizos muy pequeños.

### Correlaciones a nivel de zona

Para cada zona con **30 clientes o más** se calculan los porcentajes de nuestros clientes (4MATIC, SUV, coches antiguos,
65+, segmentos…) y se correlacionan con los indicadores externos.

> **¿Qué es la correlación de Spearman?** Mide si dos variables suben y bajan juntas, de −1 a +1. +0,5 es una relación
> moderada-fuerte; ±0,2-0,3, débil-moderada; cerca de 0, ninguna. Marcamos con * las que tienen p < 0,01, es decir, las
> muy difícilmente explicables por azar.

**Austria (115 distritos): relaciones moderadas y significativas**

| Indicador de zona | Relación con nuestros clientes |
|---|---|
| **Mortalidad estandarizada** | Coches **más antiguos** (+0,35), más coches **anteriores a julio de 2024** (+0,35) y más **Recién Llegado de Ocasión** (+0,46); menos 4MATIC (−0,31), SUV y Premium |
| **% de víctimas graves** | Más **Gran Formato** (+0,61), más clientes **65+** (+0,36) y más 4MATIC (+0,26); menos AMG y Recién Llegado (perfil **rural**) |
| **Distancia al hospital** | Más **Gran Formato** (+0,43) y **65+** (+0,29); menos Recién Llegado (−0,41) |
| **Accidentes por habitante** | Más 4MATIC, SUV, electrificados y Premium (ciudades y zonas alpinas turísticas) |

**Suiza (805 municipios): relaciones débiles** (|ρ| ≤ 0,21). Las zonas suizas se diferencian menos y las tasas por
municipio son más ruidosas. Lo único que se repite es que las zonas más alejadas del hospital tienen más Gran Formato.

### Cómo interpretarlo (y cómo no)

1. **Correlación no es causalidad.** Que en los distritos con más mortalidad haya coches más viejos no significa que una
   cosa cause la otra. Ambas dependen de un tercer factor: renta, ruralidad, edad de la población.
2. **Factor de confusión urbano/rural.** Gran parte de los patrones son el contraste ciudad frente a campo.
3. **Falacia ecológica.** Son relaciones entre zonas, no entre personas: no dicen que un cliente concreto esté en riesgo.

Aun así, el mensaje para Mercedes es claro y útil: **donde peor es el entorno de salud y seguridad vial, la flota de
clientes es más antigua, más rural y está menos equipada con los asistentes modernos.**

### Por segmento

Los indicadores de zona **apenas separan segmentos**, salvo **Gran Formato** (zonas más alejadas del hospital y con
accidentes más graves). Por eso no sustituyen a la segmentación: la **complementan**, señalando qué clientes priorizar
dentro de cada segmento.

---

## 5. Públicos y acciones para Mercedes-Benz

| Público | Clientes | Por qué | Acción Mercedes-Benz |
|---|---|---|---|
| **B** · Zona de siniestralidad grave + coche anterior a jul-2024 | ~14.600 (8,4 %) | Zonas rurales con accidentes graves y coches sin los asistentes obligatorios desde 2024 | **Campaña "Seguridad activa"**: renovación con Active Brake Assist, Active Lane Keeping Assist, ATTENTION ASSIST y PRE-SAFE®; si no renueva, **revisión de seguridad** en el taller oficial |
| **C/D** · 65+ con coche de 8+ años | ~4.900 (~470 en zonas de riesgo) | Más coches antiguos; el riesgo crece a partir de los 80 años (KFV) | Pruebas de modelos con **asistentes de aparcamiento y DISTRONIC**, **Mercedes-Benz Certified** (seminuevos con asistentes), cursos con ÖAMTC (AT) o TCS (CH) |
| **E/F** · Decil más alejado del hospital | ~6.000 (~1.100 con 65+) | Zonas rurales con más población mayor | **Mercedes me connect**: llamada de emergencia automática, asistencia en carretera, avisos de mantenimiento |
| **G** · Zona de muchos accidentes sin 4MATIC | ~12.800 (7,4 %) | Las zonas con más accidentes tienen más 4MATIC | Ofertas de **4MATIC** en la renovación y **paquete de invierno** en zonas alpinas |
| Distritos austriacos con más mortalidad | — | Flota más antigua y más Recién Llegado | **Renovación con financiación de entrada** y captación al taller oficial |

Los segmentos con más peso en estos públicos son **Fiel de Taller** y **Recién Llegado de Ocasión**: son los de coches más
antiguos (Reto 4).

### Cómo usarlo de forma responsable

- Mensajes **en positivo** ("más seguridad en tus trayectos"), **sin mencionar** la siniestralidad o la salud de su zona.
- El indicador decide **dónde y qué** comunicar; nunca **a quién excluir** ni el precio.
- Respetar los **canales consentidos**: al segmento "Contacto Solo Digital" solo por email.

---

## 6. Limitaciones

| Limitación | Efecto |
|---|---|
| Austria solo publica accidentes por distrito (no por municipio) | Menos detalle que en Suiza |
| La gravedad en Austria incluye autopistas (la tabla por tipo de vía no separa la gravedad) | Puede sobreestimar algo la gravedad en distritos con autopista |
| La distancia al hospital es en línea recta | Subestima el trayecto real en valles alpinos |
| La "fecha de julio de 2024" es un indicador aproximado | Muchos Mercedes ya llevaban esos asistentes de serie antes; habría que verificarlo modelo a modelo |
| Suiza no publica mortalidad por debajo del cantón | Solo hay indicador de salud de población para Austria |
| Una zona por código postal | Los códigos postales que abarcan varias zonas se asignan a la principal |

---

## 7. Glosario rápido

| Término | Significado |
|---|---|
| Distrito político (*Bezirk*) | Unidad administrativa austriaca entre el municipio y el estado federado |
| Número BFS | Código oficial de cada municipio suizo |
| Mortalidad estandarizada por edad | Tasa de mortalidad corregida para comparar zonas con distinta estructura de edad |
| Hospital de agudos | Hospital que atiende urgencias y enfermedades agudas |
| Correlación de Spearman | Mide si dos variables suben y bajan juntas, usando posiciones (robusta a extremos) |
| p-valor | Probabilidad de ver esa relación por puro azar; p < 0,01 = muy improbable |
| Factor de confusión | Una tercera variable que explica la relación entre otras dos |
| Falacia ecológica | Error de aplicar a una persona lo que se observa en su zona |
