import json
import os
import time
import datetime
import urllib.request
import urllib.parse
import Logik

# === KONFIGURATION ===
AUFGABEN_DATEI = "aufgaben.json"
CHAT_ID_FILE = "last_chat_id.txt"
TOKEN_FILE = "token.txt"
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)


# === LOGGING ===
def log(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(os.path.join(LOG_DIR, "worker.log"), "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass


# === TOKEN LADEN ===
def get_token():
    if not os.path.exists(TOKEN_FILE):
        log("⚠️ Kein TOKEN_FILE gefunden.")
        return None
    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()


BOT_TOKEN = get_token()


# === TELEGRAM SENDEN ===
def send_telegram_message(chat_id, text):
    if not chat_id or not BOT_TOKEN:
        log("⚠️ Konnte keine Telegram-Nachricht senden (fehlende chat_id oder BOT_TOKEN).")
        return
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = urllib.parse.urlencode(
            {"chat_id": chat_id, "text": text}
        ).encode("utf-8")
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10):
            pass
    except Exception as e:
        log(f"❌ [RÜCKKANAL] Fehler beim Senden: {e}")


# === CHAT-ID SPEICHERN ===
def speichere_chat_id(chat_id):
    if not chat_id:
        return
    try:
        with open(CHAT_ID_FILE, "w", encoding="utf-8") as f:
            f.write(str(chat_id))
    except Exception as e:
        log(f"⚠️ Konnte CHAT_ID nicht speichern: {e}")


def lade_chat_id():
    if not os.path.exists(CHAT_ID_FILE):
        return None
    try:
        with open(CHAT_ID_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except:
        return None


# === AUFGABEN VERARBEITEN ===
def verarbeite_aufgabe(task: dict):
    befehl = task.get("befehl", "UNBEKANNT")
    text = task.get("text", "")
    chat_id = task.get("chat_id") or lade_chat_id()

    if chat_id:
        speichere_chat_id(chat_id)

    log(f"📥 Neue Aufgabe: {befehl} | Text: {text} | Chat: {chat_id}")

    try:
        # SYSTEM CHECK
        if befehl == "CHECK_SYSTEM":
            antwort = "✅ System läuft stabil."
            send_telegram_message(chat_id, antwort)

        # KI-ANFRAGE → NEUE FUNKTION!
        elif befehl == "KI_ANFRAGE":
            antwort = Logik.process_ki_anfrage(text)
            send_telegram_message(chat_id, antwort)

        # FABRIK (falls du später wieder Sheets nutzt)
        elif befehl == "FABRIK":
            send_telegram_message(chat_id, "🏭 Fabrik ist aktuell deaktiviert.")

        # UNBEKANNT
        else:
