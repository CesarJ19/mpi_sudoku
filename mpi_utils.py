"""Funciones compartidas para las tres estrategias MPI de Sudoku."""
from pathlib import Path

from sudoku import puede_colocar, resolver

TAG_SOLUCION = 731


def leer_seeds(ruta):
    """Lee id|tablero, admitiendo 0 y . como casillas vacías."""
    seeds = {}
    for linea in Path(ruta).read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        identificador, contenido = linea.split("|", 1)
        contenido = contenido.strip().replace(".", "0")
        if len(contenido) != 81 or any(c not in "0123456789" for c in contenido):
            raise ValueError(f"La seed {identificador} no contiene 81 dígitos válidos")
        celdas = [int(c) for c in contenido]
        seeds[identificador.strip()] = [celdas[i:i + 9] for i in range(0, 81, 9)]
    return seeds


def crear_ramas(tablero):
    """Crea una tarea por cada valor válido en la primera casilla vacía."""
    for f in range(9):
        for c in range(9):
            if tablero[f][c] == 0:
                ramas = []
                for valor in range(1, 10):
                    if puede_colocar(tablero, f, c, valor):
                        copia = [fila[:] for fila in tablero]
                        copia[f][c] = valor
                        ramas.append(copia)
                return ramas
    # El tablero ya está completo: una sola tarea permite validarlo/resolverlo.
    return [[fila[:] for fila in tablero]]


class SolucionDeOtroProceso(Exception):
    pass


def resolver_ramas_mpi(tablero, comm):
    """Distribuye ramas en un comunicador y cancela búsquedas al hallar solución.

    Se duplica el comunicador para cada tablero. Así, los avisos de solución
    pendientes de una búsqueda no pueden confundirse con los de otro tablero.
    Devuelve una matriz resuelta o None. El tablero de entrada no se modifica.
    """
    from mpi4py import MPI

    # Cada tablero tiene su propio contexto de comunicación y sus propios tags.
    trabajo = comm.Dup()
    rank = trabajo.Get_rank()
    size = trabajo.Get_size()

    try:
        ramas = crear_ramas(tablero) if rank == 0 else None
        ramas = trabajo.bcast(ramas, root=0)
        solucion_local = None
        solucion_conocida = None

        def comprobar_cancelacion():
            nonlocal solucion_conocida
            if solucion_conocida is not None:
                raise SolucionDeOtroProceso

            # Drena todos los avisos que ya hayan llegado, no solo uno.
            while trabajo.Iprobe(source=MPI.ANY_SOURCE, tag=TAG_SOLUCION):
                recibida = trabajo.recv(source=MPI.ANY_SOURCE, tag=TAG_SOLUCION)
                if solucion_conocida is None:
                    solucion_conocida = recibida
                raise SolucionDeOtroProceso

        def buscar(actual):
            comprobar_cancelacion()
            for f in range(9):
                for c in range(9):
                    if actual[f][c] != 0:
                        continue
                    for valor in range(1, 10):
                        comprobar_cancelacion()
                        if puede_colocar(actual, f, c, valor):
                            actual[f][c] = valor
                            if buscar(actual):
                                return True
                            actual[f][c] = 0
                    return False
            return True

        try:
            for indice in range(rank, len(ramas), size):
                comprobar_cancelacion()
                candidato = [fila[:] for fila in ramas[indice]]
                if buscar(candidato):
                    solucion_local = candidato
                    # Avisar a los demás procesos de este tablero.
                    solicitudes = [
                        trabajo.isend(solucion_local, dest=destino, tag=TAG_SOLUCION)
                        for destino in range(size) if destino != rank
                    ]
                    for solicitud in solicitudes:
                        solicitud.wait()
                    break
        except SolucionDeOtroProceso:
            pass

        # Todos llegan aquí después de terminar o cancelar su búsqueda.
        soluciones = trabajo.allgather(solucion_local)

        if solucion_local is not None:
            return solucion_local
        if solucion_conocida is not None:
            return solucion_conocida
        for solucion in soluciones:
            if solucion is not None:
                return solucion
        return None
    finally:
        # Dup/Free son colectivos: aíslan por completo los mensajes de este tablero.
        trabajo.Free()


def copiar(tablero):
    return [fila[:] for fila in tablero]
