@echo off
chcp 65001 >nul
title Telegram Bot Starter

echo Starte Telegram-Bot...
start "Telegram" cmd /k "python -m core.Agent_Telegram"

exit
