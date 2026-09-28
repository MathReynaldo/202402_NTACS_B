# -*- coding: utf-8 -*-
"""
Módulo Sentinel AI (IPS Interno).
Evalúa operaciones críticas del Agente Autónomo antes de que se ejecuten.
Actúa como un firewall interno (Multi-Agent System).
"""
import os
from typing import Dict, Any

from .logs_manager import setup_logger

logger = setup_logger("SentinelAI")

class SentinelAI:
    def __init__(self):
        # Procesos sagrados (Ring-0/System Core/UI) que JAMÁS deben ser tocados
        self.protected_processes = {
            "system", "registry", "smss.exe", "csrss.exe", "wininit.exe", 
            "services.exe", "lsass.exe", "svchost.exe", "explorer.exe", 
            "dwm.exe", "spoolsv.exe", "taskmgr.exe"
        }
        
        # Extensiones bloqueadas para borrado (evitar borrar ejecutables en TEMP)
        self.forbidden_extensions = {".exe", ".dll", ".sys", ".bat", ".vbs", ".cmd", ".ps1"}

    def evaluate_process_optimization(self, pid: int, name: str) -> bool:
        """
        Evalúa si es seguro intentar vaciar la RAM de un proceso.
        """
        # Regla 1: PID Crítico (System/Kernel)
        if pid <= 4:
            logger.warning(f"[SENTINEL] ACCESS DENIED: Intento de optimizar PID Kernel ({pid}).")
            return False
            
        # Regla 2: Nombre de proceso sagrado
        if name.lower() in self.protected_processes:
            logger.debug(f"[SENTINEL] OMITTED: Proceso protegido detectado ({name}).")
            return False
            
        # Es seguro
        return True

    def evaluate_file_deletion(self, file_path: str, safe_folder: str) -> bool:
        """
        Evalúa si es seguro borrar un archivo.
        """
        try:
            # Regla 1: Prevenir Path Traversal y Symlink deception
            if os.path.islink(file_path):
                logger.warning(f"[SENTINEL] ACCESS DENIED: Archivo es un Enlace Simbólico ({file_path}).")
                return False
                
            real_path = os.path.realpath(file_path)
            if not real_path.startswith(str(safe_folder)):
                logger.critical(f"[SENTINEL] IPS TRIGGERED: Intento de borrado fuera de jaula ({real_path}).")
                return False
                
            # Regla 2: Saneamiento y Evasión de Alternate Data Streams (ADS)
            file_name = os.path.basename(file_path).strip()
            if ":" in file_name:
                logger.warning(f"[SENTINEL] ACCESS DENIED: Flujo de datos NTFS malicioso detectado ({file_name}).")
                return False
                
            # Regla 3: Extensiones Peligrosas (Ejecutables)
            ext = os.path.splitext(file_name)[1].lower()
            if ext in self.forbidden_extensions:
                logger.info(f"[SENTINEL] ACCESS DENIED: Extensión ejecutable protegida ({ext}).")
                return False
                
            return True
        except Exception as e:
            logger.error(f"[SENTINEL] Error evaluando archivo {file_path}: {e}")
            return False
