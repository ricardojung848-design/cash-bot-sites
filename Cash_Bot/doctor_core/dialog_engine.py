import re
import datetime
from doctor_core.process_manager import AgentProcessManager
from doctor_core.aegis_storage import AegisStorage

class AegisDialogEngine:
    def __init__(self, engine_manager):
        self.engines = engine_manager
        self.storage = AegisStorage()
        self.pm = AgentProcessManager(engine_manager)

    def process_command(self, text: str) -> str:
        """Analysiert den Text des Users und führt die passende Aktion aus"""
        cmd = text.lower().strip()

        if not cmd:
            return "Ich höre zu, Sir. Wie kann ich Aegis OS für Sie steuern?"

        # 1. BEREICH: PROZESS-STEUERUNG (AGENTEN STARTEN / STOPPEN)
        if "starte" in cmd or "hochfahren" in cmd or "open" in cmd:
            if "worker" in cmd:
                res = self.pm.start_agent("Agent_Worker", "core/Agent_Worker.py")
                return "Haupt-Worker-Agent wird im Hintergrund hochgefahren, Sir." if res == "SUCCESS" else f"Fehler: {res}"
            elif "telegram" in cmd or "bot" in cmd:
                res = self.pm.start_agent("Telegram_Bot", "core/Agent_Telegram.py")
                return "Telegram-Bot-Schnittstelle wird gestartet." if res == "SUCCESS" else f"Fehler: {res}"
            
        if "stoppe" in cmd or "beende" in cmd or "kill" in cmd:
            if "worker" in cmd:
                self.pm.stop_agent("Agent_Worker")
                return "Agent_Worker wurde erfolgreich terminiert."
            elif "telegram" in cmd or "bot" in cmd:
                self.pm.stop_agent("Telegram_Bot")
                return "Telegram-Bot wurde angehalten."
            elif "alle" in cmd or "alles" in cmd:
                self.pm.stop_all()
                return "Zentraler Not-Aus ausgeführt. Alle Agenten-Prozesse wurden beendet."

        # 2. BEREICH: AUFGABEN & ERLEDIGUNGEN
        if "aufgabe" in cmd or "todo" in cmd or "erledigung" in cmd:
            if "hinzufügen" in cmd or "erstelle" in cmd or "merke" in cmd:
                # Extrahiere die Aufgabe nach dem Schlüsselwort
                match = re.search(r"(?:merke|erstelle|aufgabe)\s+(?:dass|zu)?\s*(.*)", cmd, re.IGNORECASE)
                if match:
                    task_title = match.group(1).strip()
                    self.storage.add_task(task_title.capitalize())
                    return f"Erledigung wurde in die Task-Datenbank eingetragen: '{task_title.capitalize()}'"
            
            # Aufgaben abrufen
            tasks = self.storage.get_all_tasks()
            if not tasks:
                return "Ihre To-Do-Liste ist aktuell komplett leer, Sir. Hervorragende Arbeit."
            
            reply = "Hier sind Ihre aktuellen Aufgaben:\n"
            for t in tasks[:5]: # Die neuesten 5 anzeigen
                status_icon = "🟩" if t[2] == "OPEN" else "✅"
                reply += f"{status_icon} ID #{t[0]}: {t[1]}\n"
            return reply

        # 3. BEREICH: SMALLTALK / SYSTEM-STATUS
        if "wer bist du" in cmd:
            return "Ich bin AEGIS – Ihre kognitive Kommando-Zentrale. Ich überwache Ihre Agenten und verwalte Ihre Produktivität."
        
        if "status" in cmd or "wie läuft" in cmd:
            statuses = self.pm.get_statuses()
            if not statuses:
                return "Alle Agenten-Systeme schlafen aktuell. Keine aktiven Prozesse registriert."
            return f"Live-Telemetrie der Prozesse: {statuses}"

        # Standard-Fallback falls die KI den Befehl erweitern muss
        return f"Ich habe '{text}' verstanden, aber dieses Modul ist noch nicht vollständig verknüpft. Soll ich eine Aufgabe daraus erstellen?"