"""MPI: procesa los tableros en orden y reparte las ramas de cada uno."""
import argparse
import sys
from pathlib import Path
from mpi4py import MPI

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mpi_utils import leer_seeds, copiar, resolver_ramas_mpi


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archivo", type=Path, default=Path(__file__).resolve().parents[1] / "seeds.txt")
    seleccion = parser.add_mutually_exclusive_group()
    seleccion.add_argument("--id", help="resolver un único ID")
    seleccion.add_argument("--all", action="store_true", help="resolver todos los IDs en orden (opción predeterminada)")
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

    comm.Barrier()
    inicio = MPI.Wtime() if rank == 0 else None
    reportes = []
    for identificador, original in seleccionados:
        comm.Barrier()
        t0 = MPI.Wtime() if rank == 0 else None
        solucion = resolver_ramas_mpi(copiar(original), comm)
        comm.Barrier()
        if rank == 0:
            segundos = MPI.Wtime() - t0
            reportes.append((identificador, solucion is not None, segundos))
            print(f"ID: {identificador} | {'Resuelto' if solucion is not None else 'Sin solución'} | Tiempo parcial: {segundos:.6f} s", flush=True)
    comm.Barrier()
    if rank == 0:
        total = MPI.Wtime() - inicio
        print(f"Tableros procesados: {len(reportes)}")
        print(f"Procesos: {size}")
        print(f"Tiempo total MPI (reloj real): {total:.6f} segundos")


if __name__ == "__main__":
    main()
