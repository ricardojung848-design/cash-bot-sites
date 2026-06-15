@echo off
cd /d "%~dp0"

echo Starte DetoBot...
start "" "start\worker_loop.bat"
start "" "start\telegram_loop.bat"
