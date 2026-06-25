import re
from typing import Any, Dict, Tuple, Optional

from doctor_core.logging import log_doctor
from doctor_core.engine_manager import EngineManager


class DialogEngine:
    """
    PRO-Version der DialogEngine:
    - Verwaltet die Identität, Intent-Erkennung und semantische Analyse für DETO
    - Vollständig integriert in den EngineManager zur statusbasierten Interaktion mit Rico
    - Bietet saubere Schnittstellen für Telegram- und GUI-Schnittstellen
    """

    def __init__(self, engine_manager: EngineManager):
        self.engines = engine_manager
        
        # Lokaler Session-Kontext (kann bei Bedarf über 'state' persistiert werden)
        self.context: Dict[str, Any] = {}

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
        """Analysiert den eingehenden Text und klassifiziert die Absicht (Intent)."""
        t = text.lower().strip()

        # System / Heartbeat
        if t in ("ping", "alive", "bist du da"):
            return "ping"

        # Begrüßung
        if any(w in t for w in ["hallo", "hi", "moin", "servus"]):
            return "greeting"

        # Danke
        if any(w in t for w in ["danke", "thx"]):
            return "thanks"

        # Identity / Wer bin ich
        if any(w in t for w in ["wer bist du", "was bist du", "bist du echt", "was ist deto"]):
            return "identity"

        # Rolle / Funktion
        if any(w in t for w in ["was machst du", "wofür bist du da", "was ist deine funktion", "was ist deine rolle"]):
            return "role"

        # Fähigkeiten
        if any(w in t for w in ["was kannst du", "was sind deine aufgaben", "wo bist du gut drin"]):
            return "capabilities"

        # Queue-Befehlsstruktur
        if t.startswith("queue add"):
            return "queue_add"
        if t == "queue list":
            return "queue_list"
        if t == "queue clear":
            return "queue_clear"

        # Frageformen erkennen (Muster-Prüfung)
        if t.endswith("?"):
            return "question"

        if any(t.startswith(w) for w in ["wie ", "warum ", "wieso ", "was ", "wann ", "wo "]):
            return "question"

        # Standard-Chat/Fallback
        return "chat"

    # ---------------------------------------------------------
    # Parameter-Extraktion
    # ---------------------------------------------------------
    def extract_queue_add(self, text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Extrahiert die Pipe-separierten Parameter für Video-Queues."""
        try:
            payload = text[len("queue add "):].strip()
            parts = [p.strip() for p in payload.split("|")]

            video_path = parts[0] if len(parts) > 0 else None
            caption = parts[1] if len(parts) > 1 else ""
            scheduled_at = parts[2] if len(parts) > 2 else None

            return video_path, caption, scheduled_at
        except Exception as e:
            log_doctor(f"DialogEngine: Fehler beim Extrahieren der Queue-Parameter: {e}")
            return None, None, None

    # ---------------------------------------------------------
    # SEMANTISCHE TEXTANALYSE
    # ---------------------------------------------------------
    def analyze_question(self, text: str) -> str:
        """Klassifiziert das Themenfeld einer Frage für dynamische Antworten."""
        t = text.lower()

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

        return "general"

    # ---------------------------------------------------------
    # DYNAMISCHE ANTWORT GENERIERUNG
    # ---------------------------------------------------------
    def answer_question(self, text: str) -> str:
        """Generiert basierend auf der semantischen Analyse eine strukturierte Antwort."""
        topic = self.analyze_question(text)
        intro = self.personality["fallback_intro"]
        sig = self.personality["signature"]

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
                f"{sig}"
            )

        if topic == "tech":
            return (
                f"{intro}\n"
                f"Ich erkenne, dass es um ein technisches Thema geht.\n\n"
                "Meine Analyse:\n"
                "• Technische Probleme entstehen meist durch fehlende Parameter oder fehlerhafte Abläufe.\n"
                "• Ich kann dir helfen, Logs zu interpretieren oder Fehlerquellen einzugrenzen.\n"
                "• Wenn du mir den genauen Fehlertext gibst, kann ich dir eine präzise Lösung liefern.\n"
                "• Alternativ kann ich dir auch eine Debug-Strategie erstellen.\n"
                f"{sig}"
            )

        if topic == "decision":
            return (
                f"{intro}\n"
                f"Du willst eine Entscheidung treffen.\n\n"
                "Hier ist mein Ansatz:\n"
                "• Ich identifiziere zuerst die Optionen.\n"
                "• Dann bewerte ich Risiko, Aufwand und Nutzen.\n"
                "• Danach gebe ich dir eine klare Empfehlung.\n"
                "• Wenn du mir die Optionen nennst, entscheide ich für dich.\n"
                f"{sig}"
            )

        if topic == "explain":
            return (
                f"{intro}\n"
                f"Du willst etwas erklärt haben.\n\n"
                "So gehe ich vor:\n"
                "• Ich zerlege das Thema in einfache Bausteine.\n"
                "• Dann erkläre ich dir die Ursache.\n"
                "• Danach zeige ich dir, wie du es anwenden kannst.\n"
                "• Wenn du willst, mache ich dir ein Beispiel.\n"
                f"{sig}"
            )

        if topic == "help":
            return (
                f"{intro}\n"
                f"Ich erkenne, dass du Unterstützung brauchst.\n\n"
                "Mein Vorschlag:\n"
                "• Beschreibe mir kurz das Problem.\n"
                "• Ich analysiere es und gebe dir eine klare Lösung.\n"
                "• Wenn es technisch ist, kann ich dir Schritt-für-Schritt helfen.\n"
                "• Wenn es organisatorisch ist, strukturiere ich es für dich.\n"
                f"{sig}"
            )

        return (
            f"{intro}\n"
            f"Ich sehe, dass du eine allgemeine Frage stellst.\n\n"
            "Meine Einschätzung:\n"
            "• Ich kann dir helfen, das Thema einzuordnen.\n"
            "• Wenn du mir sagst, ob es um Technik, Geld, Projekte oder Entscheidungen geht, "
            "kann ich dir eine präzise Antwort geben.\n"
            "• Ich bin bereit, tiefer einzusteigen.\n"
            f"{sig}"
        )

    # ---------------------------------------------------------
    # HAUPT-ANTWORTLOGIK
    # ---------------------------------------------------------
    def generate_response(self, intent: str, result: Any = None) -> str:
        """Mappt den Intent auf das fertige Text-Template für den Endnutzer."""
        sig = self.personality["signature"]

        if intent == "ping":
            return "System läuft stabil. Ich bin bereit."

        if intent == "greeting":
            return "Ich bin da, Rico. Was steht an?"

        if intent == "thanks":
            return "Immer doch."

        if intent == "identity":
            return (
                "Ich bin DETO, dein Operator. "
                f"Ich analysiere, optimiere und automatisiere alles, was du mir gibst.\n{sig}"
            )

        if intent == "role":
            return (
                "Meine Rolle ist klar:\n"
                "• Operator: Systeme bauen, Fehler finden, Prozesse automatisieren.\n"
                "• Assistent: Projekte strukturieren und technische Aufgaben lösen.\n"
                "• Alpha‑Modus: Dich schneller machen.\n"
                f"{sig}"
            )

        if intent == "capabilities":
            return (
                f"Ich kann analysieren, automatisieren, optimieren, posten, planen, generieren "
                f"und Systeme stabil halten.\n{sig}"
            )

        if intent == "queue_add":
            if isinstance(result, dict) and "id" in result:
                return (
                    f"Post gespeichert:\n"
                    f"ID: {result['id']}\n"
                    f"Video: {result['video_path']}\n"
                    f"Caption: {result['caption']}\n"
                    f"Geplant: {result['scheduled_at']}\n"
                    f"{sig}"
                )
            return "Fehler beim Erstellen des Queue-Eintrags."

        if intent == "queue_list":
            return f"Aktuelle Video-Queue:\n{str(result)}"

        if intent == "queue_clear":
            return "Queue geleert."

        # Dynamische Fragen & Fallback Chat
        return self.answer_question(str(result) if result else "")