@echo off
chcp 65001 >nul
title Agent Doctor Starter

cd /d "C:\Users\ricoj\Desktop\Deto_Art_Agenten\Cash_Bot"

py -3.13-64 -m modules.Agent_Doctor
pause
