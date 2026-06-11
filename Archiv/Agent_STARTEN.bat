@echo off
title DETO 176 - KUNST-AGENTUR
echo ----------------------------------------------------
echo ERWECKE DAS EMPORIUM - DETO 176 KUNST-AGENT
echo ----------------------------------------------------
echo.
echo Der Agent wird geladen... Bitte einen Moment Geduld.
echo.

:: Ollama im Hintergrund starten (wird hier nicht blockiert)
start "" ollama run deto_agent

:: Jetzt den Telegram-Bot starten
python Agent_Telegram.py

pause