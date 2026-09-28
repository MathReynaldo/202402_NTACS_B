# -*- coding: utf-8 -*-
"""
Inteligencia Autónoma de NEX-PULSE Agent.

Analiza las métricas en tiempo real, determina el estado de salud del sistema
y ejecuta acciones de optimización proactivas sin matar procesos de usuario.
"""
import time
import collections
import statistics
import os
import shutil
import ctypes
import psutil
import gc

from .logs_manager import setup_logger
from .ai_brain import CognitiveBrain
from .sentinel_ai import SentinelAI
from config import SAFE_FOLDERS_TO_CLEAN, TEMP_FILE_EXTENSIONS

logger = setup_logger("AutonomousAI")

class NexpulseAgent:
    def __init__(self, history_size=30):
        # Usamos deque para mantener un registro histórico (ventana móvil)
        self.cpu_history = collections.deque(maxlen=history_size)
        self.ram_history = collections.deque(maxlen=history_size)
        self.current_health = 100.0
        self.last_clean_time = 0
        # [MACHINE LEARNING] Cargamos el Cerebro en lugar de reglas estáticas
        self.brain = CognitiveBrain()
        # [SECURITY] Cargamos la IA Centinela
        self.sentinel = SentinelAI()
        
        self.is_active = True # Control manual de la IA
        self.last_heartbeat = time.time() # [SECURITY] Monitor de vida del hilo

    def think_and_act(self, metrics, top_processes):
        """
        Ciclo principal de toma de decisiones.
        """
        if not getattr(self, 'is_active', True):
            self.last_heartbeat = time.time() # Mantenemos el pulso aunque esté en pausa
            return "AI Core: SUSPENDIDO (Pausa Manual)"
        
        self.last_heartbeat = time.time() # [SECURITY] Latido activo

        cpu = metrics['cpu']['usage_percent']
        ram = metrics['memory']['percent']
        
        self.cpu_history.append(cpu)
        self.ram_history.append(ram)

        if len(self.cpu_history) < 10:
            return "Calibrando sensores de IA..."

        # Calcular medias móviles
        cpu_avg = statistics.mean(self.cpu_history)
        ram_avg = statistics.mean(self.ram_history)

        # Penalizaciones de salud más agresivas para reaccionar rápido
        cpu_penalty = max(0, cpu_avg - 50) * 0.8
        ram_penalty = max(0, ram_avg - 70) * 1.5
        self.current_health = max(0.0, min(100.0, 100.0 - (cpu_penalty + ram_penalty)))

        now = time.time()
        
        # Decidir acciones basadas en la salud leída del Cerebro (Contexto Dinámico)
        if self.current_health < 85.0 and (now - self.last_clean_time) > self.brain.state["cooldown_seconds"]:
            logger.warning(f"¡Estrés detectado! (Salud Sistema: {self.current_health:.1f}%). Iniciando Optimizador...")
            
            start_time = time.time()
            freed_mb = self._execute_optimization(top_processes)
            end_time = time.time()
            
            # [MACHINE LEARNING] Bucle de Retroalimentación (Feedback Loop)
            new_cooldown = self.brain.learn_from_execution(freed_mb, end_time - start_time)
            logger.info(f"[ML-CORE] Memoria actualizada. Nuevo Cooldown Inteligente: {new_cooldown:.1f}s")
            
            self.last_clean_time = now
            
            # [PERFORMANCE PATCH] Autocompactación de Memoria.
            # Forzamos a Python a destruir cualquier variable residual para no consumir RAM innecesaria.
            gc.collect()
            
            return "Optimización Ejecutada"
            
        return f"Sistema Estable ({self.current_health:.1f}%)"

    def _execute_optimization(self, top_processes):
        """Ejecuta los algoritmos de limpieza sin destruir procesos de usuario."""
        # Calculamos la RAM exacta antes de limpiar para el Machine Learning
        ram_before = psutil.virtual_memory().used
        
        self._optimize_memory(top_processes)
        self._clean_temp_files()
        
        # Validamos el peso liberado para la recompensa (Reward) del ML
        ram_after = psutil.virtual_memory().used
        freed_mb = max(0.0, (ram_before - ram_after) / (1024 * 1024))
        return freed_mb

    def _optimize_memory(self, top_processes):
        """
        Inteligencia: En lugar de matar el programa (Chrome, juegos), le ordenamos al SO
        que descargue la memoria inactiva (EmptyWorkingSet) del proceso.
        """
        logger.info("[NEX-AI] Ejecutando compresión de memoria profunda...")
        optimized_count = 0

        try:
            # Acceso a la API de Windows
            psapi = ctypes.WinDLL('psapi')
            kernel32 = ctypes.WinDLL('kernel32')
            PROCESS_SET_QUOTA = 0x0100
            
            # [PENTESTER PATCH] Saneamiento de punteros de 64-bits
            # Previene corrupciones de memoria y fugas de Handles en sistemas x64.
            try:
                kernel32.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_bool, ctypes.c_uint32]
                kernel32.OpenProcess.restype = ctypes.c_void_p
                kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
                kernel32.CloseHandle.restype = ctypes.c_bool
                psapi.EmptyWorkingSet.argtypes = [ctypes.c_void_p]
                psapi.EmptyWorkingSet.restype = ctypes.c_bool
            except Exception as e:
                logger.error(f"[MEMORY] Fallo al establecer tipos C: {e}")

            for p in top_processes:
                pid = p['pid']
                name = str(p.get('name', 'unknown')).lower()
                
                # [SENTINEL AI INTERCEPTION]
                if not self.sentinel.evaluate_process_optimization(pid, name):
                    continue
                
                # [RED TEAM PATCH] Ignorar procesos del kernel y sistema. El PID 0 es System Idle, PID 4 es System.
                if pid <= 4 or name in ["system", "registry", "smss.exe", "csrss.exe", "wininit.exe", "services.exe", "lsass.exe", "svchost.exe"]:
                    continue

                try:
                    # Abrir proceso con permisos para modificar cuota de memoria
                    h_process = kernel32.OpenProcess(PROCESS_SET_QUOTA, False, pid)
                    if h_process:
                        try:
                            # Forzar a Windows a recuperar las páginas de memoria no usadas de la app
                            result = psapi.EmptyWorkingSet(h_process)
                            if result:
                                optimized_count += 1
                        finally:
                            kernel32.CloseHandle(h_process)
                except Exception:
                    pass # Ignorar si está protegido por el sistema
                    
            logger.info(f"[NEX-AI] Memoria de {optimized_count} aplicaciones purgada y recuperada exitosamente.")
        except Exception as e:
            logger.error(f"[NEX-AI] Fallo al inyectar API de Windows: {e}")

    def _clean_temp_files(self):
        """
        Inteligencia: Borra basura del disco de forma dinámica. Ignora bloqueos de SO.
        """
        logger.info("[NEX-AI] Escaneando e incinerando caché y archivos residuales...")
        bytes_freed = 0
        deleted_files = 0

        for folder in SAFE_FOLDERS_TO_CLEAN:
            if not folder.exists() or not folder.is_dir():
                continue
                
            for root, dirs, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        # [SENTINEL AI INTERCEPTION]
                        if not self.sentinel.evaluate_file_deletion(file_path, str(folder)):
                            continue

                        size = os.path.getsize(file_path)
                        os.remove(file_path) # Intento agresivo
                        bytes_freed += size
                        deleted_files += 1
                    except (PermissionError, FileNotFoundError, OSError):
                        # Inteligencia: Si falla, es porque la app activa lo está usando. Lo dejamos en paz.
                        pass
                        
        mb_freed = bytes_freed / (1024 * 1024)
        if deleted_files > 0:
            logger.info(f"[NEX-AI] Incineración de disco completada: {deleted_files} archivos ({mb_freed:.2f} MB liberados).")
        else:
            logger.info("[NEX-AI] Disco en estado óptimo. Sin basura residual.")
