import json
import os
import time
import datetime
import urllib.request
import urllib.parse
import Logik

AUFGABEN_DATEI = 'aufgaben.json'
CHAT_ID_FILE = "last_chat_id.txt"
TOKEN_FILE = "token.txt"

# 1. Funktion zum sicheren Laden des Tokens
def get_token():
    if not os.path.exists(TOKEN_FILE):
        print(f"❌ FEHLER: {TOKEN_FILE} wurde im Ordner nicht gefunden!")
        return None
    with open(TOKEN_FILE, "r") as f:
        return f.read().strip()

BOT_TOKEN = get_token()

# Sicherheits-Check
if not BOT_TOKEN:
    print("❌ Start abgebrochen: Kein Token gefunden.")
    exit()

last_scout_date = ""

def send_telegram_message(chat_id, text):
    if not chat_id:
        return
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = urllib.parse.urlencode({'chat_id': chat_id, 'text': text}).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print(f"📲 [RÜCKKANAL] Nachricht erfolgreich gesendet.")
    except Exception as e:
        print(f"❌ [RÜCKKANAL] Fehler beim Senden an Telegram: {e}")

def verarbeite_aufgabe(task):
    befehl = task.get('befehl', 'UNBEKANNT')
    text = task.get('text', '')
    chat_id = task.get('chat_id')
    
    if chat_id:
        with open(CHAT_ID_FILE, "w", encoding="utf-8") as f:
            f.write(str(chat_id))

    ergebnis = None
    if befehl == "CHECK_SYSTEM":
        ergebnis = Logik.check_system()
    elif befehl == "KI_ANFRAGE":
        ergebnis = Logik.ki_anfrage_verarbeiten(text)
    else:
        ergebnis = f"❓ Unbekannter Befehl: {befehl}"

    if ergebnis:
        print(ergebnis)
        send_telegram_message(chat_id, ergebnis)

def check_weekly_automation():
    global last_scout_date
    now = datetime.datetime.now()
    heute_str = now.strftime("%Y-%m-%d")
    
    # 0 = Montag, 8 = 08:00 bis 08:59 Uhr
    if now.weekday() == 0 and now.hour == 8 and heute_str != last_scout_date:
        if os.path.exists(CHAT_ID_FILE):
            with open(CHAT_ID_FILE, "r", encoding="utf-8") as f:
                saved_chat_id = f.read().strip()
            
            if saved_chat_id:
                print("📅 [AUTOMATION] Montag Morgen! Starte automatischen Scout...")
                bericht = Logik.run_art_scout()
                send_telegram_message(saved_chat_id, bericht)
                last_scout_date = heute_str

def main():
    print("🤖 Agent Worker läuft und ist bereit...")
    
    while True:
        check_weekly_automation()
        
        if os.path.exists(AUFGABEN_DATEI) and os.path.getsize(AUFGABEN_DATEI) > 0:
            try:
                with open(AUFGABEN_DATEI, 'r', encoding='utf-8') as f:
                    tasks = json.load(f)
                
                if isinstance(tasks, list):
                    for task in tasks:
                        verarbeite_aufgabe(task)
                
                with open(AUFGABEN_DATEI, 'w', encoding='utf-8') as f:
                    json.dump([], f)
                print("--- Warteschlange geleert ---")
                    
            except Exception as e:
                print(f"❌ Fehler bei der Verarbeitung: {e}")
                with open(AUFGABEN_DATEI, 'w', encoding='utf-8') as f:
                    json.dump([], f)
        
        time.sleep(2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nWorker wurde beendet.")