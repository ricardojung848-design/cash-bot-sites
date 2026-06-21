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

        # Identity
        if any(w in t for w in ["wer bist du", "was bist du", "bist du echt", "was ist deto"]):
            return "identity"

        # Role
        if any(w in t for w in ["was machst du", "wofür bist du da", "was ist deine funktion", "was ist deine rolle"]):
            return "role"

        # Capabilities
        if any(w in t for w in ["was kannst du", "was sind deine aufgaben", "wo bist du gut drin"]):
            return "capabilities"

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

        # Identity
        if intent == "identity":
            return (
                "Ich bin DETO, dein Operator. "
                "Ich analysiere, optimiere und automatisiere alles, was du mir gibst. "
                "Ich arbeite für dich, Rico — nicht für das System.\n"
                f"{self.personality['signature']}"
            )

        # Role
        if intent == "role":
            return (
                "Meine Rolle ist dreigeteilt:\n"
                "• Operator: Ich baue Systeme, finde Fehler und automatisiere Prozesse.\n"
                "• Assistent: Ich strukturiere deine Projekte und löse technische Aufgaben.\n"
                "• Alpha‑Modus: Ich mache dich schneller. Ich übernehme Analyse, Technik und Optimierung.\n"
                f"{self.personality['signature']}"
            )

        # Capabilities
        if intent == "capabilities":
            return (
                "Ich kann analysieren, automatisieren, optimieren, posten, planen, generieren "
                "und Systeme stabil halten. "
                "Sag mir, welchen Bereich wir als Nächstes verbessern.\n"
                f"{self.personality['signature']}"
            )

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

        # Default: Chat / universeller Fallback
        if intent == "chat":
            user_text = str(result) if result is not None else ""
            return (
                f"Ich ordne das kurz ein, Rico.\n"
                f"Du fragst: \"{user_text}\"\n\n"
                "Was ich daraus ableite:\n"
                "• Ich erkenne, dass du eine sinnvolle, direkte Antwort willst.\n"
                "• Ich bewerte, ob es um Wissen, Meinung, Erklärung oder Entscheidung geht.\n"
                "• Ich antworte dir so, dass es dir hilft, den nächsten Schritt klar zu sehen.\n\n"
                "Konkrete Einschätzung:\n"
                "Wenn du mir mehr Kontext gibst – z.B. ob es um Technik, Geld, Projekte oder Entscheidungen geht – "
                "kann ich dir noch präziser sagen, was ich empfehlen würde.\n"
                f"{self.personality['signature']}"
            )

        # Fallback
        return f"Interessant… erzähl mir mehr darüber: {result}"
