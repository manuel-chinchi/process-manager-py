# file:     pmcore.py 
# version:  1.0 beta
#
# TODO list (version: 1.0 beta)
# [1.1] Hacer mas pruebas
# [1.2] Revisar manejo de excepciones en 'get_process_list'
# [1.3] Refactorizar logica en 'get_process_info' y 'get_process_info_v2' 
#       para que cada tanda de combinacion de columnas que se pasa devuelva
#       una tupla diferente. En pruebas comprobe que a menos parametros reque
#       ridos tarda menos tiempo.


import psutil
from datetime import datetime
import time
from typing import List, Tuple

# Libraries for optimizing execute time of functions
from multiprocessing import Pool, cpu_count
from diskcache import Cache


# Tiempos que tarda 'get_process_list' con todas las columnas seleccionadas
OPTIMIZED_LEVEL_0 = 0 # ~4s
OPTIMIZED_LEVEL_1 = 1 # ~2,5s / 2s
OPTIMIZED_LEVEL_2 = 2 # ~1s
CACHE_EXPIRATION = 60  # seconds

COL_PID = 0
COL_NAME = 1
COL_STATUS = 2
COL_CREATE_TIME = 3
COL_CPU_PERCENT = 4
COL_MEMORY_INFO = 5
COL_EXE = 6

cache = Cache('/tmp/process_cache')


def get_process_info(pid) -> Tuple[int, str, str, str, float, str, str]:
    """Obtiene la información de un proceso dado su PID."""
    try:
        process = psutil.Process(pid)
        return (
            pid,
            process.name() or "___",
            process.status(),
            # datetime.fromtimestamp(process.create_time()).strftime('%Y-%m-%d %H:%M:%S'),
            process.create_time(),  # sirve para ordenar el dato
            process.cpu_percent(),
            f"{(process.memory_info().rss / 1048576):.2f} mb",
            process.exe() or "___"
        )
    # except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
    except (psutil.AccessDenied,psutil.NoSuchProcess):
        return (
            pid,
            "N/A",
            "N/A",
            "N/A",
            0.0,
            "N/A",
            "N/A"
        )


def get_process_info_v2(pid) -> Tuple[int, str, str, str, float, str, str]:
    """Obtiene la información de un proceso dado su PID. Usa almacenamiento en cache"""
    if pid in cache:
        return cache[pid]  # Retorna el resultado almacenado en caché

    try:
        process = psutil.Process(pid)
        result = (
            pid,
            process.name() or "___",
            process.status(),
            # datetime.fromtimestamp(process.create_time()).strftime('%Y-%m-%d %H:%M:%S'),
            process.create_time(),  # sirve para ordenar el dato
            process.cpu_percent(),
            f"{(process.memory_info().rss / 1048576):.2f} mb",  # Convertir a MB
            process.exe() or "___"
        )
        # cache[pid] = result  # Almacena el resultado en caché
        cache.set(pid, result, CACHE_EXPIRATION)
        return result
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        result = (
            pid,
            process.name(),
            "N/A",
            "(Acceso Denegado)",
            0.0,
            "N/A",
            "N/A"
        )
        cache.set(pid, result, CACHE_EXPIRATION)
        # cache[pid] = result  # Almacena el resultado en caché
        return result


def get_process_list(opt_level: int = OPTIMIZED_LEVEL_0) -> list:
    """Devuelve la lista de procesos usando un nivel de optimizacion

        Args:
            opt_level (int): Nivel de optimización (0, 1 o 2).

        Returns:
            List[Tuple]: Lista de tuplas con información de los procesos.
    """
    if opt_level not in [OPTIMIZED_LEVEL_0, OPTIMIZED_LEVEL_1, OPTIMIZED_LEVEL_2]:
        raise ValueError("El nivel de optimización debe ser 0, 1 o 2.")

    pids = [p.info['pid'] for p in psutil.process_iter(attrs=['pid'])]

    if opt_level == OPTIMIZED_LEVEL_0:
        return list(get_process_info(pid) for pid in pids)
    elif opt_level == OPTIMIZED_LEVEL_1:
        with Pool(cpu_count()) as pool:
            return list(pool.map(get_process_info, pids))
    elif opt_level == OPTIMIZED_LEVEL_2:
        with Pool(cpu_count()) as pool:
            return list(pool.map(get_process_info_v2, pids))
