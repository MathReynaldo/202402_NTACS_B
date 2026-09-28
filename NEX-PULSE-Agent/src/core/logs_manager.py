# -*- coding: utf-8 -*-
"""
Módulo de gestión de Logs para NEX-PULSE Agent.

Este módulo proporciona una interfaz centralizada para la creación y configuración
de loggers. Maneja la salida a consola y archivo con rotación automática,
asegurando consistencia en el formato y manejo de errores.

Características:
- Singleton-like behavior para loggers nombrados.
- Rotación de archivos basada en tamaño.
- Salida dual (Consola + Archivo).
- Creación automática de directorios de log.

Autor: NEX-PULSE Team
Versión: 1.0.0
"""

import logging
import logging.handlers
import sys
import os
from pathlib import Path

# Intentamos importar la configuración global.
# Se asume que config.py está en el root del proyecto.
try:
    import config
except ImportError:
    # Fallback robusto: añade el directorio padre al path si falla el import directo
    # Esto es útil para tests unitarios o ejecuciones aisladas del módulo
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    import config

# ==============================================================================
# CONFIGURACIÓN POR DEFECTO (FALLBACKS)
# ==============================================================================
# Si por alguna razón la configuración externa falla, usamos valores seguros.
DEFAULT_LOG_LEVEL = getattr(config, "LOG_LEVEL", logging.INFO)
DEFAULT_FORMAT = getattr(config, "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
DEFAULT_DATE_FORMAT = getattr(config, "LOG_DATE_FORMAT", "%Y-%m-%d %H:%M:%S")

def setup_logger(module_name: str, level: int = None) -> logging.Logger:
    """
    Configura y devuelve una instancia de logger para el módulo especificado.

    Si el logger ya tiene handlers configurados, se devuelve la instancia existente
    para evitar duplicidad de mensajes (idempotencia).

    Args:
        module_name (str): Nombre del módulo (usualmente __name__).
        level (int, optional): Nivel de log específico. Si es None, usa el global.

    Returns:
        logging.Logger: Instancia configurada de logger.
    """
    logger = logging.getLogger(module_name)
    
    # Determinar el nivel de logging
    target_level = level if level is not None else DEFAULT_LOG_LEVEL
    logger.setLevel(target_level)

    # Evitar agregar handlers si ya existen (Prevención de logs duplicados)
    if logger.hasHandlers():
        return logger

    # No propagar a loggers ancestros para mantener control total aquí
    logger.propagate = False

    # Formatter común
    formatter = logging.Formatter(
        fmt=DEFAULT_FORMAT,
        datefmt=DEFAULT_DATE_FORMAT
    )

    # --------------------------------------------------------------------------
    # 1. Handler de Archivo (Rotating File)
    # --------------------------------------------------------------------------
    try:
        # Asegurar que el directorio de logs existe
        log_path = Path(config.LOG_FILE_PATH)
        log_dir = log_path.parent
        
        if not log_dir.exists():
            log_dir.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            filename=str(log_path),
            mode='a',
            maxBytes=getattr(config, "LOG_MAX_BYTES", 5 * 1024 * 1024),
            backupCount=getattr(config, "LOG_BACKUP_COUNT", 5),
            encoding='utf-8',
            delay=False # Crear archivo inmediatamente
        )
        
        # [RED TEAM PATCH] Restricción estricta de permisos de lectura (CHMOD 600 equivalent)
        # En Windows, chmod restringe atributos de solo lectura, pero por seguridad general lo forzamos
        # para que solo el creador tenga control total, mitigando fuga de información (Local Info Disclosure).
        try:
            import stat
            os.chmod(str(log_path), stat.S_IREAD | stat.S_IWRITE)
        except Exception:
            pass # Falla silenciosa si no se soporta en el FS actual

        # [PERFORMANCE PATCH] Usar caché de RAM para evitar quemar el SSD
        memory_handler = logging.handlers.MemoryHandler(
            capacity=100, # Vacía al disco cada 100 mensajes...
            flushLevel=logging.ERROR, # ...o cuando hay un error inmediatamente
            target=file_handler
        )

        # En vez de añadir el file_handler directo, usamos la caché de RAM
        file_handler.setFormatter(formatter)
        file_handler.setLevel(target_level)
        memory_handler.setLevel(target_level)
        logger.addHandler(memory_handler)

    except (OSError, PermissionError) as e:
        # Fallback crítico: Si no podemos escribir en disco, avisamos en stderr
        # pero no detenemos la ejecución, permitiendo que el console handler funcione.
        sys.stderr.write(f"CRITICAL: Failed to setup file logging at {config.LOG_FILE_PATH}: {e}\n")

    # --------------------------------------------------------------------------
    # 2. Handler de Consola (Stream)
    # --------------------------------------------------------------------------
    # Esencial para desarrollo y diagnóstico rápido
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(target_level)
    logger.addHandler(stream_handler)

    return logger

# ==============================================================================
# BLOQUE DE PRUEBA (EJECUCIÓN DIRECTA)
# ==============================================================================
if __name__ == "__main__":
    # Prueba simple para verificar que el sistema funciona aisladamente
    test_log = setup_logger("TestLogger", logging.DEBUG)
    test_log.info("Sistema de logs inicializado correctamente.")
    test_log.debug("Este es un mensaje de depuración.")
    test_log.warning("Prueba de advertencia.")
    test_log.error("Prueba de error.")
    print(f"Log generado en: {config.LOG_FILE_PATH}")