@echo off
setlocal

:: Datum zuverlässig über PowerShell holen
for /f %%i in ('powershell -Command "Get-Date -Format 'yyyy-MM-dd_HH-mm'"') do set "folderdate=%%i"

:: Backup-Ordner-Pfad definieren
set "backup_dir=C:\Bots\Backups\Backup_%folderdate%"

:: Verzeichnis erstellen
mkdir "%backup_dir%"

echo Erstelle Backup in: %backup_dir%

:: Dateien kopieren (passt diese Pfade an, falls deine Bots nicht direkt in C:\Bots liegen)
xcopy /s /i /y "*.py" "%backup_dir%"
xcopy /s /i /y "*.txt" "%backup_dir%"
xcopy /s /i /y "*.csv" "%backup_dir%"
xcopy /s /i /y "*.bat" "%backup_dir%"

echo ============================================
echo   Backup erfolgreich erstellt!
echo   Deine Daten sind sicher.
echo ============================================
pause