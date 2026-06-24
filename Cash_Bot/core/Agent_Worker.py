# core/Agent_Worker.py

import os
import time
from datetime import datetime

from core.utils import (
    BASE_DIR,
    load_json,
    save_json,
    log_worker,
    warn_worker,
    error_worker,
)

from core.Logik import (
    process_ki_anfrage,
    auto_posting_tick,
)

AUFGABEN_DATEI = os.path.join(BASE_DIR, "aufgaben.json")
RUECKGABE_DATEI = os.path.join(BASE_DIR, "rueckgabe.json")


# ---------------------------------------------------------
# Aufgabe laden
# ---------------------------------------------------------
def lade_aufgabe():
    tasks = load_json(AUFGABEN_DATEI, [])
    if not tasks:
        return None

    task = tasks.pop(0)
    save_json(AUFGABEN_DATEI, tasks)
    return task


# ---------------------------------------------------------
# Antwort speichern
# ---------------------------------------------------------
def speichere_antwort(chat_id, antwort):
    save_json(RUECKGABE_DATEI, {
        "chat_id": chat_id,
        "antwort": antwort
    })
    log_worker(f"Antwort gespeichert für Chat {chat_id}")


# ---------------------------------------------------------
# Worker Loop
# ---------------------------------------------------------
def worker_loop():
    log_worker("Agent Worker gestartet...")

    while True:
        try:
            # Auto-Posting Tick
            auto_posting_tick()

            # Aufgabe prüfen
            task = lade_aufgabe()
            if not task:
                time.sleep(0.2)
                continue

            chat_id = task.get("chat_id")
            befehl = task.get("befehl")
            text = task.get("text")

            log_worker(f"Aufgabe empfangen: {befehl} | Chat {chat_id}")

            # KI-Anfrage
            if befehl == "KI_ANFRAGE":
                antwort = process_ki_anfrage(text)
                speichere_antwort(chat_id, antwort)
                continue

            # Systemcheck
            if befehl == "CHECK_SYSTEM":
                speichere_antwort(chat_id, "System läuft stabil.")
                continue

            # Architektur / Code / Run / Logbuch (Platzhalter)
            if befehl in ("ARCHITEKT", "RUN", "LOGBUCH"):
                speichere_antwort(chat_id, f"Befehl '{befehl}' ist noch nicht implementiert.")
                continue

        except Exception as e:
            error_worker(f"Fehler im Worker: {e}")

        time.sleep(0.2)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
if __name__ == "__main__":
    worker_loop()
