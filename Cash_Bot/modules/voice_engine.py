# modules/voice_engine.py

import os
from core.utils import log_worker, error_worker

class VoiceEngine:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_voiceover(self, text: str, output_path: str) -> str:
        """
        Erzeugt Voiceover mit Stimme D (jung, weiblich, TikTok-Style)
        """
        try:
            # Beispiel: OpenAI TTS (du kannst später ElevenLabs einbauen)
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            response = client.audio.speech.create(
                model="gpt-4o-mini-tts",
                voice="alloy",  # später ersetzen durch echte TikTok-Stimme
                input=text
            )

            with open(output_path, "wb") as f:
                f.write(response.read())

            log_worker(f"🎤 Voiceover gespeichert: {output_path}")
            return output_path

        except Exception as e:
            error_worker(f"❌ Voiceover-Fehler: {e}")
            return ""
