@echo off
cd /d "C:\Users\ricoj\Desktop\Deto_Art_Agenten\Cash_Bot"

:loop_worker
echo [Worker] Auto-Restart aktiv...
python Agent_Worker.py
echo [Worker] abgestuerzt - Neustart in 3 Sekunden...
timeout /t 3 >nul
goto loop_worker
