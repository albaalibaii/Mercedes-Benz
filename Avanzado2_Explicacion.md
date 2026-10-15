# Reto avanzado 2 · Reducción de dimensionalidad (PCA) y visualización — Explicación

> Documento de apoyo al notebook [`Avanzado2_PCA.ipynb`](Avanzado2_PCA.ipynb). Explica qué es cada cosa, por qué se hace
> así y por qué elegimos cada decisión.

---

## 0. El problema: no se pueden dibujar 12 dimensiones

Cada cliente está descrito por 12 features (edad, nº de vehículos, % electrificado…). Matemáticamente es un **punto en un
espacio de 12 dimensiones**. Podemos dibujar 2 dimensiones en un papel y, con algo de esfuerzo, 3. Doce, no.

La **reducción de dimensionalidad** busca representar esos 12 números con solo 2 o 3, perdiendo la menor información
posible, para poder **ver** los clusters.

---

## 1. ¿Qué es el PCA?

El **PCA** (*Principal Component Analysis*, Análisis de Componentes Principales) busca las **direcciones en las que los
clientes más se diferencian entre sí**.

**Una analogía:** imagina una nube de puntos con forma de puro (alargada). Si tuvieras que describirla con una sola línea,
elegirías la que la recorre a lo largo, porque es donde los puntos más varían. Esa línea es el **primer componente
principal (PC1)**. El segundo (PC2) es la siguiente dirección con más variación, **perpendicular** a la primera, y así
sucesivamente.

- Cada componente es una **mezcla** de las features originales (por ejemplo, "0,49 × vehículos + 0,43 × vehículos
  actuales + …").
- Con 12 features se obtienen **12 componentes**, ordenados de más a menos información.
- Si nos quedamos con los 2 primeros, tenemos la mejor "foto" posible en 2D.

### Requisito: escalar antes

El PCA busca la máxima **varianza** (dispersión). Si una variable va de 0 a 120 (meses) y otra de 0 a 1 (%), la primera
tendría muchísima más varianza solo por sus unidades y dominaría el resultado. Nuestras features ya llegan **escaladas**
del pipeline del Reto 2 (media 0, desviación 1), así que todas parten en igualdad.

### Para qué lo usamos (y para qué no)

Aquí el PCA es **solo para visualizar e interpretar**. El modelo K-Means sigue entrenado con las 12 features originales.

---

## 2. Varianza explicada: ¿cuánta información conserva cada componente?

La **varianza explicada** es el porcentaje de la información total (variación entre clientes) que recoge cada componente.

| Componente | % varianza | % acumulado | Autovalor |
|---|---|---|---|
| PC1 | 18,1 % | 18,1 % | 2,17 |
| PC2 | 12,4 % | **30,5 %** | 1,49 |
| PC3 | 10,6 % | 41,1 % | 1,27 |
| PC4 | 9,7 % | 50,8 % | 1,16 |
| PC5 | 8,9 % | 59,7 % | 1,07 |
| PC6 | 8,3 % | 68,0 % | 0,99 |
| PC7 | 7,7 % | 75,6 % | 0,92 |
| PC8 | 6,7 % | **82,3 %** | 0,80 |
| PC9-PC12 | 17,7 % | 100 % | < 0,7 |

### Cómo leerla

- **El gráfico en 2D solo muestra el 30,5 % de la información.** El 70 % restante queda oculto. Con 3D, el 41 %.
- **Para conservar el 80 % harían falta 8 componentes.**
- **Criterio de Kaiser:** quedarse con los componentes de **autovalor > 1**, es decir, los que explican más que una sola
  variable original. Serían **5** (60 % de la varianza).

> **¿Qué es el autovalor?** La varianza que recoge cada componente, en las mismas unidades que las features escaladas
> (cada feature tiene varianza 1). Un autovalor de 2,17 significa que PC1 recoge la información de "algo más de dos
> variables".

### Por qué la varianza está tan repartida

Si las features estuvieran muy relacionadas entre sí (por ejemplo, edad y antigüedad como cliente moviéndose juntas),
unos pocos componentes lo resumirían casi todo. En el Reto 2 vimos que nuestras features están **poco correlacionadas**
(la correlación más alta era 0,52). Cada una aporta información **propia**, así que no se pueden comprimir en pocas
dimensiones sin perder mucho.

Esto no es un problema del modelo (es bueno que las features no sean redundantes), pero sí una **limitación para
visualizar**.

---

## 3. ¿Qué significa cada componente? (las cargas)

La **carga** de una feature en un componente indica cuánto contribuye a él:

- **Valor alto** (positivo o negativo): esa feature define el componente.
- **Mismo signo**: las features van juntas. **Signo contrario**: van en sentido opuesto.
- **El signo global es arbitrario**: PC1 y −PC1 son el mismo eje visto desde el otro lado. Lo que importa es qué
  variables van juntas.

| Componente | Variables principales | Interpretación |
|---|---|---|
| **PC1** (18,1 %) | + vehículos (histórico y actuales), meses de cliente, leasing, visitas, gama · − antigüedad del coche | **Intensidad de la relación con la marca**: muchos coches, nuevos, con leasing |
| **PC2** (12,4 %) | + antigüedad del coche, meses de cliente, visitas · − electrificado, leasing | **Veterano con coche de combustión antiguo** frente a **cliente reciente con coche eléctrico** |
| **PC3** (10,6 %) | + electrificado, edad, visitas · − furgoneta | **Electrificación**, opuesta a las furgonetas |
| **PC4** (9,7 %) | + edad, gama · − leasing, visitas | **Cliente mayor de gama alta que compra al contado** |
| **PC5** (8,9 %) | + furgoneta · − gama | **Furgonetas** |
| **PC6** (8,3 %) | + canales consentidos (0,89), poder adquisitivo (0,43) | **Contactabilidad** |

**Detalle:** algunas features se reparten entre varios componentes (las visitas al taller cargan en PC1, PC2 y PC3). Es
normal cuando las variables están poco correlacionadas: los componentes no siempre tienen una interpretación "limpia".

---

## 4. Los clusters en 2D

### El problema del sobretrazado

Si dibujamos los 173.456 clientes, los últimos puntos tapan a los primeros y el gráfico muestra **el orden en que se
dibujaron**, no la estructura real. Por eso:

- dibujamos una **muestra aleatoria de 15.000 clientes** con **transparencia**;
- marcamos con una **X** el **centroide** de cada segmento, calculado con **todos** los clientes;
- además, hacemos un gráfico por segmento (en color) sobre el resto de clientes (en gris).

### Lo que se ve en PC1-PC2

- **Premium Multivehículo** se separa claramente a la **derecha** (PC1 alto: muchos coches, leasing, gama alta).
- **Pionero Eléctrico** se separa hacia **abajo** (PC2 bajo: coche nuevo electrificado).
- **Fiel de Taller** (arriba) y **Recién Llegado de Ocasión** (izquierda) ocupan **zonas distintas pero contiguas**.
- **Gran Formato** y **Contacto Solo Digital** aparecen **mezclados en el centro**.

### Las franjas no son grupos

En el gráfico se ven **líneas y franjas paralelas**. No son grupos de clientes: aparecen porque varias features tienen
**pocos valores posibles** (6 tramos de edad, 4 niveles de gama, 3 canales…). Cada combinación de valores discretos forma
una "lámina" de puntos. Es un efecto de los datos, no algo que interpretar.

### El biplot

En el **biplot** se dibujan las features como flechas sobre el mapa. Cada flecha indica hacia dónde crece esa variable.
Un segmento situado en la dirección de una flecha tiene valores altos de esa feature. Por ejemplo, Premium está en la
dirección de las flechas de vehículos y leasing.

---

## 5. Los segmentos "ocultos" (el hallazgo más importante)

Gran Formato y Contacto Solo Digital **parecen mezclados** en 2D. ¿Significa que el modelo los separó mal? Para
comprobarlo, calculamos la **posición media de cada segmento en cada componente**:

| Segmento | Componente donde se separa | Valor |
|---|---|---|
| Premium Multivehículo | PC1 | +2,55 |
| Pionero Eléctrico | PC2 y PC3 | −1,32 / +1,41 |
| Fiel de Taller | PC2 | +0,97 |
| Recién Llegado de Ocasión | PC1 | −1,24 |
| **Gran Formato** | **PC5** (y PC3) | **+2,35** (−1,36) |
| **Contacto Solo Digital** | **PC6** | **−2,14** |

Gran Formato y Contacto Solo Digital se separan en **PC5 y PC6**, que no salen en el gráfico 2D. Al dibujarlos en esos
componentes (PC3 vs PC5 y PC1 vs PC6), **aparecen claramente separados**: Gran Formato forma una "isla" propia y Contacto
Solo Digital queda abajo, aparte.

> **El error más habitual al leer un PCA** es concluir que dos clusters se solapan porque se solapan en PC1-PC2. Esas dos
> dimensiones solo recogen el 30 % de la información, y un segmento puede estar perfectamente separado en otra.

---

## 6. Vista 3D

Añadir PC3 (electrificación frente a furgonetas) separa mejor a **Pionero Eléctrico** (hacia arriba) y empieza a apartar
a **Gran Formato**. Pero el 3D solo recoge el **41 %** de la varianza, y Contacto Solo Digital sigue mezclado (se separa
en PC6).

Lo hicimos con matplotlib (estático) para no instalar librerías adicionales. Una versión interactiva (girable) requeriría
otra librería.

---

## 7. ¿Son los clusters visualmente separables?

### Medición

Para no responder "a ojo", calculamos el **silhouette** de los mismos clusters midiendo las distancias solo con los
primeros *d* componentes:

| Componentes usados | 2 | 3 | 4 | 5 | 6 | 8 | 10 | 12 |
|---|---|---|---|---|---|---|---|---|
| Silhouette | **0,070** | 0,118 | 0,117 | 0,158 | **0,186** | 0,156 | 0,142 | 0,135 |

- En **2D** el silhouette es la **mitad** que con todas las features: en el plano PC1-PC2 los clusters parecen
  **mucho más solapados de lo que están**.
- Con **5-6 componentes** el silhouette es incluso **mayor** que con las 12 features. Los últimos componentes tienen poca
  varianza y añaden sobre todo "ruido" que difumina las fronteras. Es una observación interesante: un K-Means sobre 5-6
  componentes podría separar algo mejor. Pero cambiar el modelo queda fuera de este reto.

### Valoración

**En 2D, los clusters no son visualmente separables en su conjunto.** Solo Premium Multivehículo y Pionero Eléctrico se
distinguen con claridad.

**Esto no significa que los clusters estén mal:**

1. El 2D solo muestra el **30 %** de la información. Los segmentos "ocultos" se separan con claridad en PC5 y PC6.
2. La varianza está **muy repartida**, así que **ninguna** proyección en 2D puede mostrar bien 6 segmentos definidos por
   variables distintas (furgonetas, eléctricos, consentimientos…).
3. Es coherente con todo lo anterior: los clientes forman un **continuo**. Los segmentos con un rasgo muy marcado se ven
   separados; Fiel de Taller frente a Recién Llegado es un corte gradual (como vimos en el avanzado 1).

### Recomendación de uso

- Para presentaciones, el gráfico PC1-PC2 sirve para mostrar el **eje de valor** (Premium) y el **eje de
  electrificación**, siempre avisando de que es una **vista parcial** (30 %).
- Para Gran Formato y Contacto Solo Digital, usar sus componentes (PC5, PC6) o directamente la tabla de perfilado del
  Reto 4.

---

## 8. Resumen de decisiones

| Decisión | Por qué |
|---|---|
| PCA sobre las features ya escaladas | Sin escalar, dominarían las variables con unidades grandes |
| Usar el PCA solo para visualizar | El modelo debe seguir basándose en toda la información |
| Muestra de 15.000 con transparencia y centroides con todos | Evitar el sobretrazado sin perder precisión en los centros |
| Gráfico por segmento sobre gris | Ver cada segmento sin que los demás lo tapen |
| Buscar en qué componente se separa cada segmento | Detectar segmentos ocultos en 2D |
| Medir la separabilidad con silhouette por nº de componentes | Responder con datos, no a ojo |
| 3D estático con matplotlib | Opcional en el reto; sin instalar librerías nuevas |

---

## 9. Glosario rápido

| Término | Significado |
|---|---|
| Dimensión | Cada variable que describe a un cliente |
| PCA | Técnica que busca las direcciones de máxima variación para resumir los datos en menos dimensiones |
| Componente principal (PC) | Cada una de esas direcciones; una mezcla de las features originales |
| Varianza explicada | % de la información total que recoge un componente |
| Autovalor | Varianza de un componente, en unidades de "nº de variables originales" |
| Criterio de Kaiser | Quedarse con los componentes de autovalor > 1 |
| Carga | Peso de una feature en un componente |
| Biplot | Gráfico que muestra a la vez los clientes y las features (como flechas) |
| Sobretrazado | Cuando hay tantos puntos que unos tapan a otros |
