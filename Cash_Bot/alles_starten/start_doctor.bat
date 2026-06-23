@echo off
chcp 65001 >nul
title Doctor Starter

cd /d "C:\Users\ricoj\Desktop\Deto_Art_Agenten\Cash_Bot"

start "Doctor" cmd /k "python -m modules.Agent_Doctor"
exit
