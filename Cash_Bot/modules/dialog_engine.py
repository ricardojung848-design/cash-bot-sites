# modules/dialog_engine.py

from core.utils import log_worker


class DialogEngine:
    """
    Natürliches Sprach- und Dialogmodul.
    Erkennt Intents, extrahiert Parameter und generiert Antworten.
    Dient als Gehirn für Telegram-Kommunikation.
    """

    def __init__(self):
        self.context = {}

    # ---------------------------------------------------------
    # Intent-Erkennung
    # ---------------------------------------------------------
    def detect_intent(self, text: str) -> str:
        t = text.lower().strip()

        # Queue-Befehle
        if t.startswith("queue add"):
            return "queue_add"
        if t == "queue list":
            return "queue_list"
        if t == "queue clear":
            return "queue_clear"

        # System
        if t in ("ping", "alive", "bist du da"):
            return "ping"

        # Smalltalk
        if any(w in t for w in ["hallo", "hi", "moin", "servus"]):
            return "greeting"

        if any(w in t for w in ["danke", "thx"]):
            return "thanks"

        # Default → Chat
        return "chat"

    # ---------------------------------------------------------
    # Parameter extrahieren (für queue add)
    # ---------------------------------------------------------
    def extract_queue_add(self, text: str):
        """
        Format:
        queue add <video_path> | <caption> | <optional datetime>
        """
        try:
            payload = text[len("queue add "):].strip()
            parts = [p.strip() for p in payload.split("|")]

            video_path = parts[0]
            caption = parts[1] if len(parts) > 1 else ""
            scheduled_at = parts[2] if len(parts) > 2 else None

            return video_path, caption, scheduled_at
        except:
            return None, None, None

    # ---------------------------------------------------------
    # Antwortgenerator
    # ---------------------------------------------------------
    def generate_response(self, intent: str, result=None) -> str:
        if intent == "ping":
            return "🏓 Ich bin da und arbeite."

        if intent == "greeting":
            return "Hey Ricardo 👋 Was geht ab?"

        if intent == "thanks":
            return "Immer gerne 🙌"

        if intent == "queue_add":
            if result and "id" in result:
                return (
                    "✅ Reel zur Posting-Queue hinzugefügt!\n"
                    f"ID: {result['id']}\n"
                    f"Video: {result['video_path']}\n"
                    f"Caption: {result['caption']}\n"
                    f"Geplant: {result['scheduled_at']}"
                )
            return "❌ Konnte den Queue-Eintrag nicht erstellen."

        if intent == "queue_list":
            return result

        if intent == "queue_clear":
            return "🧹 Posting-Queue wurde geleert."

        # Default: Chat
        return f"Interessant… erzähl mir mehr darüber: {result}"
