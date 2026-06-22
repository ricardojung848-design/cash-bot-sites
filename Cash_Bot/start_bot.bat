@echo off
chcp 65001 >nul
title DETO CashBot Starter

REM >>> Hier deinen echten Telegram-Token eintragen
set "TELEGRAM_BOT_TOKEN=8905346856:AAF9x8dA-oYf-ACfheIl-j6QsMQoOlh6qbI"

echo Starte Worker...
start cmd /k "python -m core.Agent_Worker"

echo Starte Telegram-Bot...
start cmd /k "python -m core.Agent_Telegram"

echo Starte Agent_Doctor...
start cmd /k "python -m modules.Agent_Doctor"

echo.
echo Alle Prozesse wurden gestartet.
exit
