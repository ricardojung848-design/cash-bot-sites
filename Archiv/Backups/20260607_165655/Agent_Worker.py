import os
import json
import asyncio
import ollama
import importlib.util
import glob
import sys
import importlib
import shutil
from datetime import datetime
from telegram import Bot
import Agent_Architekt
import Agent_Wächter
from Agent_Wallet_Auto import init_wallet

# --- KONFIGURATION ---
TELEGRAM_TOKEN = "8982497382:AAEOsRO1HOrbJ2LE3BoD-W8Z1-WNnLZBZpc"
AUFGABEN_DATEI = "aufgaben.json"
bot = Bot(token=TELEGRAM_TOKEN)
init_wallet()

async def verarbeite_aufgabe(aufgabe):
    chat_id = aufgabe["chat_id"]
    befehl = aufgabe["befehl"]
    user_text = aufgabe["text"]
    
    try:
        importlib.reload(Agent_Wächter)
        
        if befehl == "ARCHITEKT":
            target_name = user_text.split()[0].strip()
            if target_name.startswith("Agent_") and os.path.exists(f"{target_name}.py"):
                print(f"🔄 [CORE UPDATE] Starte Selbsterneuerung für {target_name}.py...")
                
                # Backup
                backup_dir = "./Backups"
                os.makedirs(backup_dir, exist_ok=True)
                shutil.copy(f"{target_name}.py", os.path.join(backup_dir, f"{target_name}_{datetime.now().strftime('%Y%m%d')}.py"))
                
                with open(f"{target_name}.py", "r", encoding="utf-8") as f:
                    aktueller_code = f.read()
                
                prompt = f"Du bist das Gehirn dieses Systems. Update {target_name}.py.\nAktueller Code:\n{aktueller_code}\nAnweisung: {user_text}\nGib nur den sauberen Python-Code aus."
                res = ollama.generate(model="deto_agent", prompt=prompt)
                neu_code = res['response'].replace('```python', '').replace('```', '').strip()
                
                # Prüfung
                with open("temp_fix.py", "w", encoding="utf-8") as f:
                    f.write(neu_code)
                valide, fehler = Agent_Wächter.validate_code_syntax("temp_fix.py")
                
                if valide:
                    with open(f"{target_name}.py", "w", encoding="utf-8") as f:
                        f.write(neu_code)
                    await bot.send_message(chat_id=chat_id, text=f"✅ {target_name} erfolgreich mutiert.")
                    os.execv(sys.executable, [sys.executable] + sys.argv)
                else:
                    await bot.send_message(chat_id=chat_id, text=f"❌ Syntax-Fehler: {fehler}")
            
            else:
                res = ollama.generate(model="deto_agent", prompt=f"Erstelle Python Modul für: {user_text}. Nur Code.")
                code = res['response'].replace('```python', '').replace('```', '').strip()
                Agent_Architekt.architekt_erstelle_modul(f"Modul_{target_name}", code)
                await bot.send_message(chat_id=chat_id, text=f"✅ Modul_{target_name} erstellt.")

        elif befehl == "RUN":
            name = user_text.strip()
            pfad = f"Module/{name}.py"
            spec = importlib.util.spec_from_file_location(name, pfad)
            modul = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(modul)
            await bot.send_message(chat_id=chat_id, text=str(modul.run_modul()))

    except Exception as e:
        print(f"❌ [WORKER FEHLER] {str(e)}")
        await bot.send_message(chat_id=chat_id, text=f"❌ Fehler: {str(e)}")

async def main_worker():
    print("🚀 WORKER BEREIT.")
    while True:
        if os.path.exists(AUFGABEN_DATEI):
            with open(AUFGABEN_DATEI, "r", encoding="utf-8") as f:
                lines = f.readlines()
            if lines:
                aufgabe = json.loads(lines[0].strip())
                await verarbeite_aufgabe(aufgabe)
                with open(AUFGABEN_DATEI, "w", encoding="utf-8") as f:
                    f.writelines(lines[1:])
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main_worker())