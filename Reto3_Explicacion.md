# Reto 3 · Modelo de clustering K-Means — Explicación

> Documento de apoyo al notebook [`Reto3_KMeans.ipynb`](Reto3_KMeans.ipynb). Explica qué es cada cosa, por qué se hace
> así y por qué elegimos cada decisión.

---

## 0. ¿Qué es el clustering y qué es K-Means?

**Clustering** (agrupamiento) es una técnica de **aprendizaje no supervisado**: le damos al algoritmo los datos **sin
decirle la respuesta**, y él busca grupos de elementos parecidos entre sí y distintos de los demás. En nuestro caso,
grupos de clientes con perfiles similares, que llamamos **clusters** o **segmentos**.

"No supervisado" significa que no hay una respuesta correcta con la que comparar: nadie nos ha dicho de antemano a qué
segmento pertenece cada cliente. Por eso hay que **evaluar con cuidado** si los grupos tienen sentido.

### Cómo funciona K-Means

Cada cliente es un punto en un espacio de 12 dimensiones (una por feature). K-Means hace esto:

1. Elegimos **k**, el número de grupos que queremos.
2. El algoritmo coloca **k centros** (centroides) al azar.
3. Asigna cada cliente al **centro más cercano**.
4. Mueve cada centro al **punto medio** de sus clientes.
5. Repite los pasos 3 y 4 hasta que los centros dejan de moverse.

El **centroide** de un cluster es su "cliente medio": nos dice qué caracteriza a ese grupo.

K-Means tiene dos debilidades que condicionan todo el reto:

- **Hay que decirle k.** No sabe cuántos grupos hay; lo tenemos que decidir nosotros (apartados 2 a 4).
- **Empieza al azar.** Según dónde coloque los centros al principio, puede acabar en soluciones distintas (apartado 5).

---

## 1. Riesgos que vigilamos y cómo los evitamos

| Riesgo | Qué pasaría | Qué hicimos |
|---|---|---|
| El Silhouette sobre 173.456 clientes | El cálculo compara cada cliente con todos los demás: unos 15.000 millones de pares de clientes, inviable | Calcularlo sobre **muestras de 20.000 clientes** al azar, repetido 3 veces |
| La inicialización aleatoria | Resultados distintos en cada ejecución | 50 inicializaciones en el modelo final y semilla fija |
| Clusters que separan países | Segmentos que solo dicen "suizo / austriaco" | País fuera del modelo y variables relativas al país (Reto 2), y comprobación de la mezcla de países |
| Clusters diminutos | Segmentos sin tamaño suficiente para una campaña | Vigilar el tamaño del cluster más pequeño |
| Variables con nulos estructurales | Segmentos del tipo "eléctrico / coche antiguo / no propietario" | La telemetría se retiró del modelo |

---

## 2. Probar varios valores de k

Entrenamos K-Means para **k = 2, 3, … 10** y medimos dos cosas en cada caso: la **inercia** y el **Silhouette**.

| k | Inercia | Caída de inercia | Silhouette | Cluster más pequeño | % de suizos (mín.–máx. por cluster) |
|---|---|---|---|---|---|
| 2 | 1.853.753 | — | 0,126 | 35,0 % | 62–73 % |
| 3 | 1.701.161 | 8,2 % | 0,140 | 9,4 % | 60–70 % |
| 4 | 1.537.389 | 9,6 % | **0,170** | 8,9 % | 55–70 % |
| 5 | 1.424.416 | 7,3 % | 0,132 | 8,8 % | 55–74 % |
| **6** | **1.340.947** | **5,9 %** | **0,135** | **8,7 %** | **55–74 %** |
| 7 | 1.267.050 | 5,5 % | 0,137 | 7,8 % | 55–**86 %** |
| 8 | 1.210.751 | 4,4 % | 0,138 | 7,2 % | 55–**86 %** |
| 9 | 1.179.561 | 2,6 % | 0,122 | 6,5 % | 55–**85 %** |
| 10 | 1.141.229 | 3,3 % | 0,122 | 3,5 % | 55–**86 %** |

### ¿Qué es la inercia? El método del codo

La **inercia** es la suma de las distancias (al cuadrado) de cada cliente a su centroide. Mide lo **apretados** que están
los grupos: cuanto menor, más parecidos son los clientes dentro de cada grupo.

El problema es que la inercia **siempre baja** al añadir clusters. Con un cluster por cliente sería 0, pero eso no sirve
de nada. Por eso no buscamos el mínimo, sino el **codo**: el punto a partir del cual añadir un cluster más **apenas mejora**.
En el gráfico es donde la curva pasa de bajar rápido a bajar despacio, como el codo de un brazo.

**Nuestro caso:** no hay un codo muy nítido (es habitual con datos reales). La mayor mejora llega al pasar a k = 4
(−9,6 %). Después las mejoras se van reduciendo (7,3 % → 5,9 % → 5,5 % → 4,4 %), y a partir de k = 9 son marginales.
El codo está en la zona **k = 4-6**.

### ¿Qué es el Silhouette?

El **Silhouette** mide, para cada cliente, si está **bien asignado**:

- compara la distancia media a los clientes de **su** cluster (*a*)
- con la distancia media a los del **cluster vecino más cercano** (*b*).

```
silhouette = (b − a) / máx(a, b)
```

Va de −1 a 1:

| Valor | Significado |
|---|---|
| Cerca de 1 | El cliente está muy dentro de su grupo y lejos de los demás |
| Cerca de 0 | Está en la frontera entre dos grupos |
| Negativo | Estaría mejor en otro grupo |

El Silhouette del modelo es la **media de todos los clientes**. A diferencia de la inercia, no mejora siempre al añadir
clusters, así que sí tiene sentido buscar el máximo.

**Por qué usamos muestras:** calcular el Silhouette exige comparar cada cliente con todos los demás. Con 173.456
clientes son unos 15.000 millones de pares de distancias, demasiado para un ordenador normal. Con una muestra aleatoria de 20.000
clientes el resultado es representativo. Lo repetimos con **3 muestras distintas**: la diferencia entre ellas es de
≤ 0,001, así que el muestreo no altera la conclusión.

**Nuestro caso:** el máximo está en **k = 4 (0,170)**; entre k = 5 y 8 hay una meseta (0,132-0,138) y a partir de 9 cae.

### ¿Un Silhouette de 0,13-0,17 es malo?

Es **bajo, y es lo esperable** con datos de clientes. Los clientes no forman grupos separados como islas, sino un
**continuo**: hay clientes de todas las edades, con coches de todas las antigüedades… K-Means "corta" ese continuo en zonas
homogéneas, y muchos clientes quedan cerca de las fronteras.

Valores por encima de 0,5 aparecen en datos con grupos muy definidos (por ejemplo, especies de plantas distintas), no en
bases de clientes. Lo importante aquí es que los segmentos sean **distintos entre sí, estables y útiles**, y eso es lo que
comprobamos en los apartados siguientes.

---

## 3. ¿Algún cluster es "un país"?

El 66 % de los clientes son suizos. Si la segmentación estuviera sesgada por país, algún cluster tendría casi todo suizos
o casi todo austriacos.

- **Hasta k = 6**, todos los clusters tienen entre un 55 % y un 74 % de suizos, cerca del 66 % global: **ningún segmento
  es un país**.
- **Desde k = 7** aparece un cluster de **leasing activo** con un 86 % de suizos. No es un error, porque el leasing está
  mucho más extendido en Suiza (29 % frente a 13 %) y decidimos mantenerlo como comportamiento real. Pero es un motivo más
  para no pasar de 6.

### Dos problemas que detectamos y corregimos por el camino

1. **Visitas al taller.** En la primera versión se usaban en valor absoluto y salía un cluster con un 81-86 % de suizos.
   La causa era que cada país **registra** las visitas de forma distinta (52 % de austriacos con 0 visitas frente a 23 %
   de suizos, con coches de antigüedad parecida). Se corrigió en el Reto 2 midiéndolas dentro de cada país.
2. **Telemetría.** La primera versión incluía "tiene telemetría". La auditoría del Reto 1 demostró que su ausencia es
   estructural (eléctricos, no propietarios, coches antiguos), y la retiramos. Los 6 segmentos finales son prácticamente
   los mismos con y sin ella, lo que demuestra que la segmentación **no dependía** de esa variable sesgada.

---

## 4. La elección de k: por qué 6 y no 4

Las métricas señalan **k = 4**: mejor Silhouette (0,170) y mayor caída de inercia. Pero antes de aceptarlo miramos **qué
segmentos produce**:

- **k = 4** separa tres grupos muy marcados (multi-vehículo 18 %, electrificados 16 % y furgonetas 9 %) y mete al **57 %
  de los clientes en un único cluster genérico**. El Silhouette es alto precisamente porque esos tres grupos pequeños
  están muy separados del resto, pero más de la mitad de la base queda sin segmentar. Para marketing, eso es "todos los
  demás".
- **k = 6** divide ese bloque en tres grupos con estrategia propia:
  - **recientes y con poco taller** → fidelización;
  - **fieles al taller** → planes de mantenimiento;
  - **pocos consentimientos** → recuperar permisos de contacto antes de cualquier campaña.

| Criterio | k = 4 | k = 6 |
|---|---|---|
| Silhouette | **0,170** | 0,135 (dentro de la meseta 5-8) |
| Codo | Mayor caída | Las caídas aún son apreciables (5,9 %) |
| Mezcla de países | Correcta | Correcta |
| Cluster más grande | 57 % | 27 % |
| Utilidad | 3 segmentos claros + 1 bloque genérico | 6 segmentos accionables |

**Decisión: k = 6.** Las métricas no son una regla automática, sino una guía. Sacrificamos algo de Silhouette (seguimos
en la zona buena) a cambio de que **toda** la base quede repartida en grupos útiles. Con k = 7 o más el Silhouette no
mejora, aparece un cluster dominado por un país y hay demasiados segmentos para gestionarlos.

> Esta es la diferencia entre "elegir el número que da la métrica" y **pensar como analista de negocio**, que es lo que
> pide el reto.

---

## 5. Estabilidad: ¿salen siempre los mismos segmentos?

### El problema de la inicialización

K-Means empieza colocando los centros al azar. Según dónde empiecen, puede acabar en un **óptimo local**: una solución
que parece estable pero no es la mejor posible. Es como buscar el punto más bajo de un terreno con los ojos cerrados:
según dónde empieces, puedes acabar en un hoyo pequeño en vez de en el valle más profundo.

Para medirlo, entrenamos el modelo con **5 semillas distintas** (la semilla fija el azar) y comparamos los resultados.

### ¿Qué es el ARI?

El **Adjusted Rand Index (ARI)** mide cuánto se parecen dos agrupaciones de los mismos clientes, sin importar el número
que se le ponga a cada cluster (el "cluster 2" de una ejecución puede ser el "cluster 5" de otra):

| ARI | Significado |
|---|---|
| 1 | Asignaciones idénticas |
| 0 | Parecido al de dos repartos al azar |

### Lo que encontramos

**Con 10 inicializaciones** (`n_init=10`, el valor habitual), el ARI medio fue **0,764**. Aparecían **dos soluciones
distintas** según la semilla:

| Semilla | Inercia | Solución |
|---|---|---|
| 42, 1, 2 | ≈ 1.340.943 | A (con segmento "pocos consentimientos") |
| 0, 3 | ≈ 1.343.087 | B (cambia ese segmento por uno de "leasing") |

La solución **A es mejor** (menor inercia), pero con 10 intentos el algoritmo a veces se quedaba en la B.

**Por qué es grave:** otro miembro del equipo, ejecutando el mismo código con otra semilla, podría obtener **segmentos
diferentes** y conclusiones distintas.

**Solución:** subir a **50 inicializaciones** (`n_init=50`). El algoritmo prueba 50 puntos de partida y se queda con el
de menor inercia. Con 50, las 5 semillas llegan a la misma solución A: **ARI medio de 0,995**.

El modelo final se entrena así en `features.py` (`ajustar_kmeans`), de modo que el Reto 4 y cualquiera del equipo
obtienen **exactamente** los mismos segmentos.

---

## 6. El modelo final (k = 6)

| Cluster | Clientes | % | Qué lo distingue (provisional) | Silhouette | % clientes en la frontera |
|---|---|---|---|---|---|
| 0 | 18.824 | 10,9 % | Pocos consentimientos de contacto | 0,085 | 10 % |
| 1 | 45.492 | 26,2 % | Fieles al taller y con años de relación | 0,162 | 0 % |
| 2 | 46.950 | 27,1 % | Recientes, pocas visitas al taller, coche más antiguo | 0,123 | 6 % |
| 3 | 24.778 | 14,3 % | Electrificados | 0,171 | 1 % |
| 4 | 15.173 | 8,7 % | Furgonetas | 0,229 | 1 % |
| 5 | 22.239 | 12,8 % | Multi-vehículo, leasing, gama alta, coches nuevos | 0,048 | **40 %** |

("% en la frontera" = clientes con Silhouette negativo, que encajarían casi igual en otro cluster.)

### Cómo leer la tabla

- Todos los clusters tienen **masa crítica**: el más pequeño tiene más de 15.000 clientes.
- Los grupos definidos por un rasgo muy claro (**furgonetas**, **electrificados**, **fieles al taller**) son los más
  compactos.
- El grupo **multi-vehículo / leasing / gama alta** es el más **difuso**: el 40 % de sus clientes está en la frontera.
  Agrupa clientes de alto valor pero variados, desde familias con dos coches hasta pequeñas flotas. En el Reto 4 lo
  describiremos con cuidado, y se recomienda **subdividirlo** si se quiere afinar una campaña sobre él.

### El mapa de centroides

En el notebook hay un mapa de calor con el centroide de cada cluster. Los valores están **escalados** (Reto 2):

- **0** = igual que el cliente medio;
- **+1** = una desviación por encima de la media (rojo);
- **−1** = una desviación por debajo (azul).

Por ejemplo, el cluster de furgonetas tiene +3,0 en `pct_furgoneta`: tres desviaciones por encima de la media, es decir,
casi todos sus coches son furgonetas.

Los nombres de negocio de cada segmento se ponen en el Reto 4.

---

## 7. Resumen de decisiones

| Decisión | Por qué |
|---|---|
| Probar k de 2 a 10 | Rango razonable para segmentos de marketing (menos de 2 no es segmentar; más de 10 no se puede gestionar) |
| Silhouette con muestras de 20.000 × 3 | El cálculo completo es inviable; la variación entre muestras es mínima |
| k = 6 en vez de k = 4 | k = 4 deja al 57 % en un bloque genérico; k = 6 está en la meseta de Silhouette y es accionable |
| No pasar de k = 6 | Desde 7 aparece un cluster dominado por un país y el Silhouette no mejora |
| `n_init=50` y semilla 42 | Con 10 inicializaciones había dos soluciones; con 50, siempre la mejor |

---

## 8. Glosario rápido

| Término | Significado |
|---|---|
| Clustering | Agrupar elementos parecidos sin conocer la respuesta de antemano |
| k | Número de clusters |
| Centroide | Punto medio de un cluster: su "cliente medio" |
| Inercia | Suma de distancias de cada cliente a su centroide; mide lo compactos que son los grupos |
| Método del codo | Elegir k donde la inercia deja de bajar rápido |
| Silhouette | Mide si cada cliente está bien asignado (de −1 a 1) |
| Óptimo local | Solución estable pero no la mejor posible |
| `n_init` | Número de veces que K-Means prueba un punto de partida distinto |
| Semilla (`random_state`) | Número que fija el azar para que los resultados sean reproducibles |
| ARI | Mide cuánto se parecen dos agrupaciones (1 = idénticas) |
