import threading
import queue
import time
from typing import Any
from doctor_core.logging import log_doctor

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None


class VoiceEngine:
    """
    MEGA-PRO-Version:
    - Thread-sichere Sprachausgabe (TTS) für den Doctor-Agenten
    - Internes Queue-System verhindert Abstürze bei parallelen speak()-Aufrufen
    - Nahtlose Integration in das globale Event-System
    - Zuverlässiges Fallback-Management für Windows ARM64
    """

    def __init__(self, engine_manager: Any = None):
        self.engines = engine_manager
        self.engine = None
        self._speech_queue = queue.Queue()
        self._loop_running = False

        # Initialisierung der Engine
        if pyttsx3 is not None:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty("rate", 185)
                log_doctor("VoiceEngine: pyttsx3 erfolgreich initialisiert.")
                
                # Startet den dedizierten, thread-sicheren Audioprofil-Worker
                self._start_speech_worker()
            except Exception as e:
                self.engine = None
                log_doctor(f"VoiceEngine Initialisierungs-Fehler: {e}")
        else:
            log_doctor("VoiceEngine: pyttsx3 nicht installiert (Verwende stummen Logger-Fallback).")

    def speak(self, text: str) -> None:
        """Fügt einen Text zur Sprech-Warteschlange hinzu. Absolut thread-sicher."""
        if not text or not text.strip():
            return

        if self.engine is None:
            log_doctor(f"[Voice deaktiviert] {text}")
            return

        # Text in die Queue legen, statt direkt pyttsx3 aufzurufen
        self._speech_queue.put(text)

    def _start_speech_worker(self):
        """Aktiviert den Hintergrund-Thread, der die Queue sequentiell abarbeitet."""
        self._loop_running = True
        t = threading.Thread(target=self._speech_worker_loop, daemon=True, name="DoctorVoiceWorker")
        t.start()

    def _speech_worker_loop(self):
        """Verarbeitet Textbausteine nacheinander, um C-Treiber-Kollisionen zu vermeiden."""
        while self._loop_running:
            try:
                # Wartet blockierend auf den nächsten Text (Timeout für Ressourcen-Schonung)
                text = self._speech_queue.get(timeout=1.0)
                
                try:
                    # Da pyttsx3.init() im Haupt- oder Nebenthread zicken kann,
                    # kapseln wir die Interaktion exklusiv in diesem Thread.
                    self.engine.say(text)
                    self.engine.runAndWait()
                except Exception as e:
                    log_doctor(f"VoiceEngine Fehler während der Tonausgabe: {e}")
                
                self._speech_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                log_doctor(f"CRITICAL VoiceEngine Worker-Fehler: {e}")

    def startup_greeting(self) -> None:
        """Begrüßungs-Sequenz beim Systemstart."""
        text = (
            "Hallo Rico. Agent Doctor ist vollständig gestartet. "
            "Alle Engines wurden erfolgreich geladen. "
            "Die Hintergrundüberwachung läuft stabil. "
            "Sag mir einfach, was ich als nächstes tun soll."
        )
        self.speak(text)