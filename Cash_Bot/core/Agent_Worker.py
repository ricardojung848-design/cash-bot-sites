import os
import time
import json
import traceback
from datetime import datetime

# === interne Utils ===
from core.utils import (
    BASE_DIR,
    LOGS_DIR,
    load_json,
    save_json,
    log_worker,
    warn_worker,
    error_worker,
)

# === Systemstruktur-Manager ===
from core.SystemStructureManager import SystemStructureManager

# === Logik ===
from core.Logik import process_ki_anfrage


# === PFAD ZU AUFGABEN & RÜCKGABE ===
AUFGABEN_DATEI = os.path.join(BASE_DIR, "aufgaben.json")
RUECKGABE_DATEI = os.path.join(BASE_DIR, "rueckgabe.json")


# === AUFGABEN LADEN ===
def load_tasks():
    tasks = load_json(AUFGABEN_DATEI, [])
    if not isinstance(tasks, list):
        warn_worker("Aufgaben-Datei war beschädigt – neu initialisiert.")
        tasks = []
        save_json(AUFGABEN_DATEI, tasks)
    return tasks


# === AUFGABEN SPEICHERN ===
def save_tasks(tasks):
    save_json(AUFGABEN_DATEI, tasks)


# === EINZELNE AUFGABE VERARBEITEN ===
def process_task(task):
    chat_id = task.get("chat_id")
    befehl = task.get("befehl")
    text = task.get("text")

    log_worker(f"Verarbeite Aufgabe: {befehl} | Chat {chat_id}")

    try:
        # KI-Anfrage
        if befehl == "KI_ANFRAGE":
            antwort = process_ki_anfrage(text)

        # Systemcheck
        elif befehl == "CHECK_SYSTEM":
            antwort = "System läuft stabil."

        # Architekt-Modus
        elif befehl == "ARCHITEKT":
            antwort = "Architekt-Modus aktiviert."

        # RUN
        elif befehl == "RUN":
            antwort = "RUN-Befehl ausgeführt."

        # Logbuch
        elif befehl == "LOGBUCH":
            antwort = "Logbuch wird übertragen."

        else:
            antwort = f"Unbekannter Befehl: {befehl}"

        log_worker(f"Antwort erzeugt: {antwort}")

    except Exception as e:
        error_worker(f"Fehler bei der Verarbeitung: {e}")
        traceback.print_exc()
        antwort = f"❌ Fehler bei der Verarbeitung: {e}"

    return {"chat_id": chat_id, "antwort": antwort}


# === RÜCKGABE SCHREIBEN ===
def write_response(response):
    save_json(RUECKGABE_DATEI, response)
    log_worker("Antwort für Telegram gespeichert.")


# === MAIN LOOP ===
def main():
    log_worker("Worker wird gestartet...")

    # === Systemstruktur prüfen ===
    manager = SystemStructureManager()
    status = manager.run_full_check()
    log_worker(status)

    log_worker("Worker bereit. Warte auf Aufgaben...")

    while True:
        tasks = load_tasks()

        if not tasks:
            time.sleep(0.5)
            continue

        # Erste Aufgabe entnehmen
        task = tasks.pop(0)

        # Verarbeiten
        response = process_task(task)

        # Rückgabe speichern
        write_response(response)

        # Aufgabenliste aktualisieren
        save_tasks(tasks)

        log_worker("Aufgabe abgeschlossen.\n")
        time.sleep(0.3)


if __name__ == "__main__":
    main()
