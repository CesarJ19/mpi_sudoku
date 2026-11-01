"""MPI híbrido: grupos de procesos reciben tableros y paralelizan sus ramas."""
import argparse
import math
import sys
from pathlib import Path
from mpi4py import MPI

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mpi_utils import leer_seeds, copiar, resolver_ramas_mpi


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archivo", type=Path, default=Path(__file__).resolve().parents[1] / "seeds.txt")
    parser.add_argument("--all", action="store_true", help="resolver los 30 IDs (opción predeterminada)")
    args = parser.parse_args()
    mundo = MPI.COMM_WORLD
    rank, size = mundo.Get_rank(), mundo.Get_size()

    if rank == 0:
        try:
            seeds = list(leer_seeds(args.archivo).items())
            error = None
        except Exception as exc:
            seeds, error = None, str(exc)
    else:
        seeds, error = None, None
    error = mundo.bcast(error, root=0)
    if error:
        if rank == 0:
            parser.error(error)
        return
    seeds = mundo.bcast(seeds, root=0)

    # Aproximadamente raíz cuadrada de N grupos: balance entre tableros
    # simultáneos y procesos disponibles para explorar ramas dentro de cada uno.
    cantidad_grupos = min(len(seeds), max(1, math.isqrt(size)))
    color = rank % cantidad_grupos
    grupo = mundo.Split(color=color, key=rank)
    id_grupo = color
    es_lider = grupo.Get_rank() == 0

    mundo.Barrier()
    inicio = MPI.Wtime() if rank == 0 else None
    reportes_locales = []
    for indice in range(id_grupo, len(seeds), cantidad_grupos):
        identificador, original = seeds[indice]
        grupo.Barrier()
        t0 = MPI.Wtime() if es_lider else None
        solucion = resolver_ramas_mpi(copiar(original), grupo)
        grupo.Barrier()
        if es_lider:
            reportes_locales.append((identificador, solucion is not None,
                                     MPI.Wtime() - t0, id_grupo))
    reportes_grupo = mundo.gather(reportes_locales if es_lider else None, root=0)

    if rank == 0:
        total = MPI.Wtime() - inicio
        planos = [item for bloque in reportes_grupo if bloque for item in bloque]
        planos.sort(key=lambda x: int(x[0]))
        for identificador, resuelto, segundos, grupo_id in planos:
            print(f"ID: {identificador} | {'Resuelto' if resuelto else 'Sin solución'} | Grupo: {grupo_id} | Tiempo parcial: {segundos:.6f} s")
        print(f"Tableros procesados: {len(planos)}")
        print(f"Procesos: {size} | Grupos: {cantidad_grupos}")
        print(f"Procesos por grupo: distribución automática de {size} procesos en {cantidad_grupos} grupos")
        print(f"Tiempo total MPI (reloj real): {total:.6f} segundos")


if __name__ == "__main__":
    main()
