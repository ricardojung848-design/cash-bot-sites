@echo off
cd /d "%~dp0"
cd ..

echo [Worker] Auto-Restart aktiv...
:loop
python -m core.Agent_Worker
echo [Worker] abgestuerzt – Neustart in 3 Sekunden...
timeout /t 3 >nul
goto loop
