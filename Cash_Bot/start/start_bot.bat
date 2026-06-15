@echo off
cd /d "%~dp0"
cd ..

echo Starte DetoBot...
start "" "start\worker_loop.bat"
start "" "start\telegram_loop.bat"
