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
        elif befehl == "