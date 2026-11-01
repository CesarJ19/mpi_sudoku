"""MPI: asigna tableros completos a distintos procesos."""
import argparse
import sys
import time
from pathlib import Path

from mpi4py import MPI

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mpi_utils import leer_seeds, copiar, resolver_serial


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archivo", type=Path, default=Path(__file__).resolve().parents[1] / "seeds.txt")
    seleccion = parser.add_mutually_exclusive_group()
    seleccion.add_argument("--id", help="resolver un único ID")
    seleccion.add_argument("--all", action="store_true", help="resolver todos los IDs (opción predeterminada)")
    args = parser.parse_args()
    comm = MPI.COMM_WORLD
    rank, size = comm.Get_rank(), comm.Get_size()

    if rank == 0:
        try:
            seeds = leer_seeds(args.archivo)
            if args.id:
                if args.id not in seeds:
                    raise ValueError(f"ID '{args.id}' no existe")
                seleccionados = [(args.id, seeds[args.id])]
            else:
                seleccionados = list(seeds.items())
            error = None
        except Exception as exc:
            seleccionados, error = None, str(exc)
    else:
        seleccionados, error = None, None
    error = comm.bcast(error, root=0)
    if error:
        if rank == 0:
            parser.error(error)
        return
    seleccionados = comm.bcast(seleccionados, root=0)
    tareas = [seleccionados[i] for i in range(rank, len(seleccionados), size)]

    comm.Barrier()
    inicio = MPI.Wtime() if rank == 0 else None
    locales = []
    for identificador, original in tareas:
        t0 = time.perf_counter()
        solucion = resolver_serial(copiar(original))
        locales.append((identificador, solucion is not None, time.perf_counter() - t0))
    resultados = comm.gather(locales, root=0)

    if rank == 0:
        total = MPI.Wtime() - inicio
        planos = sorted((item for bloque in resultados for item in bloque), key=lambda x: int(x[0]))
        for identificador, resuelto, segundos in planos:
            print(f"ID: {identificador} | {'Resuelto' if resuelto else 'Sin solución'} | Tiempo de búsqueda: {segundos:.6f} s")
        print(f"Tableros procesados: {len(planos)}")
        print(f"Procesos: {size}")
        print(f"Tiempo total MPI (reloj real): {total:.6f} segundos")


if __name__ == "__main__":
    main()
