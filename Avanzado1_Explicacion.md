# Reto avanzado 1 · Comparativa de algoritmos de clustering — Explicación

> Documento de apoyo al notebook [`Avanzado1_Comparativa.ipynb`](Avanzado1_Comparativa.ipynb). Explica qué es cada cosa,
> por qué se hace así y por qué elegimos cada decisión.

---

## 0. ¿Por qué comparar con otros algoritmos?

K-Means es solo **una forma** de agrupar, con sus propios supuestos: busca grupos **redondeados y de tamaño parecido**
alrededor de un centro. Si los datos tuvieran grupos alargados, de tamaños muy distintos o con formas raras, otro
algoritmo podría encontrar una segmentación mejor.

Comparar sirve para dos cosas:

1. **Elegir el algoritmo más adecuado** con argumentos, no por costumbre.
2. **Validar los segmentos**: si un segmento aparece con cualquier método, es **robusto**; si solo aparece con uno, es
   más bien una **decisión** de ese método.

El reto pide usar el **mismo k (6)** y los **mismos datos preparados** (las 12 features del Reto 2), para que la
comparación sea justa.

---

## 1. Los algoritmos

### K-Means (nuestro modelo)
Coloca k centros y asigna cada cliente al más cercano (Reto 3). Rápido, usa todos los clientes y da centroides fáciles de
interpretar.

### Gaussian Mixture Models (GMM)
Supone que los datos son una **mezcla de k "campanas"** (distribuciones normales), cada una con su forma, orientación y
tamaño. En vez de asignar a cada cliente a un grupo de forma rotunda, calcula **la probabilidad** de que pertenezca a cada
uno ("70 % grupo A, 30 % grupo B").

- **Ventaja teórica:** es más flexible que K-Means (de hecho, K-Means es un caso particular de GMM con campanas redondas e
  iguales).
- **Supuesto:** las variables son **continuas** y con forma de campana.

### Clustering aglomerativo (jerárquico)
Empieza con cada cliente como un grupo y va **uniendo los dos grupos más parecidos**, paso a paso, hasta quedarse con k.
Cómo se mide "parecido" depende del **enlace**:

| Enlace | Une los dos grupos… |
|---|---|
| **Ward** | …cuya unión aumenta menos la varianza (el mismo criterio que K-Means) |
| **Average** | …con menor distancia media entre todos sus clientes |
| **Complete** | …cuyo par de clientes más lejanos está más cerca |

### DBSCAN
Busca **zonas densas** (muchos clientes juntos) separadas por **zonas vacías**. Los clientes en zonas poco densas son
**ruido**. No recibe k: recibe un radio (`eps`) y un número mínimo de vecinos (`min_samples`).

---

## 2. Cómo comparamos de forma justa

### La misma muestra para todos

- El **silhouette** compara cada cliente con todos los demás: con 173.456 clientes es inviable (Reto 3).
- El **aglomerativo** no cabe en memoria con todos los clientes (apartado 4).

Por eso todas las métricas se calculan sobre **la misma muestra aleatoria de 20.000 clientes**. Si cada algoritmo se
evaluase con una muestra distinta, las diferencias podrían deberse a la muestra y no al algoritmo.

### Tres métricas

| Métrica | Qué mide | Mejor si |
|---|---|---|
| **Silhouette** | Si cada cliente está más cerca de los de su grupo que de los del grupo vecino | Más alto (máx. 1) |
| **Calinski-Harabasz** | Cuánto se separan los grupos entre sí respecto a lo dispersos que están por dentro | Más alto |
| **Davies-Bouldin** | Cuánto se parece, de media, cada grupo a su vecino más parecido | Más bajo (mín. 0) |

Usamos tres porque cada una tiene sus puntos débiles, y si coinciden la conclusión es más sólida.

### Dos advertencias importantes

1. **Las tres métricas favorecen a K-Means.** Todas usan distancias y premian grupos compactos y redondeados, que es
   exactamente lo que construye K-Means. Un algoritmo con grupos alargados podría ser mejor y puntuar peor.
2. **Una métrica alta no garantiza una buena segmentación.** Por eso añadimos el **tamaño del cluster más grande**: si un
   algoritmo mete al 90 % de los clientes en un grupo, no sirve para marketing aunque su métrica sea buena (lo vemos en el
   apartado 4).

---

## 3. GMM: un problema oculto

### El síntoma

GMM asignó a **todos** los clientes a su grupo con una probabilidad superior al 90 %. Parece una buena noticia, pero es
**sospechoso**: en el Reto 3 vimos que los grupos se solapan bastante. Lo esperable sería que muchos clientes estuvieran
"a medias" entre dos grupos.

### La causa: campanas degeneradas

Al mirar la **varianza** (lo "ancha" que es cada campana) de cada componente, varias valen prácticamente **0**
(0,000001, el mínimo que permite el algoritmo). Ocurre en variables **casi discretas**:

| Feature | Valores distintos |
|---|---|
| Canales consentidos | 3 |
| Vehículos actuales | 6 |
| % furgoneta y % electrificado | Casi siempre 0 % o 100 % |

GMM descubre que muchísimos clientes tienen **exactamente** "1 vehículo, 0 % furgoneta, 0 % eléctrico, 3 canales" y pone
una campana **infinitamente estrecha** justo encima de ese punto. Esa campana es "perfecta" para esos clientes, así que
la probabilidad se dispara al 100 %. Es un **artefacto matemático**: GMM asume variables continuas en forma de campana, y
las nuestras son en parte discretas.

### El intento de solución: regularizar

La solución habitual es **regularizar** (`reg_covar`): obligar a que cada campana tenga una anchura mínima. Probamos
varios valores:

| `reg_covar` | Silhouette | Parecido con K-Means (ARI) | Cluster más grande |
|---|---|---|---|
| 0,000001 (estándar) | 0,114 | 0,36 | 46 % |
| 0,05 | 0,110 | 0,36 | 46 % |
| 0,1 | 0,123 | 0,32 | 35 % |
| 0,3 | 0,139 | 0,48 | 38 % |

**Conclusión:** el resultado **cambia mucho** según un parámetro que no tiene un valor "correcto". Si eligiésemos el que
da mejor silhouette (0,3), estaríamos **ajustando el modelo a la métrica**. Además, GMM **cambia con la semilla**: de tres
ejecuciones, ninguna coincide con otra (parecido de solo 0,47-0,72). Y siempre aparece un grupo gigante (35-46 %). **GMM no es robusto
con estos datos.**

---

## 4. Aglomerativo: memoria y la trampa del silhouette

### Un límite de memoria

El aglomerativo necesita la distancia entre **cada par** de clientes:

- con 173.456 clientes son **15.000 millones de pares** → unos **120 GB** de memoria. **Inviable.**
- con 20.000 clientes → 1,6 GB. Factible.

**Solución:** entrenarlo con la muestra de 20.000 y asignar a cada uno de los otros 153.456 clientes el grupo
mayoritario entre sus **15 vecinos más cercanos** de la muestra. Así obtenemos una segmentación de toda la base,
comparable con K-Means.

### La trampa del silhouette

| Enlace | Silhouette | Cluster más grande |
|---|---|---|
| Average | **0,155** (el mejor de todo el reto) | **95 %** |
| Ward | 0,150 | 40 % |
| Complete | 0,015 | 68 % |

El enlace *average* tiene el mejor silhouette de todos, pero mete al **95 % de los clientes en un solo grupo** y reparte el
5 % restante en grupos de unos pocos clientes. El silhouette sale alto porque esos clientes raros están muy lejos de todo,
así que "su" grupo está muy bien separado. **Como segmentación no sirve para nada.**

> Esta es la razón por la que **nunca hay que elegir un modelo solo por una métrica**. Siempre hay que mirar qué grupos
> produce.

Solo **Ward** da grupos equilibrados, así que es el que comparamos con K-Means.

### Ward depende de la muestra

Repetimos Ward con **otras dos muestras** de 20.000 clientes. El parecido entre resultados fue de **0,51-0,82** (ARI).
Es decir, según qué clientes caigan en la muestra, los grupos pueden cambiar bastante. K-Means usa a todos los clientes y
es estable (0,997).

---

## 5. DBSCAN: no encaja con nuestros datos

Para elegir el radio `eps` se usa el **gráfico de k-distancias**: para cada cliente, la distancia a su vecino número
`min_samples` (24 = 2 × 12 features, una regla habitual), ordenada de menor a mayor. Si los datos tuvieran zonas densas
separadas por vacíos, el gráfico tendría un "codo" claro que indica el `eps` adecuado. **No lo tiene.**

Probamos varios valores:

| `eps` | Grupos | % ruido | Grupo más grande |
|---|---|---|---|
| 0,5 | 0 | 100 % | — |
| 1,0 | 21 | 66 % | 12 % |
| 1,3 | 14 | 43 % | 36 % |
| 1,6 | 12 | 21 % | 65 % |
| 2,0 | 4 | 7 % | 84 % |

- Con `eps` pequeño, **la mayoría de los clientes es "ruido"**.
- Con `eps` grande, **un grupo se lo come todo**.
- Nunca aparecen ~6 grupos equilibrados.

**¿Por qué?** DBSCAN necesita **huecos** entre los grupos, y nuestros clientes forman un **continuo** sin huecos (como
vimos en el Reto 3). Además, **no permite fijar k = 6**, que es lo que pide el reto. Por eso queda documentado como **no
adecuado** y fuera de la tabla comparativa.

---

## 6. Resultados

| Algoritmo | Silhouette | Calinski-Harabasz | Davies-Bouldin | Cluster más grande | Estabilidad |
|---|---|---|---|---|---|
| **K-Means** | 0,136 | **2.205** | **1,89** | **27 %** | **0,997** entre semillas |
| GMM (estándar) | 0,114 | 1.727 | 2,62 | 46 % | Sensible a la semilla (0,47-0,72) |
| GMM (regularizado) | 0,139 | 1.953 | 2,01 | 38 % | Sensible a `reg_covar` |
| Aglomerativo (Ward) | 0,150 | 1.901 | 1,95 | 40 % | 0,51-0,82 entre muestras |

### Cómo leerlos

- **K-Means** gana en Calinski-Harabasz, en Davies-Bouldin y en equilibrio, y es con diferencia el más estable.
- GMM regularizado y Ward tienen un silhouette **algo mayor** (+0,003 y +0,014), pero **siempre** a costa de crear un
  **grupo enorme** (38-40 %). Es el mismo fenómeno que vimos con k = 4 en el Reto 3: juntar a "los del medio" sube el silhouette porque deja
  muy aislados a los grupos de los extremos.
- Todas las diferencias de silhouette son **pequeñas** (entre 0,11 y 0,15): ningún algoritmo descubre una estructura que
  K-Means no viera.

---

## 7. ¿Cambian los segmentos entre algoritmos?

### El parecido global (ARI)

El **ARI** (Adjusted Rand Index) mide cuánto se parecen dos agrupaciones: 1 = idénticas, 0 = como dos repartos al azar.
Entre K-Means y los demás sale **0,36-0,48**: parecido **moderado**. Pero el ARI global no dice **qué** segmentos coinciden.

### Segmento a segmento

**Problema:** los números de grupo no se corresponden entre algoritmos (el "grupo 2" de Ward no tiene por qué ser el
"grupo 2" de K-Means). Usamos el **algoritmo húngaro**, que busca la correspondencia entre grupos que hace coincidir al
mayor número de clientes.

**Una trampa en esta lectura:** el emparejamiento es **uno a uno**. Si otro algoritmo **junta dos segmentos** en un grupo
grande, ese grupo solo puede emparejarse con uno de ellos, y el otro parece "desaparecer". Por eso medimos también qué
parte de cada segmento acaba en el **grupo más grande** del otro algoritmo:

| Segmento de K-Means | Se mantiene unido | % que acaba en el grupo gigante de otros algoritmos |
|---|---|---|
| Gran Formato | ~97 % | ~0 % |
| Pionero Eléctrico | ~90 % | 0-1 % |
| Contacto Solo Digital | 70-89 % (salvo GMM estándar: 11 %) | 2-51 % |
| Premium Multivehículo | ~60 % (27-82 %) | 0-4 % |
| **Fiel de Taller** | — | **51-78 %** |
| **Recién Llegado de Ocasión** | — | **74-86 %** |

### Conclusiones

- **Segmentos robustos**: **Gran Formato** y **Pionero Eléctrico** salen con cualquier algoritmo, porque los define un
  rasgo muy marcado (furgoneta, electrificado). **Contacto Solo Digital** también, salvo con el GMM degenerado.
- **Fiel de Taller y Recién Llegado de Ocasión se fusionan** en el grupo gigante de los demás algoritmos. Los separa sobre
  todo el uso del taller, una variable **continua**, y solo K-Means corta ese continuo en dos.
- **Premium Multivehículo** se reparte entre dos grupos, coherente con lo heterogéneo que ya vimos que era (Retos 3 y 4).

Que dos segmentos se fusionen con otros algoritmos **no los invalida**: separarlos fue una **decisión de negocio**
(Reto 3) para que toda la base tenga una estrategia propia. Pero indica que su frontera es **gradual**, no natural. Para
marketing, los clientes cercanos a esa frontera pueden recibir mensajes de ambos segmentos.

---

## 8. Conclusión: ¿qué algoritmo es el más adecuado?

**K-Means**, por cinco motivos:

1. **Ningún algoritmo encuentra una estructura claramente mejor.** Las pequeñas mejoras de silhouette siempre vienen de
   crear un grupo gigante, menos útil para marketing.
2. **Es el más estable**: mismos segmentos con cualquier semilla (0,997), frente a GMM (sensible a parámetros y semilla)
   y Ward (sensible a la muestra).
3. **Usa toda la base**, sin muestreo.
4. **Es el más equilibrado**: ningún segmento supera el 27 %.
5. **Sus supuestos encajan con los datos**: no necesita variables en forma de campana (GMM) ni huecos entre grupos
   (DBSCAN).

**Lo que aporta la comparativa:** sabemos qué segmentos son robustos (Gran Formato, Pionero Eléctrico, Contacto Solo
Digital) y cuáles son cortes útiles de un continuo (Fiel de Taller frente a Recién Llegado de Ocasión, y el heterogéneo
Premium Multivehículo).

---

## 9. Glosario rápido

| Término | Significado |
|---|---|
| GMM | Modelo de mezcla de distribuciones normales ("campanas"); asigna probabilidades |
| Varianza | Lo "ancha" o dispersa que es una distribución |
| Componente degenerado | Campana con varianza casi 0, que se coloca sobre un valor exacto |
| Regularización (`reg_covar`) | Imponer una varianza mínima para evitar componentes degenerados |
| Aglomerativo | Clustering que une grupos paso a paso, de abajo arriba |
| Enlace (Ward, average, complete) | Criterio para decidir qué dos grupos se unen |
| DBSCAN | Clustering por densidad; detecta ruido y no recibe k |
| `eps` | Radio de vecindad de DBSCAN |
| Calinski-Harabasz | Métrica: separación entre grupos / dispersión interna (más alto, mejor) |
| Davies-Bouldin | Métrica: parecido de cada grupo con su vecino (más bajo, mejor) |
| ARI | Parecido entre dos agrupaciones (1 = idénticas) |
| Algoritmo húngaro | Método para emparejar los grupos de dos agrupaciones de forma óptima |
