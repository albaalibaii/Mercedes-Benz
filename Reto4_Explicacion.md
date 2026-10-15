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
| **Premium Multivehículo** | 12,9 % | Mediana de 3 Mercedes, la mitad con 2 o más a la vez, 58,5 % leasing, coches de < 2 años, 61 % gama alta, 36 % AMG | Retener y renovar (mayor valor) |
| **Fiel de Taller** | 26,2 % | Veterano (42 meses), un coche compacto o medio de ~5 años, combustión, **mucho uso del taller oficial**, 74 % Suiza | Planes de mantenimiento y renovación |
| **Pionero Eléctrico** | 14,3 % | 97 % híbrido enchufable o eléctrico, coches de ~3 años, cliente reciente, más Austria | Gama EQ y servicios eléctricos |
| **Gran Formato** | 8,8 % | Furgonetas: V-Class/Vito 69 %, Sprinter 20 %; solo 3 % empresas, así que son sobre todo particulares | Renovación de furgoneta, furgonetas eléctricas |
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
| 2 | 0,227 | 0,999 | 23 / 77 % |
| **3** | **0,162** | **1,000** | **16 / 50 / 34 %** |
| 4 | 0,168 | 1,000 | 12 / 50 / 30 / 8 % |
| 5 | 0,116 | 0,998 | 25 / 29 / 26 / 8 / 12 % |

- **k = 2** tiene el mejor silhouette, pero junta a los clientes de leasing con los que compran al contado, que necesitan
  ofertas muy distintas.
- **k = 4** tiene un silhouette casi igual al de k = 3, pero crea un grupo del 8 % (~1.800 clientes), demasiado pequeño
  para una campaña propia.
- **k = 3** separa tres perfiles útiles, es totalmente estable (ARI 1,000) y su silhouette (0,162) es **más del triple**
  que el del segmento completo (0,048). **Elegido**, con el mismo criterio de utilidad del Reto 3.

### Los tres sub-perfiles

| Sub-perfil | % | Rasgos | Acción |
|---|---|---|---|
| **Renovador en Leasing** | 50 % | 98 % con leasing activo, 2 coches en su historia, 1 actual, coche de < 2 años | Renovación anticipada antes de que acabe el leasing |
| **Premium al Contado** | 34 % | 0 % leasing, 3 coches en su historia, 2 actuales, 74 % gama alta | Preestrenos de gama alta y AMG |
| **Gran Cuenta / Flota** | 16 % | 8 coches en su historia (mediana), 3 actuales, 34 % furgonetas, 8 % B2B, 48 % AMG | Condiciones de flota y gestor dedicado |

---

## 6. Salud y seguridad vial por segmento (datos de internet)

### Qué datos son y de dónde salen

En el notebook **Extra_SaludSeguridadVial** descargamos datos **oficiales** de Austria y Suiza y los resumimos en una
tabla por código postal (`datos_externos_por_cp.csv`). Las fuentes exactas (organismo, enlace, periodo y condiciones de
uso) están en [`Fuentes_Datos_Externos.md`](Fuentes_Datos_Externos.md). Con el código postal de cada cliente, cada uno recibe cuatro
datos de **la zona donde vive**:

| Indicador | Qué mide | Austria | Suiza |
|---|---|---|---|
| Accidentes por 1.000 habitantes | Accidentes con heridos al año, sin autopistas | ✓ (distrito) | ✓ (municipio) |
| % de accidentes graves | Accidentes con fallecidos o heridos graves | ✓ | ✓ |
| Mortalidad estandarizada | Muertes por cada 1.000 habitantes, corregida por edad (para que un distrito con más mayores no salga peor solo por eso) | ✓ | ✗ (no se publica por zona) |
| Distancia al hospital | Km en línea recta al hospital general de urgencias más cercano | ✓ | ✓ |

### Tres cuidados importantes

1. **Siempre dentro de cada país.** Suiza tiene la mitad de accidentes por habitante que Austria y hospitales más
   cercanos. Si comparásemos segmentos sin separar países, un segmento con más suizos parecería "más seguro" solo por
   ser suizo: el mismo error de agrupar por país que corregimos en el Reto 2.
2. **Es un dato de la zona, no de la persona.** Todos los vecinos de un distrito tienen el mismo valor. No sabemos si
   un cliente concreto ha tenido un accidente: sabemos cómo es la zona donde vive.
3. **Los vecinos no son independientes.** Con 170.000 clientes, un test estadístico clásico daría "significativa"
   cualquier diferencia diminuta, porque cuenta a cada vecino como una prueba nueva cuando en realidad comparten el
   mismo dato. Por eso usamos un **bootstrap por zonas**: repetimos el cálculo 500 veces sorteando **distritos o
   municipios enteros** y miramos entre qué valores se mueve el resultado (el **intervalo de confianza**). Si el
   intervalo incluye el 100, la diferencia no se distingue de la media.

### Cómo se lee el índice

**Índice 100 = el cliente medio de su país.** Un 118 en distancia al hospital significa que los clientes de ese
segmento viven, de media, un 18 % más lejos del hospital que el cliente típico de su país.

### Qué sale

| Segmento | Qué dice su zona |
|---|---|
| **Gran Formato** | El único que destaca de verdad: **18-20 % más lejos del hospital** en los dos países y, en Austria, **8 % más accidentes graves**. Es el perfil rural o de montaña |
| **Recién Llegado de Ocasión** | El más **urbano**: más cerca del hospital y menos accidentes graves. En Austria tiene la mortalidad de zona más alta, pero la diferencia es mínima (8,97 frente a 8,91 ‰) |
| **Pionero Eléctrico** | Algo más lejos del hospital en Austria (104) y algo más de accidentes graves (101-102): periferias con casa y cargador |
| **Premium, Fiel de Taller, Contacto Solo Digital** | Prácticamente en la media |

**Conclusión:** las diferencias entre segmentos son **pequeñas**. Tiene sentido: los segmentos se formaron por **qué
conduce** el cliente y **cómo se relaciona** con la marca, no por dónde vive (en el apartado de trampas ya vimos que
el poder adquisitivo de la zona tampoco los diferencia).

### Entonces, ¿para qué sirve?

Las diferencias están **dentro** de cada segmento, no entre segmentos. Dentro de Fiel de Taller, por ejemplo, unos
10.600 clientes viven en zonas con muchos accidentes graves y otros 35.000 no. Por eso combinamos las dos cosas:

- **El segmento dice QUÉ ofrecer** (renovación, mantenimiento, gama EQ...).
- **La zona dice A QUIÉN de ese segmento** priorizar con un mensaje de seguridad.

Ejemplo: de los 46.920 "Recién Llegado de Ocasión", **~7.500** viven en zona de muchos accidentes graves y tienen un
coche anterior a julio de 2024. Ese mes entró en vigor el Reglamento General de Seguridad de la UE, que obliga a
llevar asistentes como la frenada de emergencia, así que esos coches pueden no tenerlos. Para ellos: un seminuevo
**Mercedes-Benz Certified** o un primer coche nuevo con **Active Brake Assist** de serie, y una **revisión de
seguridad** gratuita en el taller oficial.

Los cortes ("zona del 25 % con más accidentes graves", "10 % más lejos del hospital") se calculan **entre clientes y
dentro de cada país**. Como los vecinos comparten valor, hay empates y el "25 %" queda en un ~22 %.

**Uso responsable:** el dato de zona decide **dónde y qué** comunicar, **nunca** a quién excluir ni qué precio cobrar.
Los mensajes son positivos y nunca mencionan la salud o los accidentes de la zona del cliente.

---

## 7. ¿Y si metemos esos datos dentro del K-Means?

La otra opción era usar los indicadores de zona como **variables del modelo** y ver si salen segmentos nuevos.

### Cómo lo hicimos

- Añadimos **accidentes, % graves y distancia al hospital** como **percentil dentro de su país** (igual que el poder
  adquisitivo y las visitas al taller del Reto 2) y los escalamos igual que el resto.
- **La mortalidad queda fuera** porque solo existe en Austria. Si rellenásemos con la mediana al 66 % de clientes
  suizos, crearíamos una variable que en realidad separa por país.
- A los clientes sin dato de zona (~10 %) se les pone la mediana, como en el Reto 2.
- Mismo K-Means del Reto 3: k = 6, 50 inicializaciones, semilla 42.

### Qué pasó

| Prueba | Resultado | Qué significa |
|---|---|---|
| Mismo peso que el resto de variables | **ARI 0,978**: salen los mismos 6 segmentos (el 99 % de cada uno cae en su equivalente) | El K-Means **ignora** las variables de zona porque no forman grupos |
| Silhouette | Baja de **0,136 a 0,102** | Solo añaden ruido |
| Zona con **peso doble** | **ARI 0,02**: segmentos totalmente distintos | La zona "se come" el modelo: clusters de "urbano" o "rural" y desaparecen furgonetas, eléctricos, leasing y taller, lo que era útil para vender. Además, el resultado lo decide quien elige el peso, no los datos |
| Mismo peso con **k = 8** | **ARI 0,60** | Las variables de zona siguen sin moverse (ningún centroide pasa de ±0,2): los clusters extra salen de dividir segmentos por rasgos del cliente. Ni dándole sitio aparece un grupo geográfico |

**Dato revelador:** con el poder adquisitivo **por hogar** (la versión anterior), k = 8 sí creaba un grupo "urbano y de
menor poder adquisitivo". Era el **artefacto** que descubrimos en el Reto 1: la variable por hogar mezclaba riqueza con
tamaño del hogar, que va unido a lo rural. Al corregirla, ese falso segmento desaparece. Es un buen ejemplo de cómo un
detalle de datos puede inventar un segmento.

### Decisión

**Los datos de salud y seguridad vial no entran en el clustering.** Con su peso natural no cambian nada y empeoran el
silhouette. Si se les fuerza, convierten segmentos de **cliente** en segmentos **geográficos**. Y son datos de zona,
no de la persona. Su sitio es el del apartado 6: una **capa de perfilado** encima de los 6 segmentos.

---

## 8. Lo que no se ve a simple vista: oportunidades ocultas

Las fichas describen cada segmento por lo **evidente**: lo que lo define. Pero en el Reto 1 (apartado 6) encontramos
relaciones **no evidentes** que no entraron en el modelo. Al cruzarlas con los segmentos aparecen públicos que
**atraviesan** varios segmentos o que **contradicen** su etiqueta.

### Las señales

| Señal | Qué es | De dónde sale |
|---|---|---|
| **PHEV que no se carga** | Híbrido enchufable que consume como un coche de combustión | 1 de cada 7 PHEV (Reto 1) |
| **Hogar mixto** | 2 o más coches actuales, unos electrificados y otros no | El eléctrico entra como coche principal |
| **Multi-combustión** | 2 o más coches actuales, ninguno electrificado | Aún sin electrificar |
| **Riesgo temprano** | Coche de 3 años o menos, sigue activo y **nunca** ha ido al taller oficial | No ir al taller va unido a más abandono |
| **65+ con coche de 8+ años** | Cliente mayor con coche antiguo (y poco usado) | Coche viejo con pocos km |
| **Zona de prevención baja** | Austria: distrito con mucha mortalidad **y** sin visitas al taller | Mortalidad ↔ menos mantenimiento |
| **Perfil incompleto** | Género desconocido | El dato que falta indica relación débil |

### Una comprobación antes de usar el "riesgo temprano"

Los eléctricos necesitan menos mantenimiento: ¿y si un eléctrico sin visitas es simplemente normal? Lo comprobamos con
los clientes que **ya** están inactivos: entre los de coche reciente, los que no fueron al taller están inactivos
**entre 3 y 6 veces más**, en combustión, eléctricos y furgonetas por igual. La señal sirve para todos.

### La relectura de cada segmento

| Segmento | Lo evidente | Lo que no se ve |
|---|---|---|
| **Premium Multivehículo** | Varios coches, leasing, gama alta | Es el que **menos carga sus híbridos** (casi 1 de cada 5 consume como un combustión): PHEV de leasing o empresa elegidos por fiscalidad o imagen. Y es donde está **el siguiente eléctrico**: ~1.900 hogares mixtos y ~2.500 multi-combustión. La conversación es "**electrifique su garaje**" (wallbox, carga, eléctrico compacto) |
| **Pionero Eléctrico** | Coches nuevos y electrificados | El de **más riesgo temprano**: ~4.300 (17 %) no han ido al taller con un coche de ≤ 3 años. El eléctrico apenas necesita mantenimiento, así que **la marca pierde el contacto físico**. Necesita otros puntos de contacto: actualizaciones, revisión de batería, eventos de carga |
| **Recién Llegado de Ocasión** | Reciente, coche antiguo, sin taller | **Concentra lo que no se ve**: más riesgo temprano (~5.200), más mayores con coche viejo (~2.900), más de la mitad de los de zona de prevención baja y el perfil más incompleto (29 % sin género). El objetivo no es venderle un coche: es **completar la relación** (datos, primera visita, revisión de seguridad) |
| **Fiel de Taller** | Usa mucho el taller | El **reservorio de los mayores**: ~1.600 clientes de 65+ con coche de 8+ años, poco usado y bien cuidado. Público ideal para "**tu coche vale más de lo que crees**" y un cambio a un coche más seguro y cómodo |
| **Gran Formato** | Furgonetas | Rural, conduce más rápido (carretera) y un 15 % de riesgo temprano: probablemente furgonetas atendidas en **talleres independientes cercanos**. Una red de **servicio móvil** o talleres asociados en zonas rurales lo retendría |
| **Contacto Solo Digital** | Solo email | Sin señales propias destacables: su reto sigue siendo el canal |

### La idea que atraviesa todo

El taller oficial no es solo posventa: es **el principal termómetro de la relación**. Una alerta "**coche nuevo sin
primera visita al taller**" en el CRM permitiría actuar **antes** de que el cliente desaparezca, en todos los segmentos.

---

## 9. Salud y ergonomía por segmento

Con las probabilidades esperadas de salud del Reto 1 (Eurostat, por país, edad y sexo), la posición de conducción de sus
coches y la duración de sus trayectos, se ve qué necesidad ergonómica tiene cada segmento y si su coche la cubre.
Fuentes: [`Fuentes_Datos_Externos.md`](Fuentes_Datos_Externos.md).

| Segmento | Limitación esperada | Coches altos | Lo que significa |
|---|---|---|---|
| **Recién Llegado de Ocasión** | ~30 % | **~37 %** | **La mayor brecha**: ~8.200 clientes con limitación esperada sin coche alto y ~4.700 de 65+ sin coche alto. Oferta: seminuevo Certified de posición alta (GLA, GLB, Clase B) |
| **Fiel de Taller** | ~32 % | ~50 % | Segunda brecha (~6.700 y ~3.300). Su coche está en edad de renovación: GLB o GLC con KEYLESS-GO y portón eléctrico, probado en su propio taller |
| **Pionero Eléctrico** | **~34 %** | ~73 % | La mayor necesidad (clientes de más edad), pero ya van sentados alto. Su ergonomía está en el interior: asientos multicontorno, cámara de 360° |
| **Contacto Solo Digital** | ~34 % | ~53 % | Necesidad alta y la mitad sin coche alto; solo se le llega por email |
| **Gran Formato** | ~31 % | ~100 % | Ya va alto, pero hace **los trayectos más largos** (~1 de cada 5 con trayectos medios de 30+ min): ergonomía de trabajo (asientos de confort con apoyo lumbar) |
| **Premium Multivehículo** | ~31 % | ~61 % | Necesidad más baja, trayectos más largos que la media: argumento de confort (masaje, ENERGIZING, AIRMATIC) |

**Idea transversal:** unos **21.000 clientes** con limitación esperada conducen un coche que no es alto. Es un argumento
de renovación distinto del precio o la tecnología: el **bienestar al volante**. Siempre en clave de comodidad, nunca de
salud ni de edad.

---

## 10. Resumen de decisiones

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
| Comparar la zona de cada segmento dentro de cada país | Austria y Suiza tienen niveles muy distintos de accidentes y distancias |
| Bootstrap por zonas, no test clásico | Los vecinos comparten el dato de zona y no son observaciones independientes |
| Datos de zona como capa de perfilado, no como variables del K-Means | No cambian los segmentos con su peso natural; forzados, los vuelven geográficos |
| Cruzar los segmentos con las relaciones no evidentes del Reto 1 | Aparecen públicos que la etiqueta del segmento no cuenta |
| Validar la señal de riesgo temprano por tipo de vehículo | Descartar que los eléctricos "no vayan al taller" solo porque no lo necesitan |
| Salud como probabilidad esperada por edad y sexo | Estimar necesidades ergonómicas sin tratar datos de salud de nadie |

---

## 11. Glosario rápido

| Término | Significado |
|---|---|
| Perfilar | Describir qué caracteriza a un grupo |
| Variable de perfilado | Variable que no entra en el modelo y se usa solo para describir |
| Huella del segmento | Diferencia de un segmento respecto a la media, en cada variable |
| Variable de confusión | Una tercera variable que podría explicar una relación aparente |
| Hipótesis | Explicación probable que los datos sugieren pero no prueban |
| Segmento de canal | Grupo definido por cómo se le puede contactar, no por su tipo de cliente |
| Sub-clustering | Aplicar clustering dentro de un segmento para subdividirlo |
| Dato de zona | Valor que comparten todos los que viven en el mismo distrito o municipio |
| Mortalidad estandarizada | Tasa de mortalidad corregida por la edad de la población, para comparar zonas jóvenes y envejecidas |
| Índice 100 | Forma de comparar: 100 es la media; 118 es un 18 % por encima |
| Bootstrap por zonas | Repetir el cálculo sorteando zonas enteras para ver cuánto puede variar el resultado |
| Intervalo de confianza | Rango en el que probablemente está el valor real; si incluye el 100, no se distingue de la media |
| Capa de perfilado | Información que se añade encima de los segmentos para describirlos, sin cambiar cómo se formaron |
