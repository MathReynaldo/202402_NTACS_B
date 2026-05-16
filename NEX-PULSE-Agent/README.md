# NEX-PULSE Agent 🧠🚀

**Creado y Desarrollado por Cristian Lucas**

[![Security: Zero Vulnerabilities](https://img.shields.io/badge/Security-Zero%_Vulnerabilities-success.svg)](https://github.com/)
[![Architecture: Multi-Agent](https://img.shields.io/badge/Architecture-Multi--Agent-purple.svg)](https://github.com/)
[![OS: Windows 10/11](https://img.shields.io/badge/OS-Windows-blue.svg)](https://github.com/)

**NEX-PULSE Agent** es un software autónomo de optimización de grado militar para entornos Windows. Diseñado para funcionar como un "Fantasma" en tu sistema, libera memoria RAM inactiva, limpia archivos residuales y protege tu computadora de forma pasiva, todo mientras se ajusta dinámicamente a tu hardware y hábitos de uso mediante aprendizaje automático local.

---

## 🏗️ Arquitectura Multi-Agente (Simbiosis AI)

El núcleo de Nexpulse opera sobre una revolucionaria arquitectura de Inteligencia Artificial Dual:

1. **El Optimizador (Nexpulse AI):** La inteligencia proactiva. Escanea el sistema, interactúa con la API profunda de Windows (`kernel32`) y ejecuta compresiones en la memoria RAM y limpiezas de disco sin matar o interferir con las aplicaciones del usuario (Juegos, Editores, etc).
2. **El Guardián (Sentinel AI):** Un *Intrusion Prevention System* (IPS) interno basado en reglas "Zero-Trust" (Cero Confianza). Antes de que el Optimizador realice cualquier inyección en memoria o eliminación de archivos, el Centinela intercepta la petición, verifica Flujos Ocultos NTFS, protege procesos de Ring-0 (Kernel) e inmuniza el sistema previniendo desastres.

## 📈 Auto-Aprendizaje (Reinforcement Learning)

Nexpulse no depende de parámetros estáticos. Cuenta con un **Cerebro Cognitivo Persistente** (`ai_brain.json`) completamente local y privado:
- **Refuerzo Activo:** Calcula cuánta RAM recupera y cuánto tarda. Si descubre una ruta de ejecución ultra-eficiente, se recompensa a sí mismo acelerando sus ciclos de optimización.
- **Autosanación (Self-Healing):** Si detecta que el disco duro es lento (I/O Wait) o la limpieza está demorando mucho sin resultados, la IA asume que está "estresando" la máquina y automáticamente multiplica su tiempo de reposo para enfriar el sistema y no causar lentitud al usuario.

## 🔒 Certificado de Seguridad (Zero Vulnerabilities)

Sometido a auditorías extremas de Red Team (Senior Pentesting), Nexpulse cuenta con parches avanzados que rivalizan con software comercial corporativo:
- **Prevención de Inyección al Kernel:** Tipado estricto en punteros de 64-bits en C++ para evitar corrupción de la memoria RAM.
- **Micro-Hardening (Anti-TOCTOU & ADS):** Resistente a Condiciones de Carrera en el disco e inmune al ocultamiento de malware en Flujos de Datos Alternos (Alternate Data Streams).
- **Atomicidad Transaccional:** El archivo de memoria inteligente de la IA usa bloqueos (`threading.Lock`) e imposiciones de permisos restrictivos (Jail Mode), protegiéndolo de intentos de manipulación externa.

---

## ⚙️ Instalación y Compilación

1. Clona el repositorio.
2. Instala las dependencias: `pip install -r requirements.txt`
3. Genera el ejecutable aislado usando PyInstaller a través de nuestro script de empaquetado:
   ```cmd
   .\scripts\build_exe.bat
   ```
4. El programa empaquetado aparecerá en la carpeta `dist/`.

> **Nota de Privacidad:** Todo el proceso de Machine Learning y heurística ocurre de forma 100% local en la máquina. NEX-PULSE Agent jamás transmite telemetría, archivos ni registros del sistema a ningún servidor externo.
