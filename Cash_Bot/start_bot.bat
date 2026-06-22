@echo off
chcp 65001 >nul
title DETO CashBot Starter

REM ================================
REM   TELEGRAM BOT TOKEN SETZEN
REM ================================
set "TELEGRAM_BOT_TOKEN=8905346856:AAF9x8dA-oYf-ACfheIl-j6QsMQoOlh6qbI"

REM ================================
REM   WORKER STARTEN
REM ================================
echo Starte Worker...
start cmd /k "python -m core.Agent_Worker"

REM ================================
REM   TELEGRAM BOT STARTEN
REM ================================
echo Starte Telegram-Bot...
start cmd /k "python -m core.Agent_Telegram"

echo.
echo Beide Prozesse wurden gestartet.
pause
