import requests
import json

# OLLAMA KONFIGURATION
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "deto_agent"  # Dein lokales Modell

def generiere_pitch(zielgruppe, projekt_info):
    """Generiert ein professionelles Anschreiben/Pitch über Ollama."""
    prompt = f"""
Du bist der PR-Assistent des Künstlers DETO. Er arbeitet im Bereich 'Puristische Narrative Fluid Art' (Lava Flow Realism) und setzt großflächige, kreative Raumkonzepte und Event-Setups um.
Schreibe eine professionelle, überzeugende und absolut auf den Punkt gebrachte Pitch-E-Mail für folgendes Ziel:

EMPFÄNGER/ZIELGRUPPE: {zielgruppe}
PROJEKT-DETAILS/IDEE: {projekt_info}

RICHTLINIEN:
1. Schreibe im Namen von DETO (oder seinem Management). Der Ton ist modern, künstlerisch anspruchsvoll, aber geschäftstüchtig und professionell.
2. Hebe den visuellen und räumlichen Impact der Arbeiten hervor.
3. Integriere eine klare Betreffzeile und einen starken "Call to Action" am Ende (Vorschlag für Telefonat oder Atelier-Besuch).
4. Antworte AUSSCHLIESSLICH mit dem fertigen Text des Anschreibens. Keine Einleitung wie "Hier ist dein Pitch", kein Markdown-Codeblock (```). Nur der rohe E-Mail-Text.
"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.5}
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=90)
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            return f"❌ Ollama fehlerhaft: Status Code {response.status_code}"
    except Exception as e:
        return f"❌ Verbindung zu Ollama fehlgeschlagen: {e}"

def analysiere_ausschreibung(text_ausschreibung):
    """Fasst lange Ausschreibungstexte oder Open Calls knackig zusammen."""
    prompt = f"""
Du bist der PR-Assistent des Künstlers DETO. Analysiere den folgenden Ausschreibungstext (Open Call / Kulturelles Projekt) und extrahiere die kritischen Kernfakten für den Künstler.

TEXT DER AUSSCHREIBUNG:
\"\"\"
{text_ausschreibung}
\"\"\"

ANWEISUNG:
Fasse den Text rigoros zusammen. Antworte AUSSCHLIESSLICH im folgenden Format (nutze genau diese Emojis für die Struktur):

📅 **Fristen & Termine:** (Wann ist Bewerbungsschluss? Wann läuft das Event?)
💰 **Finanzen & Budget:** (Teilnahmegebühr? Honorar? Transportkostenübernahme? Preisgeld?)
🎨 **Anforderungen:** (Welche Medien, Maße, Themen oder Voraussetzungen gibt es?)
📩 **Bewerbungsweg:** (Wie und wo einreichen? E-Mail, Portal, welche Unterlagen?)
🎯 **Quick-Check:** (1-2 Sätze Einschätzung: Passt das zu zeitgenössischer Fluid Art, großformatiger Malerei oder Event-Design?)
"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.3}
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=90)
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            return f"❌ Ollama fehlerhaft: Status Code {response.status_code}"
    except Exception as e:
        return f"❌ Verbindung zu Ollama fehlgeschlagen: {e}"