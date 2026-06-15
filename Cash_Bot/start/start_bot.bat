@echo off
cd /d "C:\Users\ricoj\Desktop\Deto_Art_Agenten\Cash_Bot"

start "Telegram Listener" cmd /k telegram_loop.bat
start "Worker" cmd /k worker_loop.bat

exit
