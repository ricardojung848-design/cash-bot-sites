@echo off
chcp 65001 >nul
title Worker Starter

cd /d "C:\Users\ricoj\Desktop\Deto_Art_Agenten\Cash_Bot"

start "Worker" cmd /k "python -m core.Agent_Worker"
exit
