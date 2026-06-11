@echo off
setlocal

:: Datum holen
for /f %%i in ('powershell -Command "Get-Date -Format 'yyyy-MM-dd_HH-mm'"') do set "folderdate=%%i"

:: Backup-Pfad festlegen (Wir legen es sicherheitshalber in einen festen Ordner)
set "backup_dir=C:\Bots\Backups\Backup_%folderdate%"

echo Erstelle Backup in: %backup_dir%

:: Robocopy Befehl
:: . steht für "hier im aktuellen Ordner"
:: /S kopiert alle Unterordner mit
:: /XD Backups schließt den Backup-Ordner komplett aus (verhindert das Zyklus-Problem)
robocopy . "%backup_dir%" *.py *.txt *.csv *.bat /S /XD Backups

echo ============================================
echo   Backup-Prozess abgeschlossen.
echo   Überprüfe jetzt den Ordner: %backup_dir%
echo ============================================
pause