# MPI por ramas

## Descripción

La estrategia MPI por ramas divide el trabajo de resolución de un mismo sudoku entre varios procesos. En lugar de asignar tableros completos a procesos diferentes, los procesos colaboran para resolver cada tablero.

## Funcionamiento

El coordinador recorre los IDs en orden. Para cada tablero, identifica la primera casilla vacía y genera ramas a partir de los valores válidos que pueden colocarse en ella. Después distribuye esas ramas entre los procesos para que las exploren en paralelo.

Los tableros se procesan uno después de otro: el siguiente no comienza hasta que termina el actual. Cuando un proceso encuentra una solución, avisa a los demás procesos de ese comunicador para que interrumpan la búsqueda que todavía tengan pendiente. Así se evita continuar explorando ramas que ya no son necesarias.

## Ejecución

Desde la carpeta raíz del proyecto, en PowerShell, ejecuta todos los tableros con:

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n N python /app/mpi\\\_por\\\_ramas/mpi\\\_ramas.py --all
```

Para resolver únicamente un tablero, por ejemplo el ID 7, utiliza:

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n N python /app/mpi\\\_por\\\_ramas/mpi\\\_ramas.py --id 7
```

Reemplaza `N` por el valor seleccionado durante la calibración. En macOS/Linux, utiliza `-v "$(pwd):/app"` para montar la carpeta del proyecto.

## Resultados

El programa muestra el tiempo parcial de cada tablero y el tiempo total real de la secuencia completa. El tiempo total corresponde a la ejecución de todos los IDs en orden, incluyendo la coordinación necesaria entre los procesos.



