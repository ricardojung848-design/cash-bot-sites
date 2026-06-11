import json
import os

def erstelle_monatsbericht():
    bericht = "--- MONATSBERICHT FINANZAMT ---\n"
    if os.path.exists("buchhaltung.json"):
        with open("buchhaltung.json", "r") as f:
            for line in f:
                bericht += line
    else:
        bericht += "Keine Rechnungen gefunden."
    
    with open("Export_Steuer_Monat.txt", "w") as f:
        f.write(bericht)
    return "Bericht 'Export_Steuer_Monat.txt' wurde erstellt."