@echo off
title DETO CashBot Konsole

:menu
cls
echo ============================================
echo        DETO CashBot Steuerkonsole
echo ============================================
echo.
echo  [1] Bot starten (Telegram + Worker, Auto-Restart)
echo  [2] Logs ansehen (Worker)
echo  [3] Logs ansehen (Telegram)
echo  [4] Auto-Update (git pull)
echo  [5] Beenden
echo.
set /p choice=Auswahl eingeben: 

if "%choice%"=="1" goto start_bot
if "%choice%"=="2" goto view_worker_log
if "%choice%"=="3" goto view_telegram_log
if "%choice%"=="4" goto auto_update
if "%choice%"=="5" goto end

goto menu

:start_bot
echo Starte Telegram Listener und Worker mit Auto-Restart...
start "Telegram Listener" cmd /k ^
"echo [Telegram] Auto-Restart aktiv... & ^
:loop_tg & ^
python Agent_Telegram.py & ^
echo [Telegram] abgestuerzt - Neustart in 3 Sekunden... & ^
timeout /t 3 & ^
goto loop_tg"

start "Worker" cmd /k ^
"echo [Worker] Auto-Restart aktiv... & ^
:loop_worker & ^
python Agent_Worker.py & ^
echo [Worker] abgestuerzt - Neustart in 3 Sekunden... & ^
timeout /t 3 & ^
goto loop_worker"

echo.
echo Beide Prozesse laufen jetzt. Fenster 'Telegram Listener' und 'Worker' zeigen Status.
pause
goto menu

:view_worker_log
cls
echo ============================================
echo        Worker-Log (logs\worker.log)
echo ============================================
echo.
if not exist logs\worker.log (
    echo Noch kein worker.log vorhanden.
    pause
    goto menu
)
type logs\worker.log
echo.
pause
goto menu

:view_telegram_log
cls
echo ============================================
echo        Telegram-Log (falls du eins anlegst)
echo ============================================
echo.
if not exist logs\telegram.log (
    echo Noch kein telegram.log vorhanden.
    pause
    goto menu
)
type logs\telegram.log
echo.
pause
goto menu

:auto_update
cls
echo ============================================
echo        Auto-Update (git pull)
echo ============================================
echo.
if not exist ..\.git (
    echo Kein Git-Repository gefunden. Auto-Update nicht verfuegbar.
    pause
    goto menu
)
cd ..
echo Fuehre git pull aus...
git pull
echo.
echo Fertig. Starte die Konsole ggf. neu, wenn sich Dateien geaendert haben.
pause
cd Cash_Bot
goto menu

:end
echo Beende Konsole...
exit
