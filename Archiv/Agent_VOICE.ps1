# Windows-Stimm-Engine aktivieren
$agentVoice = New-Object -ComObject SAPI.SpVoice

Clear-Host
Write-Host "===================================================" -ForegroundColor Green
Write-Host "   DETO 176 - VOICE INTERFACE INITIALISIERT        " -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Green
Write-Host " Status: Bereit und offline verknuepft." -ForegroundColor Green
Write-Host " Tipp: Druecke gleich [Win + H], um zu sprechen! " -ForegroundColor Yellow
Write-Host "===================================================" -ForegroundColor Green
Write-Host ""

# Erste Begrüßung laut sprechen
$agentVoice.Speak("Kommandozentrale aktiv. Ich hoere dir zu, DETO.")

while ($true) {
    # Spracheingabe des Nutzers abfragen
    $userInput = Read-Host ">>> DEIN BEFEHL (Nutze Win+H zum Sprechen)"
    
    # Erweiterte Sprach-Beenden-Befehle abfangen
    $cleanInput = $userInput.ToLower().Trim()
    if ($cleanInput -match "exit" -or $cleanInput -match "beenden" -or $cleanInput -match "aus" -or $cleanInput -match "ausschalten" -or $cleanInput -match "stop" -or $cleanInput -match "feierabend") { 
        $agentVoice.Speak("Kommandozentrale wird heruntergefahren. Bis zum naechsten Briefing, DETO.")
        break 
    }    
    # Leere Eingaben ignorieren
    if ([string]::IsNullOrWhiteSpace($userInput)) { continue }

    Write-Host "Agent analysiert und kalkuliert..." -ForegroundColor Yellow
    
    # Befehl an das lokale Llama-Modell senden und Antwort abfangen
    $response = ollama run deto_agent "$userInput"
    
    # Antwort im Fenster anzeigen
    Write-Host "`n[DETO-AGENT]:" -ForegroundColor Cyan
    Write-Host $response
    Write-Host "===================================================`n"
    
    # Der Agent spricht den geschriebenen Text laut aus
    $agentVoice.Speak($response)
}