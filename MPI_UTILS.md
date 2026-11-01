# MPI\_UTILS



El archivo `mpi\_utils.py` contiene funciones auxiliares que pueden ser utilizadas por las diferentes estrategias de paralelización MPI del proyecto de resolución de Sudoku.



Se creó con el propósito de evitar repetir código en cada implementación, facilitar el mantenimiento y centralizar las operaciones que son comunes entre las estrategias.



¿Por qué se utiliza?



Las implementaciones MPI por tableros, MPI por ramas y MPI híbrido necesitan realizar algunas operaciones similares para trabajar con los procesos y gestionar la información. En lugar de escribir las mismas funciones en cada archivo, se organizan en un único módulo que puede ser importado cuando sea necesario.



Ejemplos de funciones que se pueden compartir



\- Comunicación entre procesos: funciones para enviar y recibir información mediante MPI.

\- Distribución de tareas: operaciones para asignar tableros o ramas a los diferentes procesos.

\- Gestión de resultados: funciones para recopilar y organizar las soluciones encontradas.

\- Control de procesos: operaciones de sincronización y coordinación entre los procesos.



Ventajas



\- Evita duplicar código en las diferentes estrategias.

\- Facilita la corrección de errores.

\- Permite reutilizar funciones comunes.

\- Hace que los archivos principales de cada estrategia sean más organizados y fáciles de mantener.



Uso



Las estrategias pueden importar las funciones necesarias desde `mpi\_utils.py`, evitando volver a implementarlas en cada archivo.



En conclusión, este módulo sirve como apoyo para las implementaciones MPI, centralizando las funciones compartidas y manteniendo una estructura de código más organizada.

