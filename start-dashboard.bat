@echo off
chcp 65001 >nul
title CashBot Unified Command Center

set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

echo ============================================
echo   STARTING UNIFIED COMMAND CENTER
echo   %PROJECT_DIR%
echo   LOCAL ONLY: http://127.0.0.1:8088
echo ============================================

set "PYTHONUTF8=1"

start "" http://127.0.0.1:8088/
python -m uvicorn dashboard.backend.main:app --host 127.0.0.1 --port 8088
