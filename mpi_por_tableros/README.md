# MPI por tableros

## Descripción

La estrategia MPI por tableros distribuye los sudokus completos entre los procesos disponibles. Cada proceso trabaja de manera independiente sobre los IDs que recibe, sin tener que dividir la búsqueda de un mismo tablero con los demás procesos.

## Funcionamiento

Cada proceso recibe una parte de los IDs completos y resuelve sus tableros de forma independiente. Cuando termina su trabajo, envía los resultados al coordinador, que los reúne y los ordena para presentar la salida final.

Esta estrategia permite resolver varios sudokus al mismo tiempo. La cantidad de procesos utilizada se indica mediante `N`, que debe corresponder al valor elegido durante la calibración.

## Ejecución

Desde la carpeta raíz del proyecto, en PowerShell, ejecuta todos los tableros con:

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n N python /app/mpi\\\_por\\\_tableros/mpi\\\_tableros.py --all
```

Para resolver un único tablero, por ejemplo el ID 7, utiliza:

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n N python /app/mpi\\\_por\\\_tableros/mpi\\\_tableros.py --id 7
```

Reemplaza `N` por el valor elegido con `detectar\\\_procesos\\\_mpi.py`. En macOS/Linux, cambia el montaje por `-v "$(pwd):/app"`.

## Resultados y medición del tiempo

El tiempo total informado es el tiempo real transcurrido desde que comienza el trabajo distribuido hasta que el coordinador recibe todos los resultados. Los tiempos individuales corresponden a búsquedas locales de cada proceso y no deben sumarse para obtener el tiempo total de ejecución.



