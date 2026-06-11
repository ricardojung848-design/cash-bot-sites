import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "agent_logbuch.txt")

def log_aktion(bereich, details):
    """Schreibt eine neue Aktion mit Zeitstempel in die Textdatei."""
    zeit = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    eintrag = f"[{zeit}] [{bereich}] {details}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(eintrag)
        print(eintrag.strip())
    except Exception as e:
        print(f"Fehler beim Schreiben ins Logbuch: {e}")

def get_logbuch():
    """Liest die letzten Zeilen des Logbuchs für Telegram aus."""
    if not os.path.exists(LOG_FILE):
        return "Das Logbuch ist aktuell noch leer."
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            zeilen = f.readlines()
            # Die letzten 15 Einträge zurückgeben, damit es in Telegram übersichtlich bleibt
            return "".join(zeilen[-15:])
    except Exception as e:
        return f"Fehler beim Lesen des Logbuchs: {e}"