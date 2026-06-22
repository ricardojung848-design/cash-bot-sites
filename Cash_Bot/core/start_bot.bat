@echo off
chcp 65001 >nul
title DETO Telegram Bot

set "TELEGRAM_BOT_TOKEN="8905346856:AAF9x8dA-oYf-ACfheIl-j6QsMQoOlh6qbI

python -m core.Agent_Telegram

pause
