@echo off
setlocal
title CashBot OS - Rico Edition Starter

echo [AEGIS OS] Starte Kontrollzentrum...

set "STARTER_DIR=%~dp0"
set "CASHBOT_DIR=%STARTER_DIR%.."
set "MODULES_DIR=%CASHBOT_DIR%\modules"
set "TARGET_SCRIPT=%MODULES_DIR%\Aegis_Control_Pro.py"

if not exist "%TARGET_SCRIPT%" (
  echo [FEHLER] Startskript nicht gefunden:
  echo %TARGET_SCRIPT%
  pause
  exit /b 1
)

pushd "%MODULES_DIR%"
start "" pythonw "%TARGET_SCRIPT%"
popd

exit /b 0