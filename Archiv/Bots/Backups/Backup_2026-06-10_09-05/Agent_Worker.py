import json
import os
import time
import datetime
import urllib.request
import urllib.parse
import Logik

AUFGABEN_DATEI = 'aufgaben.json'
BOT_TOKEN = "8982497382:AAHwEjHiw4J78rxYzApGfptINWEZemd6J3Y"
CHAT_ID_FILE = "last_chat_id.txt"

# Speichert das Datum des letzten automatischen Montags-Scouts, um Mehrfachsendungen zu verhindern
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
                print(f"📲 [RÜCKKANAL] Nachricht erfolgreich an Telegram gesendet.")
    except Exception as e:
        print(f"❌ [RÜCKKANAL] Fehler beim Senden an Telegram: {e}")

def verarbeite_aufgabe(task):
    befehl = task.get('befehl', 'UNBEKANNT')
    text = task.get('text', '')
    chat_id = task.get('chat_id')
    
    # Speichert die Chat-ID für den automatischen Montags-Report
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
    """Prüft im Hintergrund, ob Montag Morgen 08:00 Uhr ist und triggert den Scout."""
    global last_scout_date
    now = datetime.datetime.now()
    heute_str = now.strftime("%Y-%m-%d")
    
    # 0 = Montag, 8 = 08:00 bis 08:59 Uhr
    if now.weekday() == 0 and now.hour == 8 and heute_str != last_scout_date:
        if os.path.exists(CHAT_ID_FILE):
            with open(CHAT_ID_FILE, "r", encoding="utf-8") as f:
                saved_chat_id = f.read().strip()
            
            if saved_chat_id:
                print("📅 [AUTOMATION] Montag Morgen 08:00 Uhr! Starte automatischen Deutschland-Art-Scout...")
                bericht = Logik.run_art_scout()
                send_telegram_message(saved_chat_id, bericht)
                last_scout_date = heute_str  # Verhindert, dass er innerhalb der Stunde nochmal sendet

def main():
    print("🤖 Agent Worker (Mit Montags-Automation für ganz Deutschland) läuft...")
    
    while True:
        # 1. Prüfen, ob ein automatischer Report ansteht
        check_weekly_automation()
        
        # 2. Normale Aufgabenwarteschlange abarbeiten
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