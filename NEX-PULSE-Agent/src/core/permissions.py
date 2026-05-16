# -*- coding: utf-8 -*-
"""
Módulo de gestión de permisos y privilegios para NEX-PULSE Agent.

Este módulo encapsula la lógica necesaria para verificar y solicitar elevación
de privilegios (UAC) en entornos Windows. Es crítico para operaciones de
limpieza de sistema y acceso a directorios protegidos.

Funcionalidades:
- Verificación de estado de administrador.
- Reinicio de la aplicación con solicitud de elevación (UAC).
- Compatibilidad transparente entre modo script (.py) y congelado (.exe).

Autor: NEX-PULSE Team
Versión: 1.0.0
Target: Windows 10/11
"""

import sys
import os
import ctypes
import subprocess
from typing import List

# Intentamos importar el logger, si falla usamos print (fallback seguro)
try:
    from .logs_manager import setup_logger
    logger = setup_logger("Permissions")
except (ImportError, ValueError):
    import logging
    logger = logging.getLogger("Permissions")

def is_admin() -> bool:
    """
    Verifica si el proceso actual tiene privilegios de administrador.

    Utiliza la API de Windows shell32.IsUserAnAdmin a través de ctypes.
    
    Returns:
        bool: True si el proceso tiene privilegios elevados, False en caso contrario.
    """
    try:
        # En Windows, IsUserAnAdmin devuelve 1 si es admin, 0 si no.
        # En sistemas no Windows, esto fallará, por lo que capturamos la excepción.
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except AttributeError:
        # Si no estamos en Windows o falta la DLL
        logger.warning("Verificación de admin fallida: No es un sistema Windows compatible.")
        return False
    except Exception as e:
        logger.error(f"Error inesperado verificando privilegios: {e}")
        return False

def relaunch_as_admin(args: List[str] = None) -> None:
    """
    Reinicia la aplicación actual solicitando elevación de privilegios (UAC).
    
    Si el usuario acepta el prompt de UAC, se lanzará una nueva instancia
    del proceso con permisos de administrador y la actual se cerrará.
    
    Soporta:
    - Ejecución directa de script (python.exe script.py)
    - Ejecutales congelados con PyInstaller (app.exe)

    Args:
        args (List[str], optional): Argumentos adicionales para pasar al nuevo proceso.
                                    Si es None, usa sys.argv[1:].
    """
    if is_admin():
        logger.info("Intento de elevación innecesario: Ya es administrador.")
        return

    # Preparar argumentos
    # [PENTESTER PATCH] Prevención LPE (Inyección de Argumentos al Kernel)
    # Ignoramos completamente argumentos externos al escalar privilegios.
    args = []
    
    # Convertir lista de argumentos a cadena segura para línea de comandos
    cmd_args = ""

    logger.info("Solicitando elevación de privilegios (UAC)...")

    try:
        if getattr(sys, 'frozen', False):
            # Caso 1: Ejecutable congelado (PyInstaller)
            # sys.executable apunta al .exe
            executable = sys.executable
            params = cmd_args
        else:
            # Caso 2: Script de Python (.py)
            # sys.executable apunta al intérprete python.exe
            # sys.argv[0] es la ruta del script
            executable = sys.executable
            # Reconstruimos el comando: "script.py" arg1 arg2 ...
            script_path = f'"{sys.argv[0]}"'
            params = f'{script_path} {cmd_args}'

        # ShellExecuteW con verbo 'runas' desencadena el prompt de UAC
        # Hinstance > 32 indica éxito
        ret = ctypes.windll.shell32.ShellExecuteW(
            None,           # Hwnd (None = sin ventana padre)
            "runas",        # Verbo operación (runas = Admin)
            executable,     # Programa a ejecutar
            params,         # Parámetros
            None,           # Directorio de trabajo (None = actual)
            1               # SW_SHOWNORMAL (Mostrar ventana normalmente)
        )
        
        # Códigos de error comunes de ShellExecute:
        # 0: Out of memory resources
        # 2: File not found
        # 5: Access denied (Usuario rechazó UAC)
        if int(ret) <= 32:
            raise OSError(f"ShellExecute falló con código: {ret}")
            
        # Si tuvo éxito, terminamos el proceso actual sin privilegios
        sys.exit(0)

    except OSError as e:
        logger.warning(f"Elevación cancelada o fallida: {e}")
        # No salimos aquí, permitimos al llamador decidir qué hacer si falla la elevación
        # (por ejemplo, continuar con funcionalidad limitada)

# ==============================================================================
# BLOQUE DE PRUEBA (EJECUCIÓN DIRECTA)
# ==============================================================================
if __name__ == "__main__":
    # Prueba simple de la funcionalidad
    print(f"PID Actual: {os.getpid()}")
    
    if is_admin():
        print("[OK] El script se está ejecutando COMO ADMINISTRADOR.")
        # Aquí iría la lógica que requiere permisos
        input("Presione ENTER para salir...")
    else:
        print("[INFO] El script se está ejecutando SIN permisos de administrador.")
        print("Intentando relanzar...")
        
        # Intentamos relanzar. Si el usuario dice "Sí" al UAC, se abrirá una nueva ventana.
        relaunch_as_admin()
        
        print("[ERROR] Si ves esto, el usuario rechazó el UAC o hubo un error.")
        input("Presione ENTER para salir...")