# Informe de resultados

Completa las mediciones en el equipo donde se ejecutará la entrega. Usa el mismo `seeds.txt`, el mismo contenedor y el mismo valor de N para las tres estrategias MPI.

## Entorno

* Equipo / procesador: Intel(R) Core(TM) i5-10300H CPU @ 2.50GHz, 2496 Mhz, 4 procesadores principales, 8 procesadores lógicos.
* Sistema operativo: Microsoft Windows 11 Home Single Language.
* Versión del contenedor: `augustosalazar/slim-mpi:2`
* Repeticiones por implementación: 3
* Valor común de N (salida `N RECOMENDADO`): 8
* Número de procesadores lógicos detectados (`nproc`):

## Mediciones

Ejecuta tres veces cada comando de `--all` y registra los tres tiempos. Calcula la mediana y coloca ese resultado en la tabla.

|Implementación|Caso|Procesos|Mediana del tiempo total (s)|Aceleración frente a secuencial|
|-|-|-:|-:|-:|
|Secuencial|Todos los IDs|1|113.971190|1,00|
|MPI por tableros|Todos los IDs|8|40,428355|2,82|
|MPI por ramas|Todos los IDs, en orden|8|187,653525|0,61|
|MPI híbrido|Todos los IDs|8|104,288720|1,09|

### Registro de las tres repeticiones

|Implementación|Repetición 1 (s)|Repetición 2 (s)|Repetición 3 (s)|Mediana (s)|
|-|-:|-:|-:|-:|
|Secuencial|113.296799|114.545191|113.971190|113.971190|
|MPI por tableros|40.341161|40.428355|41.273884|40.428355|
|MPI por ramas|182.721928|195.260893|187.653525|187.653525|
|MPI híbrido|104.288720|104.271912|111.751505|104.288720|

Aceleración = mediana secuencial / mediana MPI. El tiempo total MPI debe ser el tiempo de pared desde el inicio del trabajo distribuido hasta que se reciben todos los resultados; no sumes los tiempos de búsqueda de los procesos.

## Estrategia híbrida

La implementación usa `min(30, max(1, floor(sqrt(N))))` grupos. Cada grupo recibe IDs intercalados y resuelve sus tableros en orden; dentro del grupo, los procesos exploran ramas distintas del tablero actual.

## Conclusiones (completar con las mediciones)

1. **Estrategia más rápida:** Estrategia MPI por tableros, teniendo una mediana de 40.428355. Teniendo la mediana secuencial en 113.971190, seria 73.54 segundos más rápida la estrategia MPI por tableros.

2. **Aceleración:** La aceleración del tiempo secuencial entre la estrategia MPI por tableros es de 2.82.

3. **Comunicación:** MPI por tableros tuvo un menor costo de coordinación, porque cada proceso resolvía sudokus independientes. En MPI por ramas, repartir tareas, comunicar soluciones y sincronizar procesos generó mayores costos. MPI híbrido también necesitó coordinación entre grupos. Esto se refleja en que MPI por tableros fue la estrategia más rápida, MPI híbrido tuvo un rendimiento intermedio y MPI por ramas presentó el mayor tiempo de ejecución. Esto se refleja en sus tiempos totales: 40.428355 s, 187.653525 s y 104.288720 s, respectivamente. 

4. **Balance de carga:** Aunque MPI por tableros obtuvo la mejor mediana, de 40.428355 segundos, algunos sudokus necesitaron más tiempo para su resolución que otros, por lo que los procesos no terminaron al mismo tiempo. Esto ocasionó que algunos procesos quedaran desocupados mientras otros seguían trabajando, afectando el aprovechamiento de los 8 procesos.

5. **Comparación de estrategias:** Se produjeron los tiempos de 40.428355 s, 187.653525 s y 104.288720 s, respectivamente porque MPI por tableros distribuyó sudokus independientes entre los procesos, reduciendo la comunicación. MPI por ramas fue la más lenta porque los procesos debían colaborar en un mismo tablero, generando más comunicación y sincronización. MPI híbrido combinó ambas estrategias, pero la coordinación entre grupos y el reparto de ramas aumentaron el tiempo de ejecución.



No completes las conclusiones con cifras estimadas: usa las medianas medidas en tu equipo.

