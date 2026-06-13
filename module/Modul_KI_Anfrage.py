import requests
import json

def run_modul(text="Hallo"):
    # URL deiner lokalen Ollama-Instanz (Standard)
    url = "http://localhost:11434/api/chat"
    
    # Hier kannst du das Modell eintragen, das du lokal nutzt (z.B. llama3, mistral, etc.)
    # Wenn du ein spezifisches Modell für den Deto-Agenten nutzt, passe den Namen an!
    payload = {
        "model": "llama3", 
        "messages": [
            {
                "role": "system",
                "content": "Du bist DETO, ein hochentwickelter KI-Kunst-Agent. Du antwortest kurz, präzise, intelligent und hilfst bei der Organisation von Kunstprojekten, Finanzen und Workflows."
            },
            {
                "role": "user",
                "content": text
            }
        ],
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return data["message"]["content"]
        else:
            return f"🤖 Fehler von der lokalen KI (Status: {response.status_code})"
    except Exception as e:
        return f"🔌 Verbindung zur lokalen KI fehlgeschlagen. Läuft Ollama im Hintergrund? Fehler: {str(e)}"