import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Sicherstellen, dass das Root-Verzeichnis im Systempfad liegt
base_dir = Path(__file__).resolve().parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

# Modernisierte Core-Imports
from doctor_core.logging import log_doctor
from doctor_core.engine_manager import EngineManager
from modules.fabrik_engine import FabrikEngine

# Importe aus deinen bestehenden Core-Modulen
from core.utils import BASE_DIR, load_json, save_json
from core.Logik import process_ki_anfrage, auto_posting_tick

# Definition der JSON-Dateipfade im Dateisystem
AUFGABEN_DATEI = os.path.join(BASE_DIR, "aufgaben.json")
RUECKGABE_DATEI = os.path.join(BASE_DIR, "rueckgabe.json")


def lade_aufgabe():
    """Lädt die älteste Aufgabe aus der JSON-Warteschlange (FIFO) und aktualisiert die Datei."""
    tasks = load_json(AUFGABEN_DATEI, [])
    if not tasks:
        return None

    task = tasks.pop(0)
    save_json(AUFGABEN_DATEI, tasks)
    return task


def speichere_antwort(chat_id, antwort):
    """Schreibt das Verarbeitungsergebnis für das Telegram-Interface in die Rückgabe-JSON."""
    save_json(RUECKGABE_DATEI, {
        "chat_id": chat_id,
        "antwort": antwort
    })
    log_doctor(f"AgentWorker: Antwort gespeichert für Chat {chat_id}")


def worker_loop():
    """
    Zentrale, ununterbrochene Hauptschleife des Agent Workers.
    Überwacht Aufgaben, steuert Intervalle und delegiert an angeschlossene Engines.
    """
    log_doctor("Agent Worker (PRO-Version) gestartet...")

    # 1. EngineManager & asynchronen Thread-Pool (Fabrik) initialisieren
    manager = EngineManager()
    fabrik = FabrikEngine(manager)
    manager.register("fabrik", fabrik)

    # 2. Threads für parallele Hintergrund-Logiken (z.B. Video-Rendern, Uploads) aktivieren
    log_doctor(fabrik.start())

    while True:
        try:
            # Automatisches Posting-Intervall prüfen (Übergibt jetzt den zentralen Manager)
            auto_posting_tick(manager)

            # Neue Aufgabe aus der JSON-Zentrale holen
            task = lade_aufgabe()
            if not task:
                time.sleep(0.2)
                continue

            chat_id = task.get("chat_id")
            befehl = task.get("befehl")
            text = task.get("text")

            log_doctor(f"📋 Aufgabe empfangen: {befehl} | Chat {chat_id}")

            # --- BEFEHLSVERARBEITUNG ---
            
            if befehl == "KI_ANFRAGE":
                # Verarbeitet die Anfrage über die bestehende Core-Logik
                antwort = process_ki_anfrage(text)
                speichere_antwort(chat_id, antwort)
                continue

            if befehl == "CHECK_SYSTEM":
                # Kombiniert den Standard-Text mit den Echtzeitmetriken des Thread-Pools
                status_msg = "System läuft stabil.\n\n" + fabrik.get_status_summary()
                speichere_antwort(chat_id, status_msg)
                continue

            if befehl in ("ARCHITEKT", "RUN", "LOGBUCH"):
                speichere_antwort(chat_id, f"Befehl '{befehl}' ist noch nicht implementiert.")
                continue

            # Unbekannte Befehle abfangen, damit die Schleife nicht blockiert
            log_doctor(f"AgentWorker-Warnung: Unbekannter Befehl ignoriert: {befehl}")

        except Exception as e:
            # Nutzt das modernisierte Logging-System für kritische Fehlerzustände
            log_doctor(f"AgentWorker-Kritisch: Fehler im Worker-Loop: {e}")

        time.sleep(0.2)


if __name__ == "__main__":
    try:
        worker_loop()
    except KeyboardInterrupt:
        log_doctor("Agent Worker manuell über Terminal gestoppt.")