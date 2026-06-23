@echo off
chcp 65001 >nul
title DETO CashBot Starter (PRO)

REM ============================================================
REM   TELEGRAM TOKEN SETZEN
REM ============================================================
set "TELEGRAM_BOT_TOKEN=8905346856:AAF9x8dA-oYf-ACfheIl-j6QsMQoOlh6qbI"

echo.
echo ============================================
echo   Starte DETO CashBot (PRO)
echo   Worker + Telegram + Doctor
echo   (Anti-Double-Start aktiviert)
echo ============================================
echo.

REM ============================================================
REM   ALTE PYTHON-PROZESSE BEENDEN (Anti-Double-Start)
REM ============================================================
echo Beende alte Python-Prozesse...
taskkill /IM python.exe /F >nul 2>&1

timeout /t 1 >nul

REM ============================================================
REM   WORKER STARTEN
REM ============================================================
echo Starte Worker...
start "Worker" cmd /k "python -m core.Agent_Worker"

REM ============================================================
REM   TELEGRAM STARTEN
REM ============================================================
echo Starte Telegram-Bot...
start "Telegram" cmd /k "python -m core.Agent_Telegram"

REM ============================================================
REM   DOCTOR STARTEN
REM ============================================================
echo Starte Agent_Doctor...
start "Doctor" cmd /k "python -m modules.Agent_Doctor"

echo.
echo Alle Prozesse wurden erfolgreich gestartet.
exit
