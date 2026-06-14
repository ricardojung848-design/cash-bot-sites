@echo off
cd /d "C:\Users\ricoj\Desktop\Deto_Art_Agenten\Cash_Bot"

:loop_tg
echo [Telegram] Auto-Restart aktiv...
python Agent_Telegram.py
echo [Telegram] abgestuerzt - Neustart in 3 Sekunden...
timeout /t 3 >nul
goto loop_tg
