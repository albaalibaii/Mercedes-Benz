# Reto 1 · Exploración y calidad de datos — Explicación

> Documento de apoyo al notebook [`Reto1_EDA.ipynb`](Reto1_EDA.ipynb). Explica **qué** se hace en cada paso, **por qué**
> se hace y **por qué elegimos** cada decisión frente a las alternativas. Está pensado para leerse sin experiencia previa
> en ciencia de datos.

---

## 0. ¿Qué es un EDA y para qué sirve?

**EDA** significa *Exploratory Data Analysis* (análisis exploratorio de datos). Es el primer paso de cualquier proyecto
de datos: antes de construir un modelo, hay que **conocer los datos**. Hay que saber qué contienen, cuánto falta, qué
está mal y cómo se distribuyen.

Es el paso más importante porque **un modelo solo es tan bueno como los datos que recibe**. Si metemos datos con
errores en K-Means, nos devolverá segmentos con errores, y no nos avisará: los números saldrán igual de "bonitos".
En inglés se resume como *garbage in, garbage out*.

En este reto respondemos cuatro preguntas:

1. ¿Qué es exactamente cada fila del fichero?
2. ¿Qué columnas no sirven para analizar y deben apartarse?
3. ¿Qué datos faltan, por qué faltan y qué hacemos con ellos?
4. ¿Qué datos son incorrectos o raros?

Y al final describimos cómo son los clientes.

---

## 1. Estructura y granularidad: ¿qué es una fila?

### Qué encontramos

| Concepto | Valor |
|---|---|
| Filas | 302.850 |
| Columnas | 39 |
| Clientes distintos | 173.456 |
| Vehículos distintos | 244.519 |

Hay **más filas que clientes**. Cada fila no es un cliente, sino una **relación cliente–vehículo**: "el cliente X tiene
o tuvo el vehículo Y". Un cliente con tres coches aparece en tres filas.

A esto se le llama **granularidad**: el nivel de detalle que representa cada fila.

### Por qué importa

El reto pide segmentar **clientes**. Si trabajásemos directamente con las filas:

- Un cliente con 10 coches contaría 10 veces y pesaría 10 veces más que uno con un coche.
- Un mismo cliente podría acabar en **varios segmentos a la vez** (uno por coche), lo que no tiene sentido para marketing.

**Decisión:** en el Reto 2 agregamos a **una fila por cliente**. Por ejemplo, en vez de "coche 1 eléctrico, coche 2 diésel"
guardamos "el 50 % de sus coches son eléctricos".

### Cómo describimos los datos en este reto

Usamos **dos niveles**:

- Para describir **clientes** (edad, consentimientos, código postal…), una fila por cliente. Si no, los clientes con
  muchos coches inflarían las estadísticas.
- Para describir **vehículos** (modelo, motor, antigüedad…), todas las filas.

### Comprobaciones que hicimos

- **No hay duplicados**: ningún par cliente–vehículo se repite.
- **Los datos de cliente son coherentes**: la edad, el género, el país, los consentimientos, etc. de un cliente son
  **siempre iguales** en todas sus filas (0 clientes con valores distintos). Esto es importante porque significa que
  agregar por cliente no genera conflictos del tipo "¿qué edad elegimos si en una fila pone 30 y en otra 40?".
- **Clientes "flota"**: 1.706 clientes (el 1 %) tienen más de 10 vehículos y acumulan el **20 % de todas las filas**. El
  máximo es un cliente con **561 vehículos**. Son casos extremos que habrá que controlar para que no distorsionen el modelo.
- **Vehículos compartidos**: 46.648 vehículos están vinculados a más de un cliente (hasta 36), por ejemplo propietario
  y conductor. Los datos técnicos del coche (modelo, motor, fecha) coinciden entre ellos, pero la **telemetría** (cómo se
  conduce) y las **visitas al taller** cambian. Conclusión: esos datos describen **la relación** (cómo conduce *ese*
  cliente *ese* coche), no el coche en sí.

### Los roles

Cada relación tiene un **rol**: OWNER (propietario), USER (usuario), DRIVER (conductor de empresa), LEGACY (relación
heredada de sistemas antiguos) y TEMP_USER (usuario temporal, por ejemplo una prueba o un alquiler). El 87 % son
propietarios. Esto será clave para entender por qué faltan algunos datos.

---

## 2. Columnas que se excluyen (metadatos e identificadores)

Un **identificador** es una columna que sirve para distinguir registros (como un DNI), pero no describe nada del
cliente. Un **metadato** es información sobre cómo se generó el dato, no sobre el cliente.

**¿Por qué no dejarlos "por si acaso"?** Porque K-Means trata todas las columnas como información. Si le damos un número
de identificación, intentará encontrar patrones en él y los segmentos dependerán de algo sin sentido.

| Columna | Por qué se excluye |
|---|---|
| `Unnamed: 0` | Es el número de fila que añadió el programa que exportó el fichero (comprobamos que va de 0 a 302.849, sin huecos) |
| `client_id`, `vehicle_id` | Códigos cifrados que identifican; solo se usan para agrupar y contar |
| `zipcode` | Hay 4.610 códigos postales distintos. Como número no significa nada (el CP 8000 no es "el doble" que el 4000). Lo que importa de la zona ya está en las columnas de poder adquisitivo |
| `model_series` | Código interno de la serie. `model_class` dice lo mismo de forma legible (C-Class, GLC…) |
| `vehicle_type` | 1.436 nombres comerciales distintos ("C 200 d", "GLE 450 4MATIC"…). Demasiados para el modelo; solo lo usamos para **deducir** datos que faltan |
| `trip_distance_mode`, `speed_mode`, `trip_distance_median`, `speed_median` | No son valores reales, sino tramos de un histograma (ver apartado 4) |
| `*_all_counter` | Cuentan cuántas mediciones hay; es un dato técnico, no del cliente |
| `fuel_type` | Dice lo mismo que `engine_concept`, pero con más huecos (59 % frente a 44 %) |

---

## 3. Valores nulos

Un **valor nulo** (NaN, *null*) es una celda vacía: el dato no está. Es el problema más habitual en datos reales.

### 3.1 ¿Cuánto falta?

Medimos el porcentaje de nulos **de dos formas**:

- **% de filas**: de cada 100 relaciones cliente–vehículo, ¿en cuántas falta el dato?
- **% de clientes**: de cada 100 clientes, ¿a cuántos les falta en **todos** sus vehículos?

| Bloque | % filas | % clientes |
|---|---|---|
| Telemetría (10 columnas) | 57-61 % | 46-50 % |
| `fuel_type` | 59 % | 50 % |
| `engine_concept` (motorización) | 44 % | 36 % |
| `gender_derived` (género) | 11 % | 17 % |
| Socioeconómicos (5 columnas) | 6,3 % | 8,9 % |
| `zipcode` | 5,3 % | 8,3 % |
| Fecha de matriculación | 1,4 % | 0,8 % |
| `model_class` | 1,1 % | 0,7 % |
| `months_as_mb_customer` | 4 filas | 2 clientes |

**¿Por qué cambian los porcentajes según el nivel?** Por ejemplo, el poder adquisitivo falta en el 6,3 % de las filas
pero en el 8,9 % de los clientes. Esto significa que los clientes sin ese dato tienen, de media, **menos vehículos**.
Si solo mirásemos las filas, **subestimaríamos** el problema. Por eso hay que medir siempre en el nivel en el que se va
a trabajar (clientes).

### 3.2 ¿Los nulos van juntos?

Hicimos dos gráficos:

- **Mapa de nulos**: cada columna es una línea y cada fila del fichero un punto (azul si falta). Permite ver si las
  celdas vacías se agrupan.
- **Correlación entre nulos**: si dos columnas suelen faltar a la vez, su correlación es cercana a 1.

Resultado: hay **tres bloques** que faltan juntos:

1. **Telemetría**: todas sus columnas faltan a la vez. Si un coche no envía datos, no envía ninguno.
2. **Socioeconómicos** y código postal: si no hay código postal, no hay datos de la zona.
3. **Motorización** (`engine_concept` y `fuel_type`).

Esto indica que cada bloque falta **por una misma causa**, y hay que averiguar cuál.

### 3.3 ¿Por qué falta? El mecanismo del nulo

Esta es la pregunta clave, porque **la causa decide el tratamiento**. En estadística se distinguen tres tipos:

| Tipo | Qué significa | Ejemplo | Qué se puede hacer |
|---|---|---|---|
| **Aleatorio** (MCAR) | Falta por azar, sin relación con nada | Un fallo puntual al guardar | Imputar o eliminar apenas sesga |
| **Depende de otra variable** (MAR) | Falta más en ciertos grupos | El género falta más en los jóvenes | **No eliminar** (perderíamos sobre todo ese grupo). Imputar **dentro del grupo** |
| **Estructural** (no aplica) | El dato **no existe** para ese caso | El consumo de gasolina de un coche eléctrico | **No inventar** un valor |

Para saber qué tipo es cada uno, calculamos el % de nulos en distintos **subgrupos** (país, rol, tipo de producto,
motor, año de matriculación). Si el porcentaje es similar en todos, es aleatorio. Si cambia mucho, depende de algo.

**Lo que encontramos:**

- **Telemetría → estructural.** Falta en:
  - el **100 % de los coches eléctricos** (el sistema no la recoge para ellos);
  - el **92-97 % de los roles que no son propietarios** (DRIVER, LEGACY, TEMP_USER), frente al 58 % de los propietarios;
  - casi todos los coches **anteriores a 2016** (no llevaban el hardware de conexión);
  - el 100 % de los smart.

  Es decir, no falta porque el cliente "no use el coche", sino porque **el dato no existe** para esos casos.
- **Motorización → depende del sistema de origen.** El % de nulos cambia con el año de forma irregular (84 % en 2012,
  24 % en 2017, ~50 % en 2019-2022) y es igual en los dos países. Depende de qué sistema registró el coche.
- **Socioeconómicos → depende del país y del rol.** Falta más en Austria (8 %) que en Suiza (5 %), y mucho más en
  usuarios no propietarios (24-31 % en USER y TEMP_USER frente al 4 % en OWNER): de ellos no consta dirección.
- **Género → depende de la edad, el país y el rol.** Falta en el **40 % de los menores de 25** y el **27 % de los mayores
  de 65**, frente al 9-11 % de los de 45-64 años.
- **Fecha de matriculación → depende del rol.** Falta en el 12 % de las relaciones LEGACY (coches antiguos de otros
  sistemas) y en el 5 % de los G-Class. En el resto, ~1 %.
- **Clase de modelo → modelos nuevos.** Falta en el 13 % de los eléctricos: son gamas recientes sin clase asignada.

### 3.4 ¿Media, mediana o eliminar? Cómo elegimos

Cuando falta un dato hay varias opciones:

| Opción | Qué es | Cuándo tiene sentido |
|---|---|---|
| **Eliminar** la fila o el cliente | Quitar el registro incompleto | Solo si los nulos son pocos **y** aleatorios |
| **Media** | Rellenar con el promedio | Datos simétricos (sin valores extremos) |
| **Mediana** | Rellenar con el valor central (la mitad está por encima y la mitad por debajo) | Datos **asimétricos** o con valores extremos |
| **Moda** | Rellenar con el valor más frecuente | Categorías (texto) |
| **Imputación por grupo** | Media/mediana calculada **dentro de un grupo** (por ejemplo, por país) | Cuando el valor típico cambia entre grupos |
| **Categoría "desconocido"** | Tratar el nulo como un valor más | Cuando el propio hueco aporta información |
| **No usar la variable** | Apartarla del modelo | Nulos estructurales o masivos |

#### Ejemplo 1: el poder adquisitivo

Este es el ejemplo que mejor muestra por qué no da igual elegir una opción u otra.

| | Media | Mediana | Mínimo | Máximo | Asimetría |
|---|---|---|---|---|---|
| Austria | 30.347 € | 30.178 € | 19.702 € | 48.330 € | 0,57 |
| Suiza | 55.363 € | 51.434 € | 26.660 € | 148.354 € | 2,54 |
| Global | 47.189 € | 46.753 € | — | — | 1,68 |

(Poder adquisitivo **por habitante**; en el apartado 6.2 se explica por qué no usamos el de por hogar.)

- **Media global (47.189 €)**: un cliente austriaco sin dato recibiría 47.189 €, casi el máximo de Austria y **por
  encima del 88 % de los austriacos**. Lo convertiríamos en "rico" sin ninguna razón. **Descartada.**
- **Mediana global (46.753 €)**: el mismo problema. **Descartada.**
- **Media por país**: en Suiza la distribución es muy **asimétrica** (asimetría 2,54). Unas pocas zonas muy ricas
  (hasta 148.354 €) tiran de la media hacia arriba: 55.363 € frente a una mediana de 51.434 €. La media no representa
  al cliente típico. **Descartada.**
- **Mediana de su país**: un austriaco sin dato recibe el valor típico austriaco, y un suizo el suizo. **Elegida.**

> **¿Qué es la asimetría?** Mide si los datos tienen una "cola" larga hacia un lado. 0 = simétrico (como una campana).
> Por encima de 1 = muy asimétrico, con algunos valores muy altos. Cuando hay asimetría, la **media engaña** y la
> **mediana** es más fiable.

#### Ejemplo 2: ¿y si eliminamos los clientes con nulos?

Simulamos eliminar a los clientes sin género o sin poder adquisitivo:

- Perderíamos **32.272 clientes (18,6 %)**, casi uno de cada cinco.
- Además, **cambiaría el perfil** de la base:

| Grupo | Todos | Tras eliminar | Diferencia |
|---|---|---|---|
| Menores de 25 | 4,7 % | 3,4 % | −1,4 puntos |
| 65 años o más | 20,2 % | 17,4 % | −2,8 puntos |
| Austriacos | 33,8 % | 31,8 % | −2,0 puntos |

Los segmentos describirían una población más joven-adulta y más suiza que la real. **Por eso no eliminamos filas en
ninguna columna.**

### 3.5 La decisión para cada columna

| Columna | Mecanismo | Decisión | Por qué | Consecuencia |
|---|---|---|---|---|
| Telemetría | Estructural | **No imputar ni usar en el modelo**. Solo para describir segmentos | Imputar sería inventar cómo conduce alguien. Usar "tiene telemetría" mezclaría *eléctrico*, *coche antiguo* y *no propietario* | Perdemos la conducción como rasgo, pero no metemos datos falsos ni penalizamos a los eléctricos |
| `fuel_type` | Sistema de origen | **Excluir** | `engine_concept` dice lo mismo con menos nulos | Ninguna |
| `engine_concept` | Sistema de origen | **Deducir por el nombre** del coche ("EQ…", "… e", "… de", "electric") | La moda (combustión) convertiría eléctricos en gasolina | Algún híbrido sin esas letras puede quedar como no electrificado |
| Género | Depende de edad y país | Categoría **"unknown"** y fuera del modelo | Eliminar sesga la edad. La moda convertiría a 1 de cada 6 clientes en "hombre" sin base | El género solo se usa para describir |
| Socioeconómicos | Depende de país y rol | **Mediana de su país** | Ver ejemplo 1 | Un 9 % de clientes queda en el valor central de su país |
| Fecha de matriculación | Depende del rol | **Mediana** (si el cliente tiene otro coche con fecha, se usa ese) | Afecta a muy pocos | 1.348 clientes (0,8 %): efecto despreciable |
| `model_class` | Modelos nuevos | **Deducir por el nombre** ("GLC 400" → GLC) | Recuperamos el dato real | Casi el 100 % recuperado |
| `months_as_mb_customer` | Residual | **Mediana** | Son 2 clientes | Irrelevante |

---

## 4. Inconsistencias y detalles del dato

Además de los huecos, revisamos datos que están **pero son raros o incorrectos**:

| Detalle | Casos | Qué significa y qué hacemos |
|---|---|---|
| Códigos postales con formato erróneo ("CH-6340", "A-2100", "Ottenbach") | 4 | Errores de introducción. Acaban sin datos de zona y se imputan con la mediana del país |
| Código postal sin datos socioeconómicos | 2.952 filas | El CP no aparece en la tabla de datos de zona. Mismo tratamiento |
| Clientes con 0 meses de antigüedad | 7.254 | Clientes nuevos. Es correcto |
| **Clientes con exactamente 36 meses** | **21.179 (12 %)** | Frente a ~2.700 con 35 o 37 meses. Es casi seguro un **artefacto**: una fecha de alta masiva o una migración de sistema. No se puede recuperar el valor real; se interpreta como "unos 3 años o más" |
| Clientes sin ningún vehículo conectado | 18.047 (10,4 %) | Clientes inactivos o ex-clientes. Es un dato real e interesante |
| Desajuste entre vehículos actuales y el campo declarado | 4 clientes | Irrelevante |
| 0 trayectos pero con "mediana de trayecto" | 6.027 filas | La mediana toma un valor por defecto. Otro motivo para no usarla |
| Modas con varios valores ("3,7.5") | 8.272 | Empates guardados como texto |

### Valores discretizados: las "medianas" que no lo son

`trip_distance_median` solo toma **13 valores posibles** (1; 2,5; 3; 7,5; 10; 15…). Una mediana real tomaría cualquier
valor. Lo que guarda el coche es un **histograma por tramos** ("entre 3 y 7,5 km"), y la "mediana" es el límite del tramo.
**No son datos reales**, así que se excluyen. Para describir la conducción usamos las **medias**.

### Topes del sistema

El consumo va de 3 a 50, la distancia media de 1 a 300 km y la velocidad de 0,12 a 220 km/h, con muchos casos justo en
los extremos. Son **límites del sistema**: un 50 significa "50 o más". Por eso, para describir, usamos la **mediana**, que
no se ve afectada por los extremos.

### Visitas al taller

- **Dependen de la edad del coche**: crecen hasta ~5 años y luego bajan, porque solo se registran las visitas **en
  garantía**. Un coche nuevo tiene pocas visitas porque no le ha dado tiempo, no porque su dueño lo cuide menos.
- **Se registran distinto en cada país**: con coches de antigüedad parecida, el **52 % de los austriacos tiene 0 visitas**
  frente al **23 % de los suizos**. Es una diferencia en **cómo se apuntan los datos**, no de comportamiento. En el
  Reto 2 se corrige comparando a cada cliente con los de su país.

---

## 5. Cómo son los clientes

| Rasgo | Resultado |
|---|---|
| País | Suiza 66 %, Austria 34 % |
| Edad | Perfil maduro: el 61 % tiene 45 años o más; menos del 5 % tiene menos de 25 |
| Género (inferido) | 65 % hombre, 18 % mujer, 17 % desconocido |
| Antigüedad como cliente | Mediana de 36 meses (con el pico artificial en 36) |
| Vehículos | Casi todos tienen uno conectado; el 27 % ha tenido más de un Mercedes |
| Tipo de cliente | Casi todo particular (B2C); el B2B es solo el 1,8 % de las relaciones |
| Financiación | El 29 % ha usado alguna vez leasing o financiación (31,6 % activo en Suiza, 15,6 % en Austria) |
| Gama | 84 % turismos; GLC, C, A y E-Class a la cabeza |
| Electrificación | 1 de cada 4 coches con motor conocido es híbrido enchufable o eléctrico (33,5 % en Austria, 20,2 % en Suiza) |
| Consentimientos | Email: 98 % (no diferencia a nadie). Teléfono y correo postal sí diferencian |

### Por qué separamos por país

Austria y Suiza son mercados distintos, y el país podía "colarse" en los segmentos:

- **Poder adquisitivo**: Suiza casi duplica a Austria. Si lo usásemos tal cual, los segmentos serían "suizos" y
  "austriacos". → En el modelo, siempre **relativo a su país**.
- **Visitas al taller**: diferencia de registro (ver arriba). → Relativo a su país.
- **Leasing** y **electrificación**: diferencias **reales** de mercado. → Se mantienen tal cual.

### Variables redundantes

Las cinco variables socioeconómicas forman dos parejas que dicen casi lo mismo: poder adquisitivo **por habitante** ≈
**por hogar**, y **población** ≈ **nº de hogares** ≈ **poder adquisitivo total**. Estas últimas miden el tamaño de la
zona, no la riqueza del cliente. Usar varias sería contar lo mismo dos veces, así que nos quedamos con **una**: el poder
adquisitivo **por habitante**. Parece igual que el de por hogar (correlación 0,96), pero el apartado 6.2 muestra que el
de por hogar está inflado en las zonas rurales.

> **¿Qué es la correlación?** Un número entre −1 y 1 que indica si dos variables se mueven juntas. Cerca de 1: cuando
> una sube, la otra también. Cerca de 0: no tienen relación. Usamos la de **Spearman**, que funciona bien aunque haya
> valores extremos.

---

## 6. Relaciones no evidentes

Lo descriptivo (apartado 5) confirma lo que cualquiera esperaría. Aquí buscamos relaciones **que no son obvias** y que
cambian cómo interpretamos los datos o qué se le ofrece al cliente.

> **Regla para no engañarnos:** cada hallazgo se enfrenta a su **explicación aburrida** (la edad del coche, el país,
> si la zona es rural, el poder adquisitivo). Si al tenerla en cuenta el efecto desaparece, no era un hallazgo.

### 6.1 Dentro del propio CSV

| Hallazgo | Cómo lo comprobamos | Qué significa para Mercedes-Benz |
|---|---|---|
| **El cliente de 65+ tiene el doble de coches de 10+ años (7,7 % frente a ~4 %), pero los usa mucho menos** | Horas de motor (telemetría) comparando **coches de la misma edad**: ~20 % menos | Su coche viejo tiene **pocos km**: buen valor de recompra ("tu coche vale más de lo que crees") y cambio a un coche **más seguro**, no más caro |
| **1 de cada 7 híbridos enchufables (PHEV) consume como un coche de combustión** | Consumo medio del PHEV frente a la mediana de los de combustión (8,8 L/100 km); mediana PHEV 5,8 L, lejos de los 1-2 L oficiales | Se cargan poco o nada: público para **wallbox y carga**, y el mejor candidato a pasar a **100 % eléctrico** |
| **En casas con varios coches, el electrificado es el más nuevo y de más gama** | Clientes con 2+ coches actuales: el eléctrico tiene ~1,5 años frente a ~3,5 del de combustión | El eléctrico **sustituye al coche principal**, no es el "segundo coche barato". El siguiente paso es electrificar el **otro** coche |
| **Quien no va al taller oficial se va más** | Con coches **de la misma edad** y por país: los clientes con 0 visitas están inactivos entre 1,2 y 4,5 veces más | El taller es una **alarma temprana de abandono**. No prueba causa, pero sirve para priorizar |
| **Los consentimientos NO predicen el abandono** | ~10 % de inactivos tenga 1, 2 o 3 canales | Que no quiera llamadas no significa que se vaya |
| **Los AMG no se conducen más rápido** | Misma velocidad media y trayectos que el resto | El AMG se vende como **imagen y experiencia**, no como prestaciones |
| **El género "desconocido" es un perfil incompleto** | Clientes con la mitad de antigüedad (17 meses frente a 36) y más inactivos | El dato que falta indica una relación **reciente o débil** |
| **La riqueza de la zona apenas cambia la gama** | Del 20 % más pobre al 20 % más rico, la gama y el % con AMG casi no cambian; sí sube la electrificación | Mercedes no se reparte por renta de la zona |
| **Con leasing se va más al taller** | Comparando coches de la misma edad | El contrato incluye mantenimiento: el cliente **al contado** es el que hay que atraer al taller |

**Un detalle técnico que podía engañar:** las horas de motor son un **contador acumulado**: cuanto más viejo el coche,
más horas. Por eso solo se comparan coches de la misma antigüedad.

### 6.2 Con datos oficiales de salud y seguridad vial

En el notebook **Extra_SaludSeguridadVial** descargamos datos oficiales de Austria y Suiza (accidentes, % de accidentes
graves, mortalidad y distancia al hospital) y los resumimos por código postal. Cada cliente recibe los datos **de la
zona donde vive**.

**Fuentes:** Statistik Austria, Ministerio de Sanidad de Austria, ASTRA, swisstopo y BAG. El organismo, el dataset, el
periodo, el enlace y las condiciones de uso de cada una están en
[`Fuentes_Datos_Externos.md`](Fuentes_Datos_Externos.md).

**Calidad de la unión.** Los clientes sin dato de zona son sobre todo los que no tienen código postal. Además, ~900
clientes tienen un código postal con formato correcto **que no existe** (`0000`, `9999`, `1234`, `1000` genérico):
se quedan sin dato, en lugar de asignarles uno equivocado.

#### Un problema que solo se ve al cruzar: el poder adquisitivo "por hogar"

Al cruzar con la distancia al hospital (que indica si la zona es **rural**), en Austria las zonas rurales salían más
"ricas". La explicación:

| | Relación con la distancia al hospital | Relación con las personas por hogar |
|---|---|---|
| Poder adquisitivo **por hogar** | +0,47 | +0,67 |
| Poder adquisitivo **por habitante** | −0,03 | −0,11 |

En el campo los **hogares son más grandes** (más personas aportando renta), así que el valor por hogar sube aunque cada
persona no sea más rica. La variable por hogar mide en buena parte **el tamaño del hogar**. **Decisión: el modelo usa
el poder adquisitivo por habitante.** Ambas tienen los mismos nulos y una correlación de 0,96 entre sí, por eso
parecían intercambiables: el sesgo solo aparece al mirarlas junto a una **tercera** variable.

#### Relaciones entre la zona y los clientes

Agrupamos a los clientes por **distrito** (Austria) o **municipio** (Suiza) y calculamos la correlación.

> **¿Qué es la correlación parcial?** La correlación que queda después de **descontar** otras variables. Si en las
> zonas con más accidentes hay coches más nuevos, ¿es por los accidentes o porque esas zonas son rurales? La parcial
> quita el efecto de lo rural y del poder adquisitivo, y mira lo que queda.

> **Cuidado con el azar:** probamos unas 200 combinaciones. Con tantas pruebas, alguna puede salir "significativa" por
> casualidad. Solo comentamos las **moderadas** (|ρ| ≥ 0,2), que **sobreviven al control** y que **tienen sentido**.

| Hallazgo (Austria, 115 distritos) | Qué significa |
|---|---|
| **La telemetría confirma los accidentes:** donde hay más accidentes graves, nuestros clientes conducen más rápido (de ~43 a ~55 km/h de media) | Es la mecánica conocida (carreteras secundarias rápidas: menos accidentes, pero más graves). Que un dato **nuestro** cuadre con uno **oficial** demuestra que la unión por código postal funciona |
| **¿Coches viejos donde hay más accidentes? Al revés:** coches **más nuevos**, más leasing y más vehículos que el cliente ya no tiene | Son zonas rurales y de paso donde el coche se usa mucho y se renueva antes. Más accidentes ↔ más coches que salen de la relación: idea de un **programa "después del siniestro"** |
| **Donde la gente muere antes, el coche se cuida menos:** coches más viejos y más clientes que nunca van al taller oficial, también con coches de la misma edad (unos 4-5 puntos más) | Hipótesis: la misma **cultura de prevención** que cuida la salud cuida el coche. El mensaje de taller funciona mejor como **seguridad** |
| **Lejos del hospital:** menos clientes inactivos, más furgonetas, gama más baja, trayectos más largos | El cliente rural depende del coche y es **más fiel**, pero compra **utilidad**, no prestigio |

**Suiza:** solo pasan el filtro relaciones débiles (|ρ| ≤ 0,23), en la misma dirección que Austria. La unidad es el
municipio (muy pequeño y ruidoso) y no hay mortalidad por zona. **No forzamos conclusiones donde no las hay.**

> **Ojo:** son relaciones **entre zonas**, no entre personas. Que en un distrito haya más mortalidad y menos visitas al
> taller no significa que cada cliente de ese distrito sea así (a esto se le llama **falacia ecológica**).

Los indicadores de zona **no entran en el modelo** (se explica en el Reto 2), pero se usan para entender los datos y
para **perfilar** los segmentos en el Reto 4.

### 6.3 Salud y ergonomía

Nuestro CSV **no tiene datos de salud** (y no debe tenerlos: en el RGPD son datos de categoría especial). Pero sí tiene
la **edad** y el **sexo** de cada cliente, y Eurostat publica cuánta gente tiene cada problema de salud **por país, edad
y sexo**. Uniendo las dos cosas, cada cliente recibe la **probabilidad esperada** de tener ese problema.

| Indicador | Fuente | Países | Por qué importa en un coche |
|---|---|---|---|
| Limitación (moderada o grave) por salud | Eurostat, EU-SILC 2023 | Austria y Suiza | Entrar, salir, cargar, girarse |
| Limitación grave | ídem | Austria y Suiza | Necesidad de adaptaciones |
| Problema lumbar crónico | Eurostat, Encuesta Europea de Salud (EHIS) 2019 | Austria | Horas sentado, vibraciones |
| Problema cervical crónico | ídem | Austria | Girar la cabeza para maniobrar |
| Artrosis | ídem | Austria | Rodillas, caderas y manos |

Suiza no participa en la EHIS, así que los tres últimos solo se calculan para Austria: **no inventamos** valores para
Suiza. Todas las fuentes, con sus enlaces, están en [`Fuentes_Datos_Externos.md`](Fuentes_Datos_Externos.md).

> **¿Qué es una probabilidad esperada?** Si el 41 % de las mujeres austriacas de 65+ declara un problema lumbar, a una
> clienta austriaca de 65+ le asignamos 0,41. **No sabemos** si ella lo tiene. Pero si sumamos esas probabilidades en un
> grupo, obtenemos **cuántos** clientes de ese grupo lo tienen probablemente. Sirve para decidir qué ofrecer, nunca para
> etiquetar a una persona.

**Cuántos:** se esperan unos **55.000 clientes con alguna limitación por salud** (casi 1 de cada 3) y, solo en Austria,
unos 16.000 con problema lumbar, 11.000 cervical y 8.000 con artrosis.

#### La brecha ergonómica

Un coche de **posición alta** (SUV, monovolumen, furgoneta) se entra y se sale sin agacharse. Si la necesidad mandase,
los clientes mayores tendrían cada vez más coches altos. Pero:

| Edad | Limitación por salud esperada | Coches de posición alta |
|---|---|---|
| 35-44 | ~22 % | ~58 % |
| 45-54 | ~29 % | ~62 % |
| 55-64 | ~40 % | ~64 % |
| 65+ | **~48 %** | **~63 %** |

La necesidad **se duplica**, pero la proporción de coches altos **se estanca**. Hay ~12.400 clientes de 65+ sin ningún
coche alto, y unos 5.900 de ellos probablemente tienen una limitación. Es un público para un **SUV compacto o
monovolumen** (GLA, GLB, Clase B, EQA/EQB) con un argumento de **comodidad**, no de edad.

#### Tiempo al volante

Con la telemetría se estima la duración media de un trayecto (distancia media ÷ velocidad media). Estar mucho tiempo
sentado y con vibraciones es un factor de riesgo de dolor lumbar conocido en salud laboral.

- El trayecto típico dura **~18 minutos**.
- Los **conductores de furgoneta** hacen los trayectos más largos: para ellos el asiento es una herramienta de trabajo.
- Los de 65+ hacen los más **cortos**: su ergonomía es la de entrar, salir y maniobrar.

**Detalle de calidad:** ~1.800 relaciones tienen una velocidad media de menos de 5 km/h, que daría trayectos de días. Se
descartan, igual que las duraciones medias de más de 4 horas.

#### De cada problema de salud a un equipamiento Mercedes-Benz

| Problema | Qué le cuesta al conductor | Equipamiento que lo alivia |
|---|---|---|
| Limitación general | Entrar, salir, cargar | Posición alta (GLA, GLB, Clase B, EQA/EQB), KEYLESS-GO, portón eléctrico EASY-PACK, Clase V con puertas correderas |
| Lumbar | Trayectos largos, vibraciones | Asientos multicontorno con masaje, apoyo lumbar, ENERGIZING, suspensión AIRMATIC |
| Cervical | Girar la cabeza al maniobrar | Cámara de 360°, asistente de ángulo muerto, Active Parking Assist, Head-up Display |
| Artrosis | Agacharse, fuerza en las manos, frío | Posición alta, KEYLESS-GO, cierre de confort de puertas, volante y asientos calefactables |
| Limitación grave | Conducir un coche de serie | Adaptaciones con transformadores homologados; Clase V adaptada |

**Uso responsable:** el mensaje es siempre de **comodidad** ("entra y sal sin esfuerzo", "llega descansado"), nunca de
salud ni de edad.

---

## 7. Resumen de decisiones

| Problema | Decisión |
|---|---|
| Cada fila es cliente–vehículo | Agregar a una fila por cliente (Reto 2) |
| Telemetría ausente por motivos estructurales | No imputar ni modelar; solo describir |
| Motorización y clase de modelo nulas | Deducir por el nombre comercial |
| Género nulo concentrado en jóvenes y mayores | Categoría "unknown"; fuera del modelo |
| Socioeconómicos nulos y distintos por país | Mediana de su país; variable relativa al país |
| Eliminar filas con nulos | Descartado: −18,6 % de clientes y perfil sesgado |
| Medianas/modas que son tramos; topes del sistema | Excluir medianas/modas; describir con medianas |
| Visitas al taller distintas por país | Relativas al país (Reto 2) |
| Identificadores y variables redundantes | Excluidos |
| Poder adquisitivo por hogar inflado en zonas rurales | Usar el **por habitante** |
| Códigos postales que no existen (`0000`, `9999`…) | Sin dato de zona; no se inventa |
| Relaciones no evidentes | Se comprueban siempre frente a su explicación aburrida (edad del coche, país, ruralidad, riqueza) |
| Salud sin datos de salud | Probabilidad esperada por país, edad y sexo (Eurostat); nunca un dato de la persona |
| Problemas lumbares, cervicales y artrosis solo en Austria | Suiza no participa en la EHIS: no se inventan valores |
| Trayectos con velocidad media < 5 km/h | Descartados (darían duraciones de días) |
