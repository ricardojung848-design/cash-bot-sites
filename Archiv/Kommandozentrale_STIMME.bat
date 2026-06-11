@echo off
title DETO 176 - STIMMEN STEUERUNG
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File .\Agent_VOICE.ps1
pause