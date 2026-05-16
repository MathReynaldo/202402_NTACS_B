# -*- coding: utf-8 -*-
"""
Interfaz Gráfica Moderna (GUI) para NEX-PULSE Agent V2
Tecnología: CustomTkinter + PyStray (System Tray)
Estética: Mr. Robot / E-Corp (Dark Premium)
"""

import threading
import time
import os
import subprocess
import customtkinter as ctk
from PIL import Image
import pystray
from pystray import MenuItem as item

from core.system_monitor import get_system_summary
from core.autonomous_agent import NexpulseAgent
from core.logs_manager import setup_logger

logger = setup_logger("NexpulseUI")

# Paleta Corporativa E-Corp
BG_COLOR = "#1E222D"
ACCENT_COLOR = "#00A8E8"
TEXT_COLOR = "#E2E8F0"

class NexpulseUI:
    def __init__(self, agent_instance):
        self.agent = agent_instance
        self.is_running = True
        
        # Configuración ventana principal
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("NEX-PULSE AI - Security & Optimization")
        self.root.geometry("600x450")
        self.root.configure(fg_color=BG_COLOR)
        
        # Interceptar el botón de cerrar (X)
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        
        self._build_ui()
        self.tray_icon = None

    def _build_ui(self):
        """Construye los widgets de la interfaz."""
        # Título
        self.title_lbl = ctk.CTkLabel(
            self.root, 
            text="NEX-PULSE NETGUARD", 
            font=("Segoe UI Variable", 24, "bold"), 
            text_color=ACCENT_COLOR
        )
        self.title_lbl.pack(pady=(20, 10))

        # Status
        self.status_lbl = ctk.CTkLabel(
            self.root, 
            text="Status: Initializing AI Core...", 
            font=("Segoe UI Variable", 14), 
            text_color=TEXT_COLOR
        )
        self.status_lbl.pack(pady=5)

        # Frame de Gráficas
        self.metrics_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.metrics_frame.pack(pady=20, fill="x", padx=40)

        # CPU
        ctk.CTkLabel(self.metrics_frame, text="CPU Pulse", font=("Segoe UI Variable", 12)).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.cpu_bar = ctk.CTkProgressBar(self.metrics_frame, progress_color=ACCENT_COLOR, width=300)
        self.cpu_bar.grid(row=0, column=1, padx=10, pady=5)
        self.cpu_bar.set(0)

        # RAM
        ctk.CTkLabel(self.metrics_frame, text="RAM Allocation", font=("Segoe UI Variable", 12)).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.ram_bar = ctk.CTkProgressBar(self.metrics_frame, progress_color="#FF3366", width=300) # Rojo corporativo advertencia
        self.ram_bar.grid(row=1, column=1, padx=10, pady=5)
        self.ram_bar.set(0)

        # Network
        self.net_lbl = ctk.CTkLabel(
            self.root, 
            text="NetGuard: 0 KB/s \u2191 | 0 KB/s \u2193", 
            font=("Segoe UI Variable", 12, "italic"), 
            text_color="#A0AEC0"
        )
        self.net_lbl.pack(pady=10)

        # Botones de Acción (Smart Optimizer)
        self.btn_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.btn_frame.pack(pady=20)

        self.btn_flush = ctk.CTkButton(
            self.btn_frame, 
            text="Flush DNS & Net Cache", 
            command=self.flush_dns,
            fg_color=BG_COLOR,
            border_width=1,
            border_color=ACCENT_COLOR,
            hover_color="#14374A"
        )
        self.btn_flush.grid(row=0, column=0, padx=10)

        self.btn_opt = ctk.CTkButton(
            self.btn_frame, 
            text="Force AI Optimization", 
            command=self.force_optimization,
            fg_color=ACCENT_COLOR,
            hover_color="#0086B3"
        )
        self.btn_opt.grid(row=0, column=1, padx=10)

        # Switch de Control de IA (Kill Switch)
        self.ai_switch_var = ctk.StringVar(value="on")
        self.ai_switch = ctk.CTkSwitch(
            self.btn_frame, 
            text="AI Core: ON", 
            command=self.toggle_ai_core,
            variable=self.ai_switch_var, 
            onvalue="on", 
            offvalue="off",
            progress_color=ACCENT_COLOR,
            text_color=TEXT_COLOR
        )
        self.ai_switch.grid(row=0, column=2, padx=10)

    def toggle_ai_core(self):
        """Activa o Desactiva el motor autónomo de la IA"""
        if self.ai_switch_var.get() == "on":
            self.agent.is_active = True
            self.ai_switch.configure(text="AI Core: ON")
            self.status_lbl.configure(text="Status: AI Core Resumed.", text_color=TEXT_COLOR)
        else:
            self.agent.is_active = False
            self.ai_switch.configure(text="AI Core: OFF")
            self.status_lbl.configure(text="Status: AI Core Suspended.", text_color="#FF3366")

    def flush_dns(self):
        """Ejecuta el Flush DNS de forma segura (Tamper-Proof)"""
        self.status_lbl.configure(text="Status: Executing DNS Flush...")
        try:
            # [SECURITY PATCH] Evitar Binary Hijacking usando ruta absoluta absoluta
            system32 = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'System32')
            ipconfig_path = os.path.join(system32, 'ipconfig.exe')
            
            # Uso seguro de subprocess, sin shell=True, con timeout estricto
            subprocess.run([ipconfig_path, "/flushdns"], check=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=5)
            self.status_lbl.configure(text="Status: DNS Cache Purged Successfully.", text_color="#00FF9D")
        except subprocess.TimeoutExpired:
            logger.error("DNS Flush Timeout!")
            self.status_lbl.configure(text="Status: DNS Flush Timeout (Safe Abort).", text_color="#FF3366")
        except Exception as e:
            logger.error(f"Failed to flush DNS: {e}")
            self.status_lbl.configure(text="Status: DNS Flush Failed (Rollback).", text_color="#FF3366")

    def force_optimization(self):
        """Fuerza al agente a ejecutar el Nivel 2"""
        self.status_lbl.configure(text="Status: Forcing Memory Optimization...")
        # Simular salto de salud para disparar la IA en el próximo ciclo
        self.agent.current_health = 0.0

    def update_ui_loop(self):
        """Bucle para actualizar la UI desde los datos del agente"""
        if not self.is_running:
            return

        try:
            metrics = get_system_summary()
            
            # Actualizar barras
            cpu_val = metrics['cpu']['usage_percent'] / 100.0
            ram_val = metrics['memory']['percent'] / 100.0
            self.cpu_bar.set(cpu_val)
            self.ram_bar.set(ram_val)

            # Color dinámico RAM
            self.ram_bar.configure(progress_color="#FF3366" if ram_val > 0.8 else ACCENT_COLOR)

            # Actualizar Red
            sent_kb = metrics['network']['bytes_sent_sec'] / 1024
            recv_kb = metrics['network']['bytes_recv_sec'] / 1024
            self.net_lbl.configure(text=f"NetGuard: {sent_kb:.1f} KB/s \u2191 | {recv_kb:.1f} KB/s \u2193")

            # Actualizar Estado General (Salud del AI)
            health = self.agent.current_health
            estado = "Secure & Stable" if health > 80 else "Optimizing Resources"
            
            # [SECURITY WATCHDOG] Verificar si el hilo de la IA ha muerto
            if time.time() - getattr(self.agent, 'last_heartbeat', 0) > 15:
                self.status_lbl.configure(text="CRITICAL: AI CORE UNRESPONSIVE", text_color="#FF3366")
            else:
                self.status_lbl.configure(text=f"AI Status: {estado} ({health:.1f}%)", text_color=TEXT_COLOR if health > 80 else ACCENT_COLOR)
            
        except Exception as e:
            logger.error(f"UI Update error: {e}")

        # Programar siguiente actualización en 1000ms
        self.root.after(1000, self.update_ui_loop)

    # --- TRAY ICON LOGIC ---
    def quit_window(self, icon, item):
        """Cierra el programa por completo de forma segura"""
        self.is_running = False
        icon.stop()
        self.root.destroy()
        os._exit(0) # Forzar cierre de todos los hilos por seguridad

    def show_window(self, icon, item):
        """Restaura la ventana desde el Tray"""
        icon.stop()
        self.root.after(0, self.root.deiconify)

    def force_opt_tray(self, icon, item):
        self.force_optimization()

    def hide_window(self):
        """Oculta la ventana y crea el ícono en el Tray"""
        self.root.withdraw()
        
        # Crear icono negro genérico con PIL para no depender de archivos externos
        image = Image.new('RGB', (64, 64), color = (0, 168, 232))
        
        menu = pystray.Menu(
            item('Open Dashboard', self.show_window, default=True),
            item('Force AI Optimization', self.force_opt_tray),
            item('Exit Nexpulse', self.quit_window)
        )
        
        self.tray_icon = pystray.Icon("Nexpulse", image, "NEX-PULSE Agent", menu)
        # Iniciar tray icon en un hilo separado para no bloquear
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def run(self):
        """Inicia el Main Loop de la UI"""
        self.root.after(1000, self.update_ui_loop)
        self.root.mainloop()
