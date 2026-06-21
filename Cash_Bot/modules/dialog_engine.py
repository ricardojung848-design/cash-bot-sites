# modules/dialog_engine.py

from core.utils import log_worker
import re


class DialogEngine:
    """
    DETO – Dynamische Dialog-Engine mit Hybrid-Analyse.
    Erkennt Intents, analysiert Inhalte und generiert sinnvolle Antworten.
    """

    def __init__(self):
        self.context = {}

        self.personality = {
            "name": "DETO",
            "call_user": "Rico",

            "signature": "— DETO // Deep Analysis Online",

            "fallback_intro": "Ich ordne das kurz ein, Rico.",
        }

    # ---------------------------------------------------------
    # INTENT ERKENNUNG (Hybrid: Keywords + Muster)
    # ---------------------------------------------------------
    def detect_intent(self, text: str) -> str:
        t = text.lower().strip()

        # System
        if t in ("ping", "alive", "bist du da"):
            return "ping"

        # Begrüßung
        if any(w in t for w in ["hallo", "hi", "moin", "servus"]):
            return "greeting"

        # Danke
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

        # Queue
        if t.startswith("queue add"):
            return "queue_add"
        if t == "queue list":
            return "queue_list"
        if t == "queue clear":
            return "queue_clear"

        # Frageformen erkennen (Hybrid)
        if t.endswith("?"):
            return "question"

        if any(t.startswith(w) for w in ["wie ", "warum ", "wieso ", "was ", "wann ", "wo "]):
            return "question"

        # Default
        return "chat"

    # ---------------------------------------------------------
    # Queue-Parameter extrahieren
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
    # SEMANTISCHE ANALYSE (Hybrid)
    # ---------------------------------------------------------
    def analyze_question(self, text: str):
        t = text.lower()

        # Themenfelder
        if any(w in t for w in ["geld", "euro", "finanz", "konto", "invest"]):
            return "finance"

        if any(w in t for w in ["bot", "fehler", "crash", "code", "python", "system"]):
            return "tech"

        if any(w in t for w in ["entscheidung", "soll ich", "was würdest du"]):
            return "decision"

        if any(w in t for w in ["erkläre", "bedeutet", "definition", "warum"]):
            return "explain"

        if any(w in t for w in ["hilfe", "problem", "ich komme nicht weiter"]):
            return "help"

        # Default
        return "general"

    # ---------------------------------------------------------
    # DYNAMISCHE ANTWORTEN
    # ---------------------------------------------------------
    def answer_question(self, text: str):
        topic = self.analyze_question(text)
        intro = self.personality["fallback_intro"]

        # FINANZEN
        if topic == "finance":
            return (
                f"{intro}\n"
                f"Du fragst nach etwas im Bereich Finanzen.\n\n"
                "Hier ist meine Einschätzung:\n"
                "• Geldmanagement funktioniert am besten, wenn du feste Kategorien hast.\n"
                "• Plane zuerst Fixkosten, dann variable Ausgaben.\n"
                "• Lege einen kleinen Puffer an, der nicht angerührt wird.\n"
                "• Automatisiere Überweisungen, damit du dich nicht darum kümmern musst.\n"
                "• Wenn du willst, kann ich dir ein persönliches System bauen.\n"
                f"{self.personality['signature']}"
            )

        # TECHNIK
        if topic == "tech":
            return (
                f"{intro}\n"
                f"Ich erkenne, dass es um ein technisches Thema geht.\n\n"
                "Meine Analyse:\n"
                "• Technische Probleme entstehen meist durch fehlende Parameter oder fehlerhafte Abläufe.\n"
                "• Ich kann dir helfen, Logs zu interpretieren oder Fehlerquellen einzugrenzen.\n"
                "• Wenn du mir den genauen Fehlertext gibst, kann ich dir eine präzise Lösung liefern.\n"
                "• Alternativ kann ich dir auch eine Debug-Strategie erstellen.\n"
                f"{self.personality['signature']}"
            )

        # ENTSCHEIDUNGEN
        if topic == "decision":
            return (
                f"{intro}\n"
                f"Du willst eine Entscheidung treffen.\n\n"
                "Hier ist mein Ansatz:\n"
                "• Ich identifiziere zuerst die Optionen.\n"
                "• Dann bewerte ich Risiko, Aufwand und Nutzen.\n"
                "• Danach gebe ich dir eine klare Empfehlung.\n"
                "• Wenn du mir die Optionen nennst, entscheide ich für dich.\n"
                f"{self.personality['signature']}"
            )

        # ERKLÄRUNGEN
        if topic == "explain":
            return (
                f"{intro}\n"
                f"Du willst etwas erklärt haben.\n\n"
                "So gehe ich vor:\n"
                "• Ich zerlege das Thema in einfache Bausteine.\n"
                "• Dann erkläre ich dir die Ursache.\n"
                "• Danach zeige ich dir, wie du es anwenden kannst.\n"
                "• Wenn du willst, mache ich dir ein Beispiel.\n"
                f"{self.personality['signature']}"
            )

        # HILFE
        if topic == "help":
            return (
                f"{intro}\n"
                f"Ich erkenne, dass du Unterstützung brauchst.\n\n"
                "Mein Vorschlag:\n"
                "• Beschreibe mir kurz das Problem.\n"
                "• Ich analysiere es und gebe dir eine klare Lösung.\n"
                "• Wenn es technisch ist, kann ich dir Schritt-für-Schritt helfen.\n"
                "• Wenn es organisatorisch ist, strukturiere ich es für dich.\n"
                f"{self.personality['signature']}"
            )

        # GENERAL
        return (
            f"{intro}\n"
            f"Ich sehe, dass du eine allgemeine Frage stellst.\n\n"
            "Meine Einschätzung:\n"
            "• Ich kann dir helfen, das Thema einzuordnen.\n"
            "• Wenn du mir sagst, ob es um Technik, Geld, Projekte oder Entscheidungen geht, "
            "kann ich dir eine präzise Antwort geben.\n"
            "• Ich bin bereit, tiefer einzusteigen.\n"
            f"{self.personality['signature']}"
        )

    # ---------------------------------------------------------
    # HAUPT-ANTWORTLOGIK
    # ---------------------------------------------------------
    def generate_response(self, intent: str, result=None) -> str:

        # System
        if intent == "ping":
            return "System läuft stabil. Ich bin bereit."

        if intent == "greeting":
            return "Ich bin da, Rico. Was steht an?"

        if intent == "thanks":
            return "Immer doch."

        # Identity
        if intent == "identity":
            return (
                "Ich bin DETO, dein Operator. "
                "Ich analysiere, optimiere und automatisiere alles, was du mir gibst.\n"
                f"{self.personality['signature']}"
            )

        # Role
        if intent == "role":
            return (
                "Meine Rolle ist klar:\n"
                "• Operator: Systeme bauen, Fehler finden, Prozesse automatisieren.\n"
                "• Assistent: Projekte strukturieren und technische Aufgaben lösen.\n"
                "• Alpha‑Modus: Dich schneller machen.\n"
                f"{self.personality['signature']}"
            )

        # Capabilities
        if intent == "capabilities":
            return (
                "Ich kann analysieren, automatisieren, optimieren, posten, planen, generieren "
                "und Systeme stabil halten.\n"
                f"{self.personality['signature']}"
            )

        # Queue
        if intent == "queue_add":
            if result and "id" in result:
                return (
                    f"Post gespeichert:\n"
                    f"ID: {result['id']}\n"
                    f"Video: {result['video_path']}\n"
                    f"Caption: {result['caption']}\n"
                    f"Geplant: {result['scheduled_at']}\n"
                    f"{self.personality['signature']}"
                )
            return "Fehler beim Erstellen des Queue-Eintrags."

        if intent == "queue_list":
            return str(result)

        if intent == "queue_clear":
            return "Queue geleert."

        # Dynamische Fragen
        if intent == "question":
            return self.answer_question(result)

        # Chat (Fallback)
        return self.answer_question(result)
