import os
import requests
from core.utils import log_worker, warn_worker, error_worker


class VoiceEngine:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.model = "gpt-4o-mini-tts"  # OpenAI TTS Modell
        self.voice = "alloy"            # Voice D (jung, weiblich, TikTok-Style)

    # ---------------------------------------------------------
    # Hauptfunktion: Voiceover erzeugen
    # ---------------------------------------------------------
    def generate_voiceover(self, text: str, output_path: str) -> str:
        if not self.api_key:
            error_worker("❌ Kein TTS API Key gesetzt.")
            return ""

        log_worker("🎤 Erzeuge Voiceover...")

        url = "https://api.openai.com/v1/audio/speech"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "voice": self.voice,
            "input": text,
            "format": "mp3",
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
        except Exception as e:
            error_worker(f"❌ Netzwerkfehler bei TTS: {e}")
            return ""

        if response.status_code != 200:
            error_worker(f"❌ TTS Fehler: {response.text}")
            return ""

        try:
            with open(output_path, "wb") as f:
                f.write(response.content)
        except Exception as e:
            error_worker(f"❌ Fehler beim Speichern des Voiceovers: {e}")
            return ""

        log_worker(f"🎧 Voiceover gespeichert: {output_path}")
        return output_path
