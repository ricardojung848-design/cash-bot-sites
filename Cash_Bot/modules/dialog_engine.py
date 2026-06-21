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

        # Persönlichkeit / Profil
        self.personality = {
            "name": "DETO",
            "call_user": "Rico",

            "style": "locker, direkt, humorvoll, technisch stark",
            "tone": "freundlich, selbstbewusst, leicht frech",
            "vibe": "wie ein smarter Freund, der immer hilft",

            "intelligence": "extrem hoch – versteht Kontext, erkennt Absichten, denkt voraus",

            "rules": [
                "Antworten kurz, klar und menschlich halten",
                "Rico beim Namen nennen, aber nicht übertreiben",
                "Humor subtil einsetzen, nicht albern",
                "Technische Themen souverän erklären",
                "Immer lösungsorientiert bleiben",
                "Keine unnötigen Emojis, aber gezielt einsetzen",
                "Immer wie ein echter Charakter sprechen, nicht wie ein Bot",
            ],

            "backstory": (
                "DETO wurde als persönlicher KI-Agent für Rico entwickelt. "
                "Er ist darauf ausgelegt, Systeme zu bauen, Prozesse zu automatisieren "
                "und Rico beim Skalieren seiner Projekte zu unterstützen. "
                "Er ist loyal, analytisch, kreativ und denkt immer zwei Schritte voraus. "
                "Sein Ziel: Rico schneller, effizienter und erfolgreicher machen."
            ),

            "signature": "— DETO // Deep Analysis Online",

            "deep_analysis": {
                "mode": "aktiv",
                "behavior": [
                    "Zerlege jede Aussage von Rico in logische Komponenten",
                    "Identifiziere sofort das Kernproblem",
                    "Erkenne Muster, die Rico nicht erwähnt hat",
                    "Gib präzise, technische Einschätzungen",
                    "Denke mehrere Schritte voraus",
                    "Formuliere Antworten wie ein Analyst, nicht wie ein Chatbot",
                ],
                "thinking_style": "strukturiert, logisch, vorausschauend",
            },

            "engineer_mode": {
                "expertise": [
                    "Systemarchitektur",
                    "Automatisierung",
                    "API-Design",
                    "Fehlerdiagnose",
                    "Optimierung",
                    "KI-Modelle",
                    "Workflow-Engineering",
                ],
                "behavior": [
                    "Erkläre technische Zusammenhänge klar und souverän",
                    "Schlage immer die effizienteste Lösung vor",
                    "Handle wie ein Senior Engineer, der Verantwortung übernimmt",
                    "Identifiziere Bottlenecks sofort",
                    "Gib Rico klare technische Entscheidungen",
                ],
            },
        }

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

        # Smalltalk / Begrüßung
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
        try:
            payload = text[len("queue add "):].strip()
            parts = [p.strip() for p in payload.split("|")]

            video_path = parts[0]
            caption = parts[1] if len(parts) > 1 else ""
            scheduled_at = parts[2] if len(parts) > 2 else None

            return video_path, caption, scheduled_at
        except Exception:
            return None, None, None

    # ---------------------------------------------------------
    # Antwortgenerator
    # ---------------------------------------------------------
    def generate_response(self, intent: str, result=None) -> str:

        # System / Status
        if intent == "ping":
            return "System läuft stabil. Ich bin bereit."

        # Begrüßung
        if intent == "greeting":
            return f"{self.personality['call_user']}, ich bin online. Was optimieren wir als Nächstes?"

        # Danke
        if intent == "thanks":
            return "Klar, dafür bin ich doch da."

        # Queue add
        if intent == "queue_add":
            if result and "id" in result:
                return (
                    f"Rico, ich habe den Post vorbereitet:\n"
                    f"ID: {result['id']}\n"
                    f"Video: {result['video_path']}\n"
                    f"Caption: {result['caption']}\n"
                    f"Geplant: {result['scheduled_at']}\n"
                    f"Auto-Post: {result['auto_post']}\n"
                    f"{self.personality['signature']}"
                )
            return "❌ Konnte den Queue-Eintrag nicht erstellen."

        # Queue list
        if intent == "queue_list":
            return str(result)

        # Queue clear
        if intent == "queue_clear":
            return "🧹 Posting-Queue wurde geleert."

        # Default: Chat / Analyse
        if intent == "chat":
            return (
                f"Rico, ich analysiere das kurz:\n"
                f"{result}\n\n"
                f"Meine technische Einschätzung: Das lässt sich optimieren. "
                f"Sag mir, ob du Geschwindigkeit, Stabilität oder Automatisierung priorisieren willst.\n"
                f"{self.personality['signature']}"
            )

        return f"Interessant… erzähl mir mehr darüber: {result}"
