# core/Logik.py

from modules.dialog_engine import DialogEngine
from core.utils import log_worker, error_worker

dialog_engine = DialogEngine()


# ---------------------------------------------------------
# KI-Anfrage verarbeiten
# ---------------------------------------------------------
def process_ki_anfrage(text: str) -> str:
    """
    Nimmt den User-Text entgegen,
    erkennt den Intent,
    und gibt eine dynamische Antwort zurück.
    """

    try:
        if not text:
            return "Ich habe keinen Text erhalten."

        # Intent erkennen
        intent = dialog_engine.detect_intent(text)

        # WICHTIG: Text korrekt weitergeben!
        response = dialog_engine.generate_response(intent, text)

        return response

    except Exception as e:
        error_worker(f"Fehler in process_ki_anfrage: {e}")
        return "Es gab einen Fehler bei der Verarbeitung deiner Anfrage."


# ---------------------------------------------------------
# Auto-Posting Tick
# ---------------------------------------------------------
def auto_posting_tick():
    """
    Wird vom Worker regelmäßig aufgerufen.
    Hier kannst du später Auto-Posting, Scheduler,
    Queue-Handling oder Cron-ähnliche Abläufe einbauen.
    """

    try:
        # Placeholder – später erweiterbar
        pass

    except Exception as e:
        error_worker(f"Fehler im Auto-Posting Tick: {e}")
