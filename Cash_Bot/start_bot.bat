@echo off
cd /d "C:\Users\ricoj\Desktop\Deto_Art_Agenten\Cash_Bot"

:: ============================
:: TELEGRAM LISTENER
:: ============================
start "Telegram Listener" cmd /k "call :loop_tg"
goto start_worker

:loop_tg
echo [Telegram] Auto-Restart aktiv...
python Agent_Telegram.py
echo [Telegram] abgestuerzt - Neustart in 3 Sekunden...
timeout /t 3 >nul
goto loop_tg


:: ============================
:: WORKER
:: ============================
:start_worker
start "Worker" cmd /k "call :loop_worker"
goto :eof

:loop_worker
echo [Worker] Auto-Restart aktiv...
python Agent_Worker.py
echo [Worker] abgestuerzt - Neustart in 3 Sekunden...
timeout /t 3 >nul
goto loop_worker
