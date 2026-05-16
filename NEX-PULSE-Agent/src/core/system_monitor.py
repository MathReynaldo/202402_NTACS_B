# -*- coding: utf-8 -*-
"""
Módulo de monitoreo de recursos del sistema para NEX-PULSE Agent.

Proporciona interfaces para obtener métricas en tiempo real de CPU, Memoria,
Disco y Procesos utilizando la librería psutil. Diseñado para ser stateless,
eficiente y resistente a errores de permisos.

Dependencias:
    - psutil (Debe estar instalado: pip install psutil)

Autor: NEX-PULSE Team
Versión: 1.0.0
Target: Windows 10/11
"""

import os
import time
from typing import Dict, List, Any, Union

# Intentamos importar psutil de forma segura
try:
    import psutil
except ImportError:
    psutil = None

# Configuración de Logging
try:
    from .logs_manager import setup_logger
    logger = setup_logger("SystemMonitor")
except (ImportError, ValueError):
    import logging
    logger = logging.getLogger("SystemMonitor")

def _check_psutil():
    """Verifica si psutil está disponible y loguea un error crítico si no."""
    if psutil is None:
        msg = "La librería 'psutil' no está instalada. El monitoreo no funcionará."
        logger.critical(msg)
        raise ImportError(msg)

def get_cpu_metrics(interval: float = None) -> Dict[str, Any]:
    """
    Obtiene métricas actuales del procesador.

    Args:
        interval (float): Tiempo de bloqueo para cálculo de CPU. Si es None, es no bloqueante
                          y retorna el valor desde la última llamada.

    Returns:
        Dict: {
            'usage_percent': float,
            'physical_cores': int,
            'logical_cores': int,
            'frequency_current': float (Mhz)
        }
    """
    _check_psutil()
    try:
        # percent(interval=None) es no bloqueante por defecto
        usage = psutil.cpu_percent(interval=interval)
        
        # Conteo de núcleos
        p_cores = psutil.cpu_count(logical=False)
        l_cores = psutil.cpu_count(logical=True)
        
        # Frecuencia (puede fallar en algunos entornos virtuales o restringidos)
        try:
            freq = psutil.cpu_freq().current
        except Exception:
            freq = 0.0

        return {
            "usage_percent": usage,
            "physical_cores": p_cores or 1,
            "logical_cores": l_cores or 1,
            "frequency_current": freq
        }
    except Exception as e:
        logger.error(f"Error obteniendo métricas de CPU: {e}")
        return {
            "usage_percent": 0.0,
            "physical_cores": 1,
            "logical_cores": 1,
            "frequency_current": 0.0
        }

def get_memory_metrics() -> Dict[str, Any]:
    """
    Obtiene estado actual de la memoria RAM.

    Returns:
        Dict: {
            'total': int (bytes),
            'available': int (bytes),
            'used': int (bytes),
            'percent': float
        }
    """
    _check_psutil()
    try:
        mem = psutil.virtual_memory()
        return {
            "total": mem.total,
            "available": mem.available,
            "used": mem.used,
            "percent": mem.percent
        }
    except Exception as e:
        logger.error(f"Error obteniendo métricas de Memoria: {e}")
        return {"total": 0, "available": 0, "used": 0, "percent": 0.0}

def get_disk_metrics(path: str = "C:\\") -> Dict[str, Any]:
    """
    Obtiene uso de disco para la partición o ruta especificada.

    Args:
        path (str): Ruta o letra de unidad (ej: "C:\\").

    Returns:
        Dict: {
            'total': int (bytes),
            'used': int (bytes),
            'free': int (bytes),
            'percent': float
        }
    """
    _check_psutil()
    try:
        # En Windows es importante asegurar que la ruta exista
        # Si la ruta no existe, usamos el directorio actual como fallback seguro
        target_path = path if os.path.exists(path) else os.getcwd()

        usage = psutil.disk_usage(target_path)
        return {
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "percent": usage.percent
        }
    except Exception as e:
        logger.error(f"Error obteniendo métricas de Disco ({path}): {e}")
        return {"total": 0, "used": 0, "free": 0, "percent": 0.0}

def get_top_processes(limit: int = 5, sort_by: str = "cpu") -> List[Dict[str, Any]]:
    """
    Obtiene la lista de procesos que más recursos consumen (Top N).

    Args:
        limit (int): Cantidad de procesos a retornar.
        sort_by (str): Criterio de ordenamiento ('cpu' o 'memory').

    Returns:
        List[Dict]: Lista con info del proceso (pid, name, cpu_percent, memory_percent).
    """
    _check_psutil()
    procs = []
    
    # Atributos a recuperar (oneshot para eficiencia)
    attrs = ['pid', 'name', 'cpu_percent', 'memory_percent']
    
    try:
        # Iterar sobre todos los procesos en ejecución
        for p in psutil.process_iter(attrs):
            try:
                # psutil cachea los valores en p.info
                p_info = p.info
                
                # Saneamiento de nombre y prevención de DoS por desbordamiento de string
                p_info['name'] = str(p_info['name'])[:100] if p_info['name'] else "Unknown"
                
                # Normalizar valores None
                if p_info['cpu_percent'] is None: p_info['cpu_percent'] = 0.0
                if p_info['memory_percent'] is None: p_info['memory_percent'] = 0.0

                procs.append(p_info)

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Procesos que mueren o son del sistema durante la iteración
                pass
    except Exception as e:
        logger.error(f"Error iterando procesos: {e}")
        return []

    # Selección de clave de ordenamiento
    key = 'cpu_percent' if sort_by == 'cpu' else 'memory_percent'
    
    # Ordenar lista (Descendente)
    procs.sort(key=lambda x: x.get(key, 0), reverse=True)
    
    return procs[:limit]

def get_system_summary() -> Dict[str, Any]:
    """
    Helper para obtener una foto completa instantánea del estado del sistema.
    Útil para la UI o logs periódicos.
    """
    return {
        "cpu": get_cpu_metrics(),
        "memory": get_memory_metrics(),
        "disk": get_disk_metrics(),
        "network": get_network_metrics(),
        "timestamp": time.time()
    }

_last_net_io = None
_last_net_time = None

def get_network_metrics() -> Dict[str, Any]:
    """
    Calcula el uso actual de la red (ancho de banda).
    """
    global _last_net_io, _last_net_time
    _check_psutil()
    try:
        current_io = psutil.net_io_counters()
        current_time = time.time()

        if _last_net_io is None:
            _last_net_io = current_io
            _last_net_time = current_time
            return {"bytes_sent_sec": 0, "bytes_recv_sec": 0}

        time_delta = current_time - _last_net_time
        if time_delta == 0: time_delta = 1

        sent_sec = (current_io.bytes_sent - _last_net_io.bytes_sent) / time_delta
        recv_sec = (current_io.bytes_recv - _last_net_io.bytes_recv) / time_delta

        _last_net_io = current_io
        _last_net_time = current_time

        return {
            "bytes_sent_sec": max(0, sent_sec),
            "bytes_recv_sec": max(0, recv_sec)
        }
    except Exception as e:
        logger.error(f"Error obteniendo métricas de Red: {e}")
        return {"bytes_sent_sec": 0, "bytes_recv_sec": 0}

# ==============================================================================
# BLOQUE DE PRUEBA (EJECUCIÓN DIRECTA)
# ==============================================================================
if __name__ == "__main__":
    print(f"--- System Monitor Test (PID: {os.getpid()}) ---")
    
    if psutil is None:
        print("ERROR CRÍTICO: psutil no instalado.")
    else:
        # Llamada inicial para "cebar" el contador de CPU de psutil (primera llamada suele dar 0.0)
        psutil.cpu_percent()
        time.sleep(0.5) 

        print("\n[MÉTRICAS EN TIEMPO REAL]")
        print(f"CPU: {get_cpu_metrics()}")
        print(f"RAM: {get_memory_metrics()}")
        print(f"DISK (C:): {get_disk_metrics('C:\\')}")
        
        print("\n[TOP 3 CPU]")
        for i, p in enumerate(get_top_processes(3, 'cpu'), 1):
            print(f"  {i}. {p['name']:<20} PID:{p['pid']:<6} CPU:{p['cpu_percent']}%")
            
        print("\n[TOP 3 RAM]")
        for i, p in enumerate(get_top_processes(3, 'memory'), 1):
            print(f"  {i}. {p['name']:<20} PID:{p['pid']:<6} RAM:{p['memory_percent']:.2f}%")
            