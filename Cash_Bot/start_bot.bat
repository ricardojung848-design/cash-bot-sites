@echo off
cd /d "C:\Users\ricoj\Desktop\Deto_Art_Agenten\Cash_Bot"

:: ============================
:: TELEGRAM LISTENER
:: ============================
start "Telegram Listener" cmd /k ^
"echo [Telegram] Auto-Restart aktiv... & ^
:loop_tg & ^
python Agent_Telegram.py & ^
echo [Telegram] abgestuerzt - Neustart in 3 Sekunden... & ^
timeout /t 3 >nul & ^
goto loop_tg"

:: ============================
:: WORKER
:: ============================
start "Worker" cmd /k ^
"echo [Worker] Auto-Restart aktiv... & ^
:loop_worker & ^
python Agent_Worker.py & ^
echo [Worker] abgestuerzt - Neustart in 3 Sekunden... & ^
timeout /t 3 >nul & ^
goto loop_worker"

exit
