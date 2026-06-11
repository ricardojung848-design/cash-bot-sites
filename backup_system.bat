@echo off
echo Starte Backup der Agenten...

:: Zielordner definieren
set "zielordner=Backups\Aktuelles_Backup"

:: Ordner erstellen, falls er nicht existiert
if not exist "Backups" mkdir "Backups"

:: Kopieren der Bot-Ordner
echo Kopiere Cash_Bot...
xcopy "Cash_Bot" "%zielordner%\Cash_Bot" /E /I /H /K /Y

echo Kopiere Kunst_Bot...
xcopy "Kunst_Bot" "%zielordner%\Kunst_Bot" /E /I /H /K /Y

echo ============================
echo Backup erfolgreich erstellt!
echo Die Daten liegen in: %zielordner%
echo ============================
pause