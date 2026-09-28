# -*- coding: utf-8 -*-
"""
Módulo de configuración global para NEX-PULSE Agent.

Este archivo centraliza todas las constantes, rutas y parámetros de configuración
del sistema. Diseñado para ser importado por los módulos core, ui y ai.

Robustez:
- Soporte para variables de entorno (prefijo NEX_).
- Validación de tipos y rangos.
- Fallback automático para rutas críticas.

Autor: NEX-PULSE Team
Versión: 1.1.0 (Robust)
Target: Windows 10/11
Python: 3.10+
"""

import os
import sys
import logging
from pathlib import Path

# ==============================================================================
# HELPERS DE ROBUSTEZ (INTERNAL)
# ==============================================================================
def _get_env(key: str, default, cast_type=str):
    """
    Obtiene una variable de entorno de forma segura con casting de tipo.
    """
    value = os.getenv(f"NEX_{key}", default)
    try:
        if cast_type == bool:
            return str(value).lower() in ("true", "1", "yes", "on")
        return cast_type(value)
    except (ValueError, TypeError):
        sys.stderr.write(f"Warning: Invalid value for NEX_{key}. Using default: {default}\n")
        return default

def _resolve_path(path_str: str) -> Path:
    """
    Resuelve rutas expandiendo variables de entorno de Windows (%VAR%).
    """
    try:
        expanded = os.path.expandvars(path_str)
        return Path(expanded).resolve()
    except Exception as e:
        sys.stderr.write(f"Error resolving path {path_str}: {e}\n")
        return Path(path_str)

# ==============================================================================
# INFORMACIÓN DE LA APLICACIÓN
# ==============================================================================
APP_NAME = "NEX-PULSE Agent"
APP_VERSION = "1.1.0"
APP_AUTHOR = "Cristian Lucas"
APP_ID = "nex_pulse_agent_v1"

# ==============================================================================
# RUTAS DEL SISTEMA (PATH CONFIGURATION)
# ==============================================================================
if getattr(sys, 'frozen', False):
    ROOT_DIR = Path(sys.executable).parent
else:
    ROOT_DIR = Path(__file__).resolve().parent

# Configuración de directorios con soporte para override
LOGS_DIR_NAME = _get_env("LOGS_DIR", "logs")
ASSETS_DIR_NAME = _get_env("ASSETS_DIR", "assets")
DATA_DIR_NAME = _get_env("DATA_DIR", "data")

LOGS_DIR = ROOT_DIR / LOGS_DIR_NAME
ASSETS_DIR = ROOT_DIR / ASSETS_DIR_NAME
DATA_DIR = ROOT_DIR / DATA_DIR_NAME

# Inicialización robusta de directorios
critical_dirs = {"Logs": LOGS_DIR, "Data": DATA_DIR}

for name, path in critical_dirs.items():
    # [PENTESTER PATCH] Path Hijacking Prevention (Directory Jail)
    try:
        real_path = path.resolve()
        real_root = ROOT_DIR.resolve()
        # Verificamos que el path resuelto no escape del directorio base
        if not str(real_path).startswith(str(real_root)):
            sys.stderr.write(f"SECURITY ALERT: Intent de Path Hijacking detectado en {name}. Bloqueado.\n")
            path = real_root / name.lower() # Forzamos a la ruta segura local
    except Exception:
        path = ROOT_DIR / name.lower()

    try:
        path.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        # Fallback a directorio temporal local si falla la escritura en ROOT_DIR
        fallback = Path(os.getenv('LOCALAPPDATA', os.getenv('TEMP'))) / APP_ID / name.lower()
        sys.stderr.write(f"Warning: Permission denied for {path}. Falling back to {fallback}\n")
        try:
            fallback.mkdir(parents=True, exist_ok=True)
            # Actualizamos la referencia global
            if name == "Logs": LOGS_DIR = fallback
            if name == "Data": DATA_DIR = fallback
        except Exception as e:
            sys.stderr.write(f"Critical: Could not create fallback directory for {name}: {e}\n")

# ==============================================================================
# CONFIGURACIÓN DE LOGS (LOGGING)
# ==============================================================================
# Mapeo seguro de nivel de log desde string
_LOG_LEVEL_STR = _get_env("LOG_LEVEL", "INFO").upper()
LOG_LEVEL = getattr(logging, _LOG_LEVEL_STR, logging.INFO)

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

LOG_MAX_BYTES = _get_env("LOG_MAX_BYTES", 5 * 1024 * 1024, int)
LOG_BACKUP_COUNT = _get_env("LOG_BACKUP_COUNT", 5, int)
LOG_FILENAME = "nexpulse.log"
LOG_FILE_PATH = LOGS_DIR / LOG_FILENAME

# ==============================================================================
# CONFIGURACIÓN DE MONITOREO (SYSTEM MONITORING)
# ==============================================================================
CPU_THRESHOLD_PERCENT = _get_env("CPU_LIMIT", 85.0, float)
RAM_THRESHOLD_PERCENT = _get_env("RAM_LIMIT", 80.0, float)
DISK_THRESHOLD_PERCENT = _get_env("DISK_LIMIT", 90.0, float)

MONITORING_INTERVAL = _get_env("MONITOR_INTERVAL", 2.0, float)

# ==============================================================================
# CONFIGURACIÓN DE LIMPIEZA (SYSTEM CLEANING)
# ==============================================================================
AUTO_CLEAN_ENABLED = _get_env("AUTO_CLEAN", True, bool)
CLEAN_INTERVAL_MINUTES = _get_env("CLEAN_INTERVAL", 60, int)

# Rutas del sistema resueltas dinámicamente
SYSTEM_TEMP = _resolve_path(r"%TEMP%")
WINDOWS_TEMP = _resolve_path(r"%WINDIR%\Temp")
PREFETCH_DIR = _resolve_path(r"%WINDIR%\Prefetch")

SAFE_FOLDERS_TO_CLEAN = [
    SYSTEM_TEMP,
    WINDOWS_TEMP,
    # Añadir validación extra: solo limpiar si la ruta existe y es directorio
]

TEMP_FILE_EXTENSIONS = [
    ".tmp", ".log", ".bak", ".old", ".gid", ".chk", ".dmp", ".wbk", ".fts"
]

# ==============================================================================
# CONFIGURACIÓN DE VOZ Y NOTIFICACIONES (UI & VOICE)
# ==============================================================================
VOICE_ENABLED = _get_env("VOICE_ENABLED", True, bool)
VOICE_LANGUAGE = _get_env("VOICE_LANG", "es-ES")
VOICE_RATE = _get_env("VOICE_RATE", 150, int)
DEFAULT_VOLUME = _get_env("VOLUME", 0.8, float)

NOTIFICATIONS_ENABLED = _get_env("NOTIFICATIONS", True, bool)
NOTIFICATION_DURATION = _get_env("NOTIF_DURATION", 5, int)

# ==============================================================================
# UTILIDADES DE VALIDACIÓN Y DEBUG
# ==============================================================================
def validate_config():
    """
    Verifica la integridad lógica de la configuración.
    Lanza advertencias si encuentra valores fuera de rango.
    """
    global SAFE_FOLDERS_TO_CLEAN
    issues = []
    
    # Validar rangos de monitoreo
    if not (0 <= CPU_THRESHOLD_PERCENT <= 100):
        issues.append(f"CPU_THRESHOLD_PERCENT invalid ({CPU_THRESHOLD_PERCENT}), must be 0-100.")
    if not (0 <= RAM_THRESHOLD_PERCENT <= 100):
        issues.append(f"RAM_THRESHOLD_PERCENT invalid ({RAM_THRESHOLD_PERCENT}), must be 0-100.")
    
    # Validar rutas de limpieza
    valid_folders = []
    for folder in SAFE_FOLDERS_TO_CLEAN:
        if folder.exists() and folder.is_dir():
            valid_folders.append(folder)
        else:
            # No es un error crítico, pero se debe notar
            logging.warning(f"Config Warning: Cleanup folder not found or invalid: {folder}")
    
    # Actualizar la lista con solo carpetas válidas existentes para evitar errores en runtime
    # Nota: Modificar una global aquí es intencional para saneamiento
    SAFE_FOLDERS_TO_CLEAN[:] = valid_folders

    if issues:
        for issue in issues:
            sys.stderr.write(f"[CONFIG ERROR] {issue}\n")
        return False
    return True

def print_config():
    """
    Imprime la configuración actual.
    """
    print(f"\n--- {APP_NAME} v{APP_VERSION} CONFIGURATION (Robust Mode) ---")
    g = globals()
    for key in sorted(g.keys()):
        if key.isupper() and not key.startswith("_"):
            value = g[key]
            print(f"{key:<25}: {value}")
    print("-" * 60 + "\n")

if __name__ == "__main__":
    # Al ejecutar directamente, validamos y mostramos
    is_valid = validate_config()
    print_config()
    if not is_valid:
        print("!!! CONFIGURATION  ERRORS !!!")
        sys.exit(1)