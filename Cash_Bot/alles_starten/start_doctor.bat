@echo off
chcp 65001 >nul
title Agent Doctor Starter

cd /d "C:\Users\ricoj\Desktop\Deto_Art_Agenten\Cash_Bot"

py -3.11-64 modules\Agent_Doctor.py
pause
