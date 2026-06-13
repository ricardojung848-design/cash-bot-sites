@echo off
title DETO CashBot Starter

echo Starte Telegram Listener...
start cmd /k "python Agent_Telegram.py"

echo Starte Worker...
start cmd /k "python Agent_Worker.py"

echo Beide Systeme wurden gestartet.
pause
