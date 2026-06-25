@echo off
chcp 65001 >nul
title Worker Starter ⚙️

:: Setzt den absoluten Pfad zum Projekt-Hauptverzeichnis
set "PROJECT_DIR=C:\Users\ricoj\Desktop\Deto_Art_Agenten\Cash_Bot"

echo ========================================================
echo   ⚙️ STARTING CORE AGENT WORKER
echo   Projekt-Pfad: %PROJECT_DIR%
echo ========================================================
echo.

:: Wechselt sicher in das Zielverzeichnis auf dem passenden Laufwerk
cd /d "%PROJECT_DIR%"

:: Überprüfung, ob das Ziel-Skript existiert (Verhindert leere "Crash"-Fenster)
if not exist "core\Agent_Worker.py" (
    color 0C
    echo ❌ KRITISCHER FEHLER: 'core\Agent_Worker.py' wurde nicht gefunden!
    echo Bitte überprüfe, ob die Datei im core-Ordner liegt.
    goto end
)

echo [INFO] Starte Core-Worker-Schleife in neuem Fenster...
echo --------------------------------------------------------

:: Startet den Haupt-Worker in einem separaten CMD-Fenster als Modul
start "Agent Worker Engine" cmd /k "python -m core.Agent_Worker"

:end
echo.
echo --------------------------------------------------------
echo [STATUS] Starter-Skript ausgeführt.
timeout /t 3 >nul
exit