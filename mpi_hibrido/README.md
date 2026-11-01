# MPI híbrido

## Descripción

La estrategia MPI híbrida combina dos niveles de paralelismo: la distribución de tableros entre grupos de procesos y la distribución de ramas dentro de cada grupo. De esta manera, se busca aprovechar el trabajo paralelo tanto entre diferentes sudokus como dentro de la resolución de un mismo sudoku.

## Funcionamiento

Los procesos se dividen en grupos. Cada grupo recibe IDs diferentes en orden intercalado y resuelve sus tableros uno por uno. Mientras se resuelve un tablero, los procesos que pertenecen al mismo grupo reparten entre sí las ramas de búsqueda.

El número de grupos se calcula automáticamente mediante la expresión `min(30, max(1, floor(sqrt(N))))`. Esta regla busca equilibrar el paralelismo entre tableros y el paralelismo dentro de cada tablero. Los procesos se distribuyen entre los grupos mediante `MPI\\\_Comm\\\_split`.

Por ejemplo, cuando `N = 8`, se forman 2 grupos. Cada grupo recibe una parte de los IDs y utiliza sus procesos para resolver las ramas de cada tablero asignado.

## Ejecución

Desde la carpeta raíz del proyecto, en PowerShell, ejecuta:

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n N python /app/mpi\\\_hibrido/mpi\\\_hibrido.py --all
```

Reemplaza `N` por el valor seleccionado durante la calibración. En macOS/Linux, utiliza `-v "$(pwd):/app"` para montar la carpeta del proyecto.

## Resultados

El programa muestra qué grupo resolvió cada ID y el tiempo total real necesario para completar el trabajo y reunir los resultados de todos los grupos. Este tiempo permite evaluar el rendimiento de la estrategia híbrida considerando tanto la resolución como la coordinación entre procesos.



