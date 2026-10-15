# Reto avanzado 3 · Estabilidad de los clusters (Jackknife) — Explicación

> Documento de apoyo al notebook [`Avanzado3_Jackknife.ipynb`](Avanzado3_Jackknife.ipynb). Explica qué es cada cosa, por
> qué se hace así y qué hemos decidido.

---

## 0. ¿Qué problema resuelve este reto?

En el Reto 3 obtuvimos 6 segmentos y en el Reto 4 les pusimos nombre y acciones. Pero falta una pregunta clave antes de
gastar dinero en campañas: **¿los segmentos son "de verdad" o dependen de qué clientes estén en el fichero?**

Imagina que mañana llegan datos nuevos, o que se pierde un 20 % de los clientes. Si al re-entrenar el modelo los
segmentos cambian por completo, las campañas diseñadas hoy no servirían mañana. Un buen silhouette **no** garantiza esto:
mide lo separados que están los grupos, no si **se repiten**.

### ¿Qué es el Jackknife?

Es una técnica de remuestreo muy sencilla:

1. Quitamos al azar un trozo de los clientes (por ejemplo, el 20 %).
2. Re-entrenamos el modelo con el resto.
3. Repetimos muchas veces (20), quitando cada vez un trozo distinto.
4. Comparamos: ¿los clientes que aparecen en varias ejecuciones caen siempre en el mismo segmento?

Si la respuesta es sí, los segmentos son **robustos**: no dependen de clientes concretos.

---

## 1. Cómo lo hicimos (y las trampas que evitamos)

| Decisión | Por qué |
|---|---|
| **Quitamos clientes enteros, no filas** | El CSV tiene una fila por cada pareja cliente–coche. Si quitásemos filas sueltas, a un cliente con 3 coches le podríamos quitar 1 y cambiaría su "nº de vehículos" o su "% electrificado": ya no sería el mismo cliente. Se quita al cliente con todas sus filas |
| **Re-entrenamos todo, no solo K-Means** | Los percentiles por país, el escalado y las medianas para rellenar huecos dependen de qué clientes haya. Forman parte del modelo, así que también se recalculan en cada ejecución |
| **20 ejecuciones quitando el 20 %** y otras 20 quitando el 10 % | Es el rango que pide el reto. Con el 20 %, cada cliente aparece de media en 16 de las 20 |
| **El mismo modelo final** (k = 6, 50 inicializaciones) | Es el que se usaría para marketing |
| **Un control** | Re-entrenar con **todos** los datos cambiando solo la semilla. Así distinguimos si la variación viene de los datos o del azar del propio algoritmo |

### El problema de los nombres de los clusters

En cada ejecución, K-Means numera los grupos al azar: el "cluster 2" de una puede ser el "cluster 4" de otra. Para
comparar hay que **emparejarlos** primero. Usamos el **algoritmo húngaro**: busca la correspondencia entre grupos que
hace coincidir al mayor número de clientes posible.

Como ese emparejamiento podría "maquillar" el resultado, usamos también medidas que **no dependen de los nombres**:

- **ARI (Adjusted Rand Index):** mira si cada **pareja de clientes** sigue junta o separada. 1 = idéntico, 0 = al azar.
- **Jaccard de Hennig, por cluster:** para cada segmento, cuánto se solapa con su mejor equivalente en otra ejecución
  (clientes en común ÷ clientes en total). La escala habitual: **más de 0,85 = muy estable**; 0,75-0,85 = estable;
  0,6-0,75 = patrón débil; menos de 0,5 = el cluster "se disuelve".

---

## 2. Resultado general: muy estable

| | Media | Mínimo |
|---|---|---|
| ARI con el modelo original (quitando el 20 %) | **0,995** | 0,991 |
| % de clientes en el mismo segmento que en el original | **99,8 %** | 99,7 % |
| % de coincidencia entre dos ejecuciones cualesquiera | 99,7 % | 99,4 % |
| ARI quitando solo el 10 % | 0,996 | 0,992 |
| **Control** (todos los datos, solo cambia la semilla) | 0,997 | 0,994 |

**Cómo leerlo:** quitar un 20 % de los clientes apenas cambia nada, y el resultado es casi igual que el del control.
Es decir, la pequeña variación que queda se debe al **azar del algoritmo**, no a qué clientes haya en los datos.

**¿Y el preprocesado?** Comparamos re-entrenar todo frente a usar los datos ya preparados y re-entrenar solo K-Means:
el ARI es el mismo (0,995). Los percentiles y el escalado del Reto 2 son robustos.

---

## 3. Estabilidad de cada cliente

Para cada cliente contamos en qué segmento cae en cada ejecución en la que aparece:

- **99,1 %** de los clientes cae **siempre** en el mismo segmento.
- Solo **1.555 clientes** (0,9 %) cambian alguna vez, y casi siempre solo en una o dos ejecuciones.

---

## 4. ¿Hay algún segmento inestable?

| Segmento | Jaccard media | % de clientes que saltan alguna vez |
|---|---|---|
| Gran Formato | 0,999 | 0,2 % |
| Pionero Eléctrico | 0,999 | 0,3 % |
| Contacto Solo Digital | 0,997 | 0,6 % |
| Recién Llegado de Ocasión | 0,996 | 0,9 % |
| Fiel de Taller | 0,994 | 1,3 % |
| Premium Multivehículo | 0,994 | **1,5 %** |

- **Todos son muy estables** (Jaccard muy por encima de 0,85).
- **Los más sólidos** son Gran Formato y Pionero Eléctrico: los define algo casi de sí o no (furgoneta, eléctrico). No
  hay clientes "a medias".
- **Los menos estables** son Premium Multivehículo y Fiel de Taller. Y los saltos tienen dirección:
  - **Fiel de Taller ↔ Recién Llegado de Ocasión**: el par con más cambios. Los separa el uso del taller, que es una
    variable continua: hay clientes con un uso intermedio.
  - **Premium Multivehículo ↔ Fiel de Taller**: clientes con algo del perfil premium, pero no todo. Premium ya era el
    segmento más heterogéneo (Retos 3 y 4).

---

## 5. ¿Quién salta? Los clientes de la frontera

Para cada cliente medimos su **margen**: cuánto más cerca está de su segmento que del segundo más cercano. Un margen
cercano a 0 significa que está justo en la frontera entre dos segmentos.

- **El 100 % de los clientes que saltan está en el 10 % con menos margen.** Nadie del "centro" de un segmento cambia.
- Su segundo segmento más cercano es justo el segmento al que saltan. No es azar: es una **frontera difusa** entre dos
  perfiles concretos.
- Ejemplo: los que saltan entre Fiel de Taller y Recién Llegado tienen un uso del taller **intermedio** (percentil
  ~0,5), mientras que los estables están en los extremos (~0,8 y ~0,2).

### ¿Silhouette negativo = inestable? No

| Segmento | % con silhouette negativo (Reto 3) | % que saltan en el jackknife |
|---|---|---|
| Premium Multivehículo | **40 %** | 1,5 % |
| Fiel de Taller | 0 % | 1,3 % |

- El **silhouette** mide si un cliente está **más cerca de otro grupo** que del suyo, de media.
- El **jackknife** mide si el cliente cae **siempre en el mismo grupo** cuando cambian los datos.

Premium tiene muchos clientes "en la frontera" según el silhouette, pero asignados siempre igual. Y Fiel de Taller no
tiene ninguno con silhouette negativo, pero algunos saltan. **Son dos preguntas distintas y hacen falta las dos.**

---

## 6. ¿Es mérito de los datos o lo haría cualquier dato?

K-Means **siempre** devuelve k grupos, aunque los datos no tengan estructura. Con 140.000 clientes, podría ser que
cualquier reparto se repitiese solo por tamaño. Lo comprobamos de dos formas:

- **Prueba de estrés:** quitar mucho más (50 %, 70 % y 90 % de los clientes).
- **Modelo nulo:** barajar cada columna por separado. Cada variable conserva sus valores, pero se rompe la relación entre
  ellas, es decir, se destruyen los segmentos reales. Le aplicamos el mismo jackknife.

| % de clientes excluidos | ARI · datos reales | ARI · datos barajados |
|---|---|---|
| 20 % | 0,995 | 0,73 |
| 50 % | 0,992 | 0,75 |
| 70 % | 0,986 | 0,68 |
| 90 % | 0,90 (mínimo 0,58) | 0,72 |

- Con los datos reales, los segmentos aguantan casi intactos **hasta quitar el 70 %** de los clientes.
- Con los datos barajados, el ARI se queda en **~0,7** incluso con el 80 % de los datos.

**Conclusión:** la estabilidad **no es un truco** del algoritmo ni del tamaño de la muestra: nuestras variables tienen
**estructura real**. (Con solo el 10 % de los clientes, alguna ejecución cae en la solución alternativa del apartado
siguiente.)

---

## 7. La fragilidad escondida: dos soluciones casi empatadas

Este es el hallazgo más importante del reto, y solo aparece mirando con detalle.

Todo lo anterior usa **50 inicializaciones** (K-Means prueba 50 puntos de partida y se queda con el mejor). Con el valor
habitual de **10**, **2 de cada 6** ejecuciones dieron una segmentación **distinta** (ARI 0,61). ¿Cuál?

| | Solución A (la nuestra) | Solución B (alternativa) |
|---|---|---|
| Calidad (inercia) | La mejor | Solo **~0,15 % peor** |
| Segmento distintivo | **Contacto Solo Digital** (canal) | **Leasing activo** (relación financiera) |
| Qué pasa con el otro rasgo | El leasing queda repartido, sobre todo en Premium | Los clientes "solo email" se reparten entre los demás grupos |
| Con un solo punto de partida | Se encuentra 11 veces de 60 | Se encuentra **22 veces de 60** |

**Qué significa:**

- Hay **dos formas casi igual de buenas** de cortar la base de clientes. Nuestra segmentación es estable **porque
  buscamos bien el mejor óptimo**, no porque sea la única posible.
- Si alguien del equipo re-entrenase con 10 inicializaciones, tendría bastantes posibilidades de obtener la solución B.
- **"Contacto Solo Digital" es el segmento estructuralmente más frágil**: es muy estable en el modelo bien optimizado,
  pero compite con una alternativa en la que no existe. Encaja con lo visto en el Reto 4: es un segmento de **canal**
  (cómo se le puede contactar), no de tipo de cliente.
- El **leasing** es una forma de segmentar casi tan fuerte como el canal. En nuestra solución aparece dentro de Premium
  (el sub-perfil "Renovador en Leasing" del Reto 4).

> **¿Qué es la inercia?** La suma de las distancias de cada cliente al centro de su grupo (Reto 3). Cuanto menor, más
> compactos son los grupos. Una diferencia del 0,15 % es prácticamente un empate.

---

## 8. ¿Era k = 6 una buena elección?

El jackknife también sirve para elegir k: un buen k da segmentaciones que se repiten.

| k | 3 | 4 | 5 | **6** | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|
| ARI medio entre ejecuciones | 0,997 | 0,996 | 0,986 | **0,990** | 0,993 | 0,995 | 0,907 |

Todos los k de 3 a 8 son muy estables y solo k = 9 baja. Esto **confirma** que k = 6 no es una elección frágil, pero
**no decide** entre k = 3 y 8. Esa decisión sigue siendo la de negocio del Reto 3: segmentar a toda la base en grupos con
estrategia propia.

---

## 9. Recomendación final

1. **La segmentación es robusta y se puede usar para tomar decisiones.** El 99,1 % de los clientes cae siempre en el
   mismo segmento, todos los segmentos superan con holgura el umbral de estabilidad y la estructura no aparece en datos
   sin relación entre variables.
2. **Mantener siempre 50 inicializaciones** (ya está fijado en `ajustar_kmeans` de `features.py`). Y cuando se
   re-entrene con datos nuevos, comprobar con el ARI que el modelo no ha "saltado" a la solución alternativa.
3. **Marcar a los clientes de frontera** (el ~10 % con menos margen) con un **segmento secundario** en el CRM. Son los
   únicos que cambian, y lo hacen hacia su segundo segmento más cercano: les encajan mensajes de ambos.
4. **Tratar el canal como una capa aparte.** Como "Contacto Solo Digital" compite con una segmentación por leasing, una
   opción robusta es usar el número de canales consentidos como **filtro de campaña** sobre todos los segmentos, y
   valorar el **leasing** como segmento en una próxima versión.
5. **k = 6 es una elección estable**, igual que cualquier k entre 3 y 8.

---

## 10. Glosario rápido

| Término | Significado |
|---|---|
| Jackknife | Repetir un análisis quitando cada vez una parte distinta de los datos para ver si el resultado se mantiene |
| Submuestra | La parte de los datos que queda tras quitar un trozo al azar |
| Estabilidad | Que el resultado se repita aunque cambien un poco los datos |
| ARI | Medida de parecido entre dos agrupaciones (1 = idénticas, 0 = como al azar), que no depende de los nombres de los grupos |
| Algoritmo húngaro | Método para emparejar los grupos de dos agrupaciones de forma que coincidan el máximo de clientes |
| Jaccard | Solapamiento entre dos grupos: clientes en común ÷ clientes en total |
| Margen | Cuánto más cerca está un cliente de su segmento que del siguiente; cerca de 0 = en la frontera |
| Modelo nulo | Versión de los datos sin estructura (columnas barajadas), para comprobar si un resultado es real |
| Óptimo local | Una solución "buena" en la que K-Means se queda atascado aunque exista otra mejor |
| Inicialización (`n_init`) | Cuántos puntos de partida prueba K-Means antes de quedarse con el mejor |
