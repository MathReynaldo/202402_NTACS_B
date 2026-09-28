; =========================================================
; NEXPULSE AGENT - INNO SETUP INSTALLER SCRIPT
; =========================================================
; Este script genera un instalador profesional (setup.exe)
; =========================================================

[Setup]
; Metadatos y Credenciales
AppId={{8B3C1F4A-2A1B-4C9D-9F3E-5B7A6C8D9E0F}
AppName=NEX-PULSE Agent
AppVersion=1.0.0
AppPublisher=Cristian Lucas
AppCopyright=Copyright (C) 2026 Cristian Lucas
AppPublisherURL=https://github.com/Cristian-code24/NEX-PULSE-Agent
AppSupportURL=https://github.com/Cristian-code24/NEX-PULSE-Agent
AppUpdatesURL=https://github.com/Cristian-code24/NEX-PULSE-Agent

; Rutas de Instalación Oficiales de Windows
DefaultDirName={autopf}\NEX-PULSE Agent
DefaultGroupName=NEX-PULSE Agent

; Privilegios (Requiere Admin para instalar en Archivos de Programa)
PrivilegesRequired=admin

; Configuración del Archivo Final (Setup.exe)
OutputDir=..\dist
OutputBaseFilename=Nexpulse_Agent_Installer_v1.0.0
Compression=lzma2/ultra64
SolidCompression=yes

; Estética del Instalador
WizardStyle=modern

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Origen de los archivos (Debe haber sido compilado previamente con build_exe.bat)
; Copia el ejecutable universal al destino
Source: "..\dist\NEX-PULSE-Agent.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Accesos Directos (Menú de Inicio)
Name: "{group}\NEX-PULSE Agent"; Filename: "{app}\NEX-PULSE-Agent.exe"
Name: "{group}\{cm:UninstallProgram,NEX-PULSE Agent}"; Filename: "{uninstallexe}"
; Acceso Directo (Escritorio)
Name: "{autodesktop}\NEX-PULSE Agent"; Filename: "{app}\NEX-PULSE-Agent.exe"; Tasks: desktopicon

[Run]
; Opcion final en el asistente: "Ejecutar Nexpulse Agent ahora"
Filename: "{app}\NEX-PULSE-Agent.exe"; Description: "{cm:LaunchProgram,NEX-PULSE Agent}"; Flags: nowait postinstall skipifsilent
