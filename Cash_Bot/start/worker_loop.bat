@echo off
cd /d "%~dp0"
cd ..

echo [Worker] Auto-Restart aktiv...
:loop
python core\Agent_Worker.py
echo [Worker] abgestuerzt – Neustart in 3 Sekunden...
timeout /t 3 >nul
goto loop
