# -*- coding: utf-8 -*-
"""
Módulo de Machine Learning Ligero (Reinforcement Learning & Self-Healing).
Actúa como el "Cerebro" de Nexpulse Agent, permitiendo mutar sus variables
en base al rendimiento empírico.
"""

import json
import threading
import os
import stat
from config import DATA_DIR

BRAIN_FILE = DATA_DIR / "ai_brain.json"

class CognitiveBrain:
    def __init__(self):
        self.lock = threading.Lock()
        self.state = {
            "cooldown_seconds": 60.0,
            "total_optimizations": 0,
            "avg_freed_mb": 0.0,
            "avg_time_sec": 0.0,
            "learning_rate": 0.1 # Alpha para el modelo Q-Learning Simplificado
        }
        self.load()

    def load(self):
        with self.lock:
            if BRAIN_FILE.exists():
                try:
                    with open(BRAIN_FILE, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # [PENTESTER PATCH] Type Checking & Bounds Validation (Prevención de JSON DoS)
                        if not isinstance(data.get("cooldown_seconds", 0.0), (int, float)): raise ValueError("Invalid Type")
                        if not isinstance(data.get("learning_rate", 0.0), (int, float)): raise ValueError("Invalid Type")
                        
                        # Forzar valores matemáticamente seguros
                        data["cooldown_seconds"] = max(5.0, min(3600.0, float(data.get("cooldown_seconds", 60.0))))
                        data["learning_rate"] = max(0.001, min(1.0, float(data.get("learning_rate", 0.1))))
                        
                        self.state.update(data)
                except Exception:
                    # Si falla o el JSON está corrupto/hackeado, se mantiene el estado inicial sano.
                    pass

    def save(self):
        with self.lock:
            try:
                with open(BRAIN_FILE, 'w', encoding='utf-8') as f:
                    json.dump(self.state, f, indent=4)
                    
                # [PENTESTER PATCH] Restricción de permisos (Database Jail)
                try:
                    os.chmod(str(BRAIN_FILE), stat.S_IREAD | stat.S_IWRITE)
                except Exception:
                    pass
            except Exception:
                pass

    def learn_from_execution(self, freed_mb: float, time_spent_sec: float) -> float:
        """
        Algoritmo de Reinforcement Learning y Self-Healing matemático.
        """
        self.state["total_optimizations"] += 1
        n = self.state["total_optimizations"]
        
        # Calcular medias móviles
        self.state["avg_freed_mb"] = ((n-1) * self.state["avg_freed_mb"] + freed_mb) / n
        self.state["avg_time_sec"] = ((n-1) * self.state["avg_time_sec"] + time_spent_sec) / n
        
        # --- SELF-HEALING (Castigo) ---
        # Si la optimización tarda mucho (> 1.5s) y libera poca RAM (< 10MB)
        # Significa que el algoritmo está lastimando el rendimiento de la PC (I/O Wait).
        if time_spent_sec > 1.5 and freed_mb < 10.0:
            # Relajarse (Aumentar Cooldown multiplicativamente)
            self.state["cooldown_seconds"] = min(300.0, self.state["cooldown_seconds"] * 1.5)
            self.state["learning_rate"] = max(0.01, self.state["learning_rate"] * 0.9)
            
        # --- REINFORCEMENT LEARNING (Recompensa) ---
        # Si la optimización es un éxito brutal (> 50MB en menos de 1s)
        elif freed_mb > 50.0 and time_spent_sec < 1.0:
            # Ser más agresivo (Bajar Cooldown usando el Alpha Learning Rate)
            target_cooldown = 15.0 # Mínimo teórico
            adjustment = self.state["learning_rate"] * (self.state["cooldown_seconds"] - target_cooldown)
            self.state["cooldown_seconds"] = max(15.0, self.state["cooldown_seconds"] - adjustment)
            
        self.save()
        return self.state["cooldown_seconds"]
