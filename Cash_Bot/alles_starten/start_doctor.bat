@echo off
chcp 65001 >nul
title Agent Doctor Starter 🚀

:: Setzt den absoluten Pfad zum Projekt-Hauptverzeichnis
set "PROJECT_DIR=C:\Users\ricoj\Desktop\Deto_Art_Agenten\Cash_Bot"

echo ========================================================
echo   🤖 STARTING AGENT DOCTOR ECOSYSTEM
echo   Projekt-Pfad: %PROJECT_DIR%
echo ========================================================
echo.

:: Wechselt sicher in das Zielverzeichnis auf dem passenden Laufwerk
cd /d "%PROJECT_DIR%"

:: Überprüfung, ob das Ziel-Skript an der richtigen Stelle existiert
if not exist "modules\Agent_Doctor.py" (
    color 0C
    echo ❌ KRITISCHER FEHLER: 'modules\Agent_Doctor.py' wurde nicht gefunden!
    echo Bitte überprüfe die Ordnerstruktur im VS Code.
    goto end
)

echo [INFO] Starte Core-Engine mit Python 3.13-64...
echo --------------------------------------------------------

:: Führt das Modul aus dem Hauptverzeichnis heraus im Kontext des Paket-Managers aus
py -3.13-64 -m modules.Agent_Doctor

:end
echo.
echo --------------------------------------------------------
echo [STATUS] Prozess beendet oder manuell gestoppt.
pause