@echo off
chcp 65001 >nul
title Telegram Starter

cd /d "C:\Users\ricoj\Desktop\Deto_Art_Agenten\Cash_Bot"

REM >>> HIER DEIN TOKEN EINTRAGEN
set "TELEGRAM_BOT_TOKEN=8905346856:AAF9x8dA-oYf-ACfheIl-j6QsMQoOlh6qbI"

echo Starte Telegram-Bot...
start "Telegram" cmd /k "python -m core.Agent_Telegram"

exit
