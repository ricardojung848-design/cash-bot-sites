@echo off
chcp 65001 >nul
title Agent_Doctor Starter

echo Starte Agent_Doctor...
start "Doctor" cmd /k "python -m modules.Agent_Doctor"

exit
