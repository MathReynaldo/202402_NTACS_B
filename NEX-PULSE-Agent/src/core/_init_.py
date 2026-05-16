# -*- coding: utf-8 -*-
"""
Paquete Core de NEX-PULSE Agent.

Este paquete contiene la lógica de negocio central de la aplicación,
incluyendo monitoreo del sistema, gestión de logs y verificación de permisos.

Módulos expuestos:
- system_monitor: Funcionalidades de monitoreo de hardware.
- logs_manager: Configuración y gestión de rotación de logs.
- permissions: Utilidades para manejo de privilegios en Windows.
"""

# Definición de exportaciones públicas
__all__ = [
    # Módulos
    "system_monitor",
    "logs_manager",
    "permissions",
    
    # Clases y funciones principales (Alias de conveniencia)
    "SystemMonitor",
    "LogManager",
    "check_admin_privileges",
]

# ------------------------------------------------------------------------------
# Importaciones relativas seguras
# ------------------------------------------------------------------------------
# Usamos try-except para permitir importar el paquete incluso si algún módulo
# individual tiene dependencias faltantes (útil para tests o entornos parciales).
# En producción, estos módulos deberían existir.

try:
    from . import system_monitor
    # Se asume que existe una clase principal SystemMonitor en system_monitor.py
    # Si no existe, se puede acceder vía core.system_monitor.SystemMonitor
    from .system_monitor import SystemMonitor
except ImportError:
    system_monitor = None
    SystemMonitor = None

try:
    from . import logs_manager
    from .logs_manager import LogManager
except ImportError:
    logs_manager = None
    LogManager = None

try:
    from . import permissions
    from .permissions import check_admin_privileges
except ImportError:
    permissions = None
    check_admin_privileges = None

# Metadatos del paquete
__version__ = "1.0.0"
__author__ = "NEX-PULSE Team"