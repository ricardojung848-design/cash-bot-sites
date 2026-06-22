@echo off
title DETO Telegram Bot Starter

REM ================================
REM   TELEGRAM BOT TOKEN SETZEN
REM ================================
set TELEGRAM_BOT_TOKEN=8905346856:AAF9x8dA-oYf-ACfheIl-j6QsMQoOlh6qbI

echo [Telegram] Starte DETO Bot...
echo.

REM ================================
REM   BOT STARTEN MIT AUTO-RESTART
REM ================================
:RESTART
python -m core.Agent_Telegram

echo.
echo [Telegram] abgestuerzt. Neustart in 3 Sekunden...
timeout /t 3 >nul
goto RESTART
