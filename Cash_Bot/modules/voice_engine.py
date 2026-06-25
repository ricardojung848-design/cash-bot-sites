import os
import requests
from pathlib import Path
from typing import Optional

from doctor_core.logging import log_doctor
from doctor_core.engine_manager import EngineManager


class VoiceEngine:
    """
    PRO-Version der VoiceEngine:
    - Kapselt die OpenAI TTS-Schnittstelle zur asynchronen Voiceover-Generierung.
    - Vollständig thread-sicher für die parallele Abarbeitung in der FabrikEngine integriert.
    - Nutzt moderne Pathlib-Operationen zur Verzeichnisvalidierung vor dem Schreibvorgang.
    """

    def __init__(self, engine_manager: EngineManager):
        self.engines = engine_manager
        # API-Key dynamisch aus der Systemumgebung laden
        self.api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        
        # Standardkonfiguration für die Stimmen-Ausgabe
        self.model = "tts-1"  # Offizielles OpenAI TTS-Standardmodell (zuvor gpt-4o-mini-tts)
        self.voice = "alloy"  # Neutrale, klare Stimme (Anpassung je nach TikTok/Reel-Style möglich)

    def generate_voiceover(self, text: str, output_path: str) -> str:
        """
        Sendet den Text an die OpenAI Audio-API, generiert eine MP3-Audiodatei 
        und speichert diese am gewünschten Zielort ab.
        """
        if not self.api_key:
            log_doctor("VoiceEngine-Fehler: 'OPENAI_API_KEY' fehlt in den Umgebungsvariablen.")
            return ""

        if not text.strip():
            log_doctor("VoiceEngine-Warnung: Leerer Text an TTS-Engine übergeben.")
            return ""

        log_doctor(f"VoiceEngine: Starte TTS-Anfrage an OpenAI (Modell: {self.model}, Stimme: {self.voice})...")

        url = "https://api.openai.com/v1/audio/speech"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "voice": self.voice,
            "input": text,
            "response_format": "mp3",
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            if response.status_code != 200:
                log_doctor(f"VoiceEngine-Fehler: API meldet Status {response.status_code} - {response.text}")
                return ""
        except Exception as e:
            log_doctor(f"VoiceEngine-Kritisch: Netzwerkfehler bei TTS-Request: {e}")
            return ""

        # Ordnerstrukturen prüfen und Datei schreiben
        try:
            target_path = Path(output_path).resolve()
            target_path.parent.mkdir(parents=True, exist_ok=True)

            with open(target_path, "wb") as f:
                f.write(response.content)

            log_doctor(f"VoiceEngine: 🎉 Voiceover erfolgreich generiert und gesichert -> {target_path}")
            return str(target_path)
            
        except Exception as e:
            log_doctor(f"VoiceEngine-Fehler beim Schreiben der Audiodatei auf Festplatte: {e}")
            return ""


# Abwärtskompatibler Einstiegspunkt für ältere Programmteile
def generate_voiceover_legacy(text: str, output_path: str, engine_manager: EngineManager) -> str:
    """Erlaubt Legacy-Modulen den Aufruf der neuen Sprachgenerierungs-Logik."""
    engine = VoiceEngine(engine_manager)
    return engine.generate_voiceover(text, output_path)