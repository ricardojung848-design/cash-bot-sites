@echo off
echo [AEGIS OS] Starte Kontrollzentrum...
:: Wechselt in das Verzeichnis, in dem deine Skripte liegen
cd /d "C:\Users\ricoj\Desktop\Deto_Art_Agenten\Cash_Bot\modules"
:: Startet das Dashboard sauber im Hintergrund
start pythonw Aegis_Control_Pro.py
exit