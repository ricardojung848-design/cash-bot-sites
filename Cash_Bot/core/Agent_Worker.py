import os
import json
import time
import datetime
import traceback

# === PFAD BASIS ===
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CORE_DIR = os.path.join(BASE_DIR, "core")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

AUFGABEN_DATEI = os.path.join(BASE_DIR, "aufgaben.json")
WORKER_LOG = os.path.join(LOGS_DIR, "worker.log")

os.makedirs(LOGS_DIR, exist_ok=True)

# === LOGGING ===
def log(level, msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    try:
        with open(WORKER_LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

def info(msg): log("INFO", msg)
def warn(msg): log("WARN", msg)
def error(msg): log("ERROR", msg)


# === KI-LOGIK LADEN ===
try:
    from core.Logik import process_ki_anfrage
    info("Logik erfolgreich geladen.")
except Exception as e:
    error(f"Fehler beim Laden der Logik: {e}")
    traceback.print_exc()
    time.sleep(3)
    exit()


# === AUFGABEN LADEN ===
def load_tasks():
    if not os.path.exists(AUFGABEN_DATEI):
        return []

    try:
        with open(AUFGABEN_DATEI, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        warn("Konnte Aufgaben-Datei nicht lesen – JSON fehlerhaft.")
        return []


# === AUFGABEN SPEICHERN ===
def save_tasks(tasks):
    try:
        with open(AUFGABEN_DATEI, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=4, ensure_ascii=False)
    except Exception as e:
        error(f"Fehler beim Speichern der Aufgaben: {e}")


# === AUFGABE VERARBEITEN ===
def process_task(task):
    chat_id = task["chat_id"]
    befehl = task["befehl"]
    text = task["text"]

    info(f"Verarbeite Aufgabe: {befehl} | Chat {chat_id}")

    try:
        if befehl == "KI_ANFRAGE":
            antwort = process_ki_anfrage(text)
        elif befehl == "CHECK_SYSTEM":
            antwort = "System läuft stabil."
        elif befehl == "ARCHITEKT":
            antwort = "Architekt-Modus aktiviert."
        elif befehl == "RUN":
            antwort = "RUN-Befehl ausgeführt."
        elif befehl == "LOGBUCH":
            antwort = "Logbuch wird übertragen."
        else:
            antwort = f"Unbekannter Befehl: {befehl}"

        info(f"Antwort erzeugt: {antwort}")

    except Exception as e:
        error(f"Fehler bei der Verarbeitung: {e}")
        traceback.print_exc()
        antwort = f"❌ Fehler bei der Verarbeitung: {e}"

    return antwort


# === MAIN LOOP ===
def main():
    info("Worker gestartet und wartet auf Aufgaben...")

    while True:
        tasks = load_tasks()

        if not tasks:
            time.sleep(1)
            continue

        task = tasks.pop(0)
        antwort = process_task(task)

        # Antwort speichern für Telegram (Worker schreibt Rückgabe)
        rueckgabe_datei = os.path.join(BASE_DIR, "rueckgabe.json")
        with open(rueckgabe_datei, "w", encoding="utf-8") as f:
            json.dump({"chat_id": task["chat_id"], "antwort": antwort}, f, indent=4, ensure_ascii=False)

        save_tasks(tasks)
        info("Aufgabe abgeschlossen.\n")

        time.sleep(0.5)


if __name__ == "__main__":
    main()
