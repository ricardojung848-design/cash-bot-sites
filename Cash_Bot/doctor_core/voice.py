import threading
import time

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None


class VoiceEngine:
    def __init__(self, logger=None):
        self.logger = logger
        self.engine = None

        if pyttsx3 is not None:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty("rate", 185)
                if self.logger:
                    self.logger("VoiceEngine: pyttsx3 initialisiert.")
            except Exception as e:
                self.engine = None
                if self.logger:
                    self.logger(f"VoiceEngine Fehler: {e}")
        else:
            if self.logger:
                self.logger("VoiceEngine: pyttsx3 nicht installiert.")

    def speak(self, text: str):
        if self.engine is None:
            if self.logger:
                self.logger(f"(Voice deaktiviert) {text}")
            return

        def _run():
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                if self.logger:
                    self.logger(f"VoiceEngine Fehler beim Sprechen: {e}")

        threading.Thread(target=_run, daemon=True).start()

    def startup_greeting(self):
        text = (
            "Hallo Rico. Agent Doctor ist vollständig gestartet. "
            "Alle Engines wurden erfolgreich geladen. "
            "Die Hintergrundüberwachung läuft stabil. "
            "Sag mir einfach, was ich als nächstes tun soll."
        )
        self.speak(text)
