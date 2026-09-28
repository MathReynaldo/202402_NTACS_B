# -*- coding: utf-8 -*-
"""
Punto de entrada principal para NEX-PULSE Agent.

Orquesta la configuración, logs, verificación de permisos y 
el bucle de monitoreo principal del sistema.

Autor: NEX-PULSE Team
Versión: 1.0.0
"""

import time
import sys
import os
import threading
import psutil
import config
from config import validate_config
from core import logs_manager
from core import permissions
from core import system_monitor
from core.autonomous_agent import NexpulseAgent

def agent_worker(ai_agent, logger):
    logger.info(f"Iniciando ciclo de monitoreo IA en background (Intervalo: {config.MONITORING_INTERVAL}s)...")
    while True:
        try:
            metrics = system_monitor.get_system_summary()
            top_procs = system_monitor.get_top_processes(limit=15, sort_by='memory')
            ai_status = ai_agent.think_and_act(metrics, top_procs)
            # Solo guardamos un log debug para no saturar si hay UI
            logger.debug(f"[AI] {ai_status}")
        except Exception as e:
            logger.error(f"Fallo critico en hilo IA: {e}")
        time.sleep(config.MONITORING_INTERVAL)

def apply_hardware_optimizations(logger):
    """Ajusta dinámicamente el rendimiento basado en el hardware local (Rendimiento Extremo)."""
    try:
        # Bajar prioridad del proceso para evitar impacto al usuario
        p = psutil.Process(os.getpid())
        if hasattr(psutil, 'BELOW_NORMAL_PRIORITY_CLASS'):
            p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
            logger.info("[PERFORMANCE] Prioridad del proceso bajada a Background (BELOW_NORMAL).")
        
        # Detección de HW
        cores = psutil.cpu_count(logical=True)
        ram_gb = psutil.virtual_memory().total / (1024**3)
        
        if cores <= 2 or ram_gb <= 4:
            # Low end PC
            config.MONITORING_INTERVAL = max(5.0, config.MONITORING_INTERVAL)
            logger.info(f"[PERFORMANCE] Low-End PC ({cores} Cores, {ram_gb:.1f}GB RAM). Intervalo auto-ajustado a {config.MONITORING_INTERVAL}s.")
        else:
            logger.info(f"[PERFORMANCE] High-End PC ({cores} Cores, {ram_gb:.1f}GB RAM). Modo rendimiento máximo.")
    except Exception as e:
        logger.error(f"[PERFORMANCE] Fallo al aplicar optimizaciones de SO: {e}")

def main():
    # 1. Configurar Logger Principal
    logger = logs_manager.setup_logger("Main")
    logger.info("Iniciando NEX-PULSE Agent...")

    # 2. Validación de Configuración y Hardening
    if not validate_config():
        logger.error("Fallo la validacion de configuracion inicial.")
        sys.exit(1)

    # 3. Verificación de Seguridad y Permisos
    if not permissions.is_admin():
        logger.warning("Privilegios insuficientes. Solicitando elevacion UAC para Hardening...")
        try:
            permissions.relaunch_as_admin()
        except Exception as e:
            logger.error(f"Fallo en elevacion de privilegios: {e}")
        sys.exit(0)
    
    logger.info("Privilegios de Administrador verificados (OK).")
    
    # 3.5. Aplicar optimizaciones extremas de Hardware y SO
    apply_hardware_optimizations(logger)

    logger.info("NEX-PULSE Core inicializado correctamente.")

    # 4. Iniciar Agente Autónomo (Background)
    ai_agent = NexpulseAgent()
    agent_thread = threading.Thread(target=agent_worker, args=(ai_agent, logger), daemon=True)
    agent_thread.start()

    # 5. Iniciar Interfaz Gráfica CustomTkinter (Main Thread)
    try:
        from ui.app_window import NexpulseUI
        app = NexpulseUI(ai_agent)
        app.run()
    except KeyboardInterrupt:
        logger.info("Detenido por el usuario.")
    except Exception as e:
        logger.critical(f"Fallo critico en UI: {e}", exc_info=True)
    finally:
        logger.info("NEX-PULSE Agent detenido limpiamente.")

if __name__ == "__main__":
    main()
