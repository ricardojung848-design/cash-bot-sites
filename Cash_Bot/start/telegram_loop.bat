@echo off
cd /d "%~dp0"
cd ..

echo [Telegram] Auto-Restart aktiv...
:loop
python core\Agent_Telegram.py
echo [Telegram] abgestuerzt – Neustart in 3 Sekunden...
timeout /t 3 >nul
goto loop
