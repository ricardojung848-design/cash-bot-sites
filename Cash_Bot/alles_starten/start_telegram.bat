@echo off
chcp 65001 >nul
title Telegram Starter

cd /d "C:\Users\ricoj\Desktop\Deto_Art_Agenten\Cash_Bot"

start "Telegram" cmd /k "python -m core.Agent_Telegram"
exit
