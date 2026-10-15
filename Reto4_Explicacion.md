# Reto 4 · Interpretación de los segmentos — Explicación

> Documento de apoyo al notebook [`Reto4_Segmentos.ipynb`](Reto4_Segmentos.ipynb). Explica qué es cada cosa, por qué se
> hace así y por qué elegimos cada decisión.

---

## 0. ¿Qué es "interpretar" un cluster?

K-Means nos devuelve, para cada cliente, un número del 0 al 5. Ese número **no significa nada** por sí solo. Interpretar
consiste en responder, para cada grupo:

- **¿Quién es?** ¿Qué tienen en común sus clientes y en qué se diferencian de los demás?
- **¿Cómo lo llamamos?** Un nombre que un equipo de marketing entienda sin ver un gráfico.
- **¿Qué hacemos con él?** Qué ofrecerle, cómo mantener su coche, cómo fidelizarlo y por qué canal contactarlo.

Este es el reto que más valora el jurado ("perfilar al cliente con sentido de negocio y utilidad comercial"). También es
donde es más fácil **equivocarse**: un nombre atractivo pero mal fundamentado lleva a campañas equivocadas.

---

## 1. Qué variables usamos para perfilar

Usamos **dos tipos**:

1. **Las 12 features del modelo**, pero en **unidades reales** (años, %, número de vehículos), no escaladas. Un "+1,9"
   no le dice nada a marketing; "mediana de 3 vehículos" sí.
2. **Variables de perfilado**, que **no entraron** en el modelo: país, género, B2B, AMG, modelos concretos, tipo de motor,
   consentimiento por canal y telemetría.

**¿Por qué usar variables que no entraron en el modelo?** Porque describen mejor al grupo sin haberlo condicionado. Por
ejemplo, el país no se usó para agrupar, pero saber que un segmento tiene un 74 % de suizos es útil para planificar
campañas.

Siempre comparamos con la **media de toda la base**: decir que un segmento tiene un 26 % de leasing no informa de nada si
no sabemos que la media es 26 %.

---

## 2. Cómo se asignan los nombres

### El problema de los números

El número de cada cluster (0, 1, 2…) es **arbitrario**: si se cambia la semilla, el cluster "Premium" puede pasar de ser
el 5 a ser el 2. Si escribiésemos "el cluster 5 se llama Premium", un cambio mínimo en el código pondría los nombres en
los grupos equivocados.

**Solución:** cada nombre se asigna con una **regla sobre el rasgo que lo define**:

| Regla | Nombre |
|---|---|
| El de más % de furgonetas | Gran Formato |
| El de más % electrificado | Pionero Eléctrico |
| El de menos canales de contacto | Contacto Solo Digital |
| El de más vehículos en su historia | Premium Multivehículo |
| De los dos restantes, el de más visitas al taller | Fiel de Taller |
| El último (menos visitas al taller) | Recién Llegado de Ocasión |

Así los nombres siempre caen en el grupo correcto.

### El estilo de los nombres

Elegimos nombres **comerciales**, como los del ejemplo del reto ("Premium Tradicional", "Joven Digital"), porque son más
fáciles de recordar y usar en una reunión de marketing. Cada nombre va acompañado de su descripción y sus cifras, para que
no haya malentendidos.

Cuidamos que el nombre **no diga más de lo que dicen los datos**. Por ejemplo, para "Recién Llegado de Ocasión"
descartamos "Joven": aunque es el segmento con más menores de 35 (33 % frente al ~20 % de la base), **la mitad tiene 45
años o más**. Llamarlo "Joven" llevaría a diseñar campañas para un público que no es el mayoritario.

---

## 3. Las trampas de interpretación (lo más importante de este reto)

Antes de dar por bueno un nombre, comprobamos si el rasgo que vemos es **real** o es un **efecto de otra cosa**. Es la
parte que distingue un análisis serio de uno superficial.

### Trampa 1 · ¿Las visitas al taller son del cliente o de la edad de su coche?

**El riesgo.** En el Reto 1 vimos que las visitas en garantía dependen de la edad del coche: suben hasta ~5 años y
luego bajan (se acaba la garantía). Resulta que:

- "Fiel de Taller" tiene coches de **~5 años**, justo en el pico de visitas;
- "Recién Llegado de Ocasión" tiene coches de **~6 años**, ya fuera de garantía.

Si la diferencia se debiera solo a eso, los nombres "Fiel de Taller" y "sin taller oficial" serían **falsos**: estaríamos
describiendo la edad del coche, no al cliente.

**La comprobación.** Comparamos clientes con coches **de la misma edad** (en bandas de 0-2, 2-4, 4-6, 6-8 y 8+ años):

| Segmento | 0-2 | 2-4 | 4-6 | 6-8 | 8+ |
|---|---|---|---|---|---|
| Fiel de Taller | 0,66 | 0,74 | 0,80 | 0,73 | 0,68 |
| Recién Llegado de Ocasión | 0,23 | 0,26 | 0,27 | 0,25 | 0,22 |

(percentil de visitas dentro de su país; 0,5 = lo normal)

**Conclusión:** en **todas** las bandas de edad, "Fiel de Taller" va más al taller y "Recién Llegado" menos. Es
**comportamiento real**. Los nombres se sostienen.

> A esto se le llama una **variable de confusión**: una tercera variable (la edad del coche) que podría explicar la
> relación que vemos. Para descartarla, se compara **dentro de grupos homogéneos** de esa variable.

### Trampa 2 · "Recién Llegado de Ocasión": ¿compró un coche usado?

**El indicio.** En el **81 %** de este segmento, el coche es más de un año más antiguo que la relación del cliente con la
marca (frente al 10 % en Premium Multivehículo). Si alguien es cliente desde hace 20 meses y su coche tiene 6 años, lo
más probable es que lo comprase **de segunda mano**. Además, casi nunca financia (85 %) y no usa el taller oficial.

**Por qué es solo una hipótesis.** La variable `months_as_mb_customer` cuenta los meses **desde la primera conexión** del
cliente a un coche, no desde la compra. Otra explicación posible es que fueran clientes que **activaron tarde** los
servicios conectados.

**Qué hicimos:** presentarlo **como hipótesis**, explicar el dato que la apoya y la alternativa, y proponer cómo
validarla: cruzar con el registro de ventas (coche nuevo / usado / concesionario) antes de lanzar campañas basadas en ella.

> Es importante **no presentar como hecho algo que es una deducción**. Si la hipótesis fuera falsa y diseñásemos una
> campaña de "tu primer Mercedes nuevo" para clientes que ya compraron nuevo, la campaña fracasaría.

### Trampa 3 · "Contacto Solo Digital": ¿no son contactables?

**El riesgo.** El modelo lo separó por tener pocos canales de contacto. Sería fácil llamarlo "no contactables".

**La comprobación.** El **89 % acepta email** (el **79 % solo email**) y **ninguno** tiene 0 canales. Lo que les falta es
teléfono (10 %) y correo postal (11 %). El resto de su perfil (edad, gama, coches, taller) está **en la media**.

**Conclusión:** es un segmento de **canal**, no de tipo de cliente. No dice *qué* ofrecerles, sino *cómo* llegar a ellos.
Su utilidad es operativa: cualquier campaña por teléfono o correo postal **no llega a este 11 % de la base**, y la acción
prioritaria es recuperar consentimientos.

### Trampa 4 · Variables que no diferencian

Comprobamos también qué **no** cambia entre segmentos, para no atribuirles rasgos falsos:

| Variable | Resultado | Conclusión |
|---|---|---|
| Poder adquisitivo de la zona | ≈ 0,5 en todos | El carácter premium viene de **lo que conducen** (gama, AMG), no de **dónde viven**. No hay que vender "Premium" como "zonas ricas" |
| Conducción (km por trayecto, velocidad) | Prácticamente igual en todos | La telemetría no habría ayudado a segmentar |
| Poder adquisitivo imputado | Entre el 2 % y el 15 % según el segmento | En los segmentos con más imputados, la media está algo "aplastada" hacia 0,5 |
| Pico de 36 meses (artefacto del Reto 1) | Entre el 6 % y el 16 % | No domina ningún segmento |

### Trampa 5 · El género

El género es **inferido** (no lo declaró el cliente) y desconocido en hasta un 29 % de un segmento. Por eso **no lo
usamos para definir campañas**. Solo lo mencionamos donde destaca con poco desconocido: "Premium Multivehículo" (81 %
hombres, con solo un 4 % desconocido).

---

## 4. Los seis segmentos

| Segmento | % | Quién es | Prioridad comercial |
|---|---|---|---|
| **Premium Multivehículo** | 12,8 % | Mediana de 3 Mercedes, la mitad con 2 o más a la vez, 58 % leasing, coches de < 2 años, 61 % gama alta, 36 % AMG | Retener y renovar (mayor valor) |
| **Fiel de Taller** | 26,2 % | Veterano (42 meses), un coche compacto o medio de ~5 años, combustión, **mucho uso del taller oficial**, 74 % Suiza | Planes de mantenimiento y renovación |
| **Pionero Eléctrico** | 14,3 % | 97 % híbrido enchufable o eléctrico, coches de ~3 años, cliente reciente, más Austria | Gama EQ y servicios eléctricos |
| **Gran Formato** | 8,7 % | Furgonetas: V-Class/Vito 69 %, Sprinter 20 %; solo 3 % empresas, así que son sobre todo particulares | Renovación de furgoneta, furgonetas eléctricas |
| **Recién Llegado de Ocasión** | 27,1 % | El más reciente (20 meses), coche de 6 años, no usa el taller oficial, 85 % nunca financió, 18 % inactivo | Primer coche nuevo, atraer al taller, evitar el abandono |
| **Contacto Solo Digital** | 10,9 % | Perfil medio, pero el 79 % solo acepta email | Recuperar consentimientos; solo canal digital |

En el notebook, cada segmento tiene una **ficha** con acciones concretas para los cuatro objetivos del reto: ofertas de
vehículos, planes de mantenimiento, campañas de fidelización y comunicaciones dirigidas.

### Cómo se lee la "huella" de cada segmento

En el notebook hay un mapa de calor con la diferencia de cada segmento respecto a la media, en **desviaciones estándar**:
0 = como la media; +2 = muy por encima (rojo); −2 = muy por debajo (azul). La celda más intensa de cada columna es el
rasgo que define al segmento. Por ejemplo, Gran Formato tiene +3,0 en furgonetas.

---

## 5. Sub-perfiles de "Premium Multivehículo"

### Por qué subdividirlo

En el Reto 3 fue el segmento **menos cohesionado**: un 40 % de sus clientes estaba en la frontera con otros grupos. Por
dentro mezcla situaciones distintas:

| Situación | % del segmento |
|---|---|
| Solo multivehículo (2+ coches, sin leasing) | 23,6 % |
| Solo leasing activo | 32,5 % |
| Multivehículo y leasing | 25,8 % |
| Ninguna de las dos (muchos coches en el pasado) | 18,1 % |
| Flota (más de 10 vehículos en su historia) | 7,5 % |

Una única campaña para todos ellos no tendría sentido: no se le ofrece lo mismo a quien está a punto de renovar un
leasing que a una pequeña flota.

### Por qué un sub-clustering y no los retos avanzados

Los retos avanzados piden comparar algoritmos, aplicar PCA y medir la estabilidad con Jackknife. Aplicar un K-Means
**dentro** de un segmento no se solapa con ninguno, y aporta valor directo a marketing, así que lo incluimos aquí.

### Cómo se hizo

Un K-Means **solo con los clientes de este segmento**, con las mismas features y el mismo preprocesado, 50
inicializaciones y k de 2 a 5:

| k | Silhouette | ARI entre semillas | Tamaños |
|---|---|---|---|
| 2 | 0,229 | 1,000 | 23 / 77 % |
| **3** | **0,162** | **0,999** | **50 / 16 / 34 %** |
| 4 | 0,167 | 1,000 | 8 / 30 / 12 / 49 % |
| 5 | 0,117 | 0,999 | 29 / 26 / 8 / 11 / 25 % |

- **k = 2** tiene el mejor silhouette, pero junta a los clientes de leasing con los que compran al contado, que necesitan
  ofertas muy distintas.
- **k = 4** tiene un silhouette casi igual al de k = 3, pero crea un grupo del 8 % (~1.800 clientes), demasiado pequeño
  para una campaña propia.
- **k = 3** separa tres perfiles útiles, es totalmente estable (ARI 0,999) y su silhouette (0,162) es **más del triple**
  que el del segmento completo (0,048). **Elegido**, con el mismo criterio de utilidad del Reto 3.

### Los tres sub-perfiles

| Sub-perfil | % | Rasgos | Acción |
|---|---|---|---|
| **Renovador en Leasing** | 50 % | 98 % con leasing activo, 2 coches en su historia, 1 actual, coche de < 2 años | Renovación anticipada antes de que acabe el leasing |
| **Premium al Contado** | 34 % | 0 % leasing, 3 coches en su historia, 2 actuales, 74 % gama alta | Preestrenos de gama alta y AMG |
| **Gran Cuenta / Flota** | 16 % | 8 coches en su historia (mediana), 3 actuales, 34 % furgonetas, 8 % B2B, 48 % AMG | Condiciones de flota y gestor dedicado |

---

## 6. Resumen de decisiones

| Decisión | Por qué |
|---|---|
| Perfilar en unidades reales y comparar con la media | Las cifras escaladas no se entienden fuera del equipo técnico |
| Usar variables que no entraron en el modelo | Describen sin haber condicionado la agrupación |
| Asignar nombres con reglas sobre los centroides | Los números de cluster son arbitrarios |
| Nombres comerciales, sin decir más de lo que dicen los datos | Fáciles de usar, sin crear expectativas falsas (por ejemplo, "Joven") |
| Comprobar visitas al taller con coches de la misma edad | Descartar que el nombre describa la edad del coche y no al cliente |
| Presentar la "segunda mano" como hipótesis | El dato lo sugiere pero no lo prueba |
| Tratar "Contacto Solo Digital" como segmento de canal | Su único rasgo es cómo se le puede contactar |
| No usar el género para campañas | Es inferido y con mucho desconocido |
| Sub-clustering de Premium con k = 3 | Era el segmento más heterogéneo; tres sub-perfiles estables y accionables |

---

## 7. Glosario rápido

| Término | Significado |
|---|---|
| Perfilar | Describir qué caracteriza a un grupo |
| Variable de perfilado | Variable que no entra en el modelo y se usa solo para describir |
| Huella del segmento | Diferencia de un segmento respecto a la media, en cada variable |
| Variable de confusión | Una tercera variable que podría explicar una relación aparente |
| Hipótesis | Explicación probable que los datos sugieren pero no prueban |
| Segmento de canal | Grupo definido por cómo se le puede contactar, no por su tipo de cliente |
| Sub-clustering | Aplicar clustering dentro de un segmento para subdividirlo |
