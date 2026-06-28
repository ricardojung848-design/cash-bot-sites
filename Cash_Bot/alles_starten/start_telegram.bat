@echo off
chcp 65001 >nul
title Telegram Bot Starter 🤖

:: Setzt den absoluten Pfad zum Projekt-Hauptverzeichnis
set "PROJECT_DIR=C:\Users\ricoj\Desktop\Deto_Art_Agenten\Cash_Bot"

echo ========================================================
echo   💬 STARTING TELEGRAM BOT INTERFACE
echo   Projekt-Pfad: %PROJECT_DIR%
echo ========================================================
echo.

:: Wechselt sicher in das Zielverzeichnis auf dem passenden Laufwerk
cd /d "%PROJECT_DIR%"

:: Erwartet TELEGRAM_BOT_TOKEN aus System-/User-Umgebung oder vorigem Shell-Context
if "%TELEGRAM_BOT_TOKEN%"=="" (
    color 0C
    echo ❌ KRITISCHER FEHLER: Umgebungsvariable TELEGRAM_BOT_TOKEN fehlt.
    echo Bitte vor dem Start setzen, z.B.:
    echo setx TELEGRAM_BOT_TOKEN "dein-token"
    goto end
)

:: Überprüfung, ob das Ziel-Skript existiert
if not exist "core\Agent_Telegram.py" (
    color 0C
    echo ❌ KRITISCHER FEHLER: 'core\Agent_Telegram.py' wurde nicht gefunden!
    echo Bitte überprüfe, ob die Datei im core-Ordner liegt.
    goto end
)

echo [INFO] Starte Telegram-Schnittstelle in neuem Fenster...
echo --------------------------------------------------------

:: Startet den Bot in einem separaten, minimierten oder aktiven Konsolenfenster
start "Telegram Bot Engine" cmd /k "python -m core.Agent_Telegram"

:end
echo.
echo --------------------------------------------------------
echo [STATUS] Starter-Skript ausgeführt.
timeout /t 3 >nul
exit