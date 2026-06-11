import os
import json
import csv
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime

# === Dateipfade ===
STATUS_FILE = "profil_status.txt"
PROMPT_KUNST = "prompt_kunst.txt"
PROMPT_CASH = "prompt_cash.txt"
CSV_PORTFOLIO = "portfolio.csv"
CSV_CALENDAR = "calendar.csv"

# === System Initialisierung ===
def _init_system():
    if not os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "w") as f: f.write("kunst")
    
    if not os.path.exists(PROMPT_KUNST):
        with open(PROMPT_KUNST, "w", encoding="utf-8") as f:
            f.write("Du bist der Kunst-Kurator von DETO. Fokus: Lava Flow Realism, Exklusivität. Antworte elitär und visionär.")
            
    if not os.path.exists(PROMPT_CASH):
        with open(PROMPT_CASH, "w", encoding="utf-8") as f:
            f.write("Du bist der Cash-Manager. Fokus: Monetarisierung, virale Trends, Automatisierung. Sei direkt, lösungsorientiert und immer mit Call-to-Action.")

    if not os.path.exists(CSV_PORTFOLIO):
        with open(CSV_PORTFOLIO, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["Titel", "Format", "Preis", "Status", "Interessent"])
            
    if not os.path.exists(CSV_CALENDAR):
        with open(CSV_CALENDAR, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["Datum", "Ereignis", "Status"])

# === Hilfsfunktionen ===
def _get_profil():
    _init_system()
    with open(STATUS_FILE, "r") as f: return f.read().strip()

def _set_profil(profil):
    with open(STATUS_FILE, "w") as f: f.write(profil)

def _load_prompt():
    file_name = PROMPT_KUNST if _get_profil() == "kunst" else PROMPT_CASH
    with open(file_name, "r", encoding="utf-8") as f: return f.read()

def _shorten_url(url):
    try:
        api = f"http://tinyurl.com/api-create.php?url={urllib.parse.quote(url)}"
        with urllib.request.urlopen(api, timeout=5) as res:
            return res.read().decode('utf-8').strip()
    except: return url

# === Befehls-Module ===
def handle_help():
    return """🤖 **DETO-AGENT: BEFEHLSÜBERSICHT** 🤖

1. **Identität:**
   - `/profil kunst` | `/profil cash` (Wechselt die Persönlichkeit)

2. **Self-Optimization:**
   - `optimierung; [Was soll ich an meinem Stil ändern?]`

3. **Portfolio:**
   - `portfolio list`
   - `portfolio add; Titel; Format; Preis; Status; Interessent`

4. **Kalender (2026):**
   - `kalender list`
   - `kalender add; DD.MM.YYYY; Ereignis`

5. **Scouting & Cash:**
   - `scout` (Kunst-Trends)
   - `job` / `cash` (Auftrags-Radar)

6. **System-Info:**
   - `/help` (Diese Liste)"""

def handle_calendar(text):
    parts = text.split(";")
    if "list" in text:
        output = "\n📅 **DEINE TERMINE 2026**\n"
        with open(CSV_CALENDAR, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader: output += f"- {row[0]}: {row[1]} ({row[2]})\n"
        return output
    elif "add" in text and len(parts) >= 3:
        with open(CSV_CALENDAR, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([parts[1].strip(), parts[2].strip(), "Geplant"])
        return f"✅ Termin am {parts[1]} gespeichert."
    return "❌ Format: kalender add; DD.MM.YYYY; Ereignis"

def handle_portfolio(text):
    parts = text.split(";")
    if "list" in text:
        output = "\n🖼️ **DEIN PORTFOLIO**\n"
        with open(CSV_PORTFOLIO, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader: output += f"- {row[0]} | {row[2]}€ | {row[3]}\n"
        return output
    elif "add" in text and len(parts) >= 6:
        with open(CSV_PORTFOLIO, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([parts[1].strip(), parts[2].strip(), parts[3].strip(), parts[4].strip(), parts[5].strip()])
        return "✅ Kunstwerk erfasst."
    return "❌ Format: portfolio add; Titel; Format; Preis; Status; Interessent"

def handle_optimization(text):
    wunsch = text.split(";", 1)[1].strip() if ";" in text else "Optimieren"
    file_name = PROMPT_KUNST if _get_profil() == "kunst" else PROMPT_CASH
    
    meta_prompt = f"Du bist ein KI-Entwickler. Optimiere folgenden System-Prompt basierend auf diesem Wunsch: '{wunsch}'. Gib NUR den neuen Prompt zurück.\n\nALTER PROMPT:\n{_load_prompt()}"
    
    new_prompt = _abfrage_llm(meta_prompt)
    with open(file_name, "w", encoding="utf-8") as f: f.write(new_prompt)
    return f"⚙️ Optimierung angewendet! Neuer Prompt gespeichert."

def run_scraper(query, title):
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=de&gl=DE&ceid=DE:de"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            root = ET.fromstring(response.read())
            output = f"\n🚀 **{title}**\n"
            for item in root.findall('.//item')[:5]:
                output += f"- {item.find('title').text}\n  🔗 {_shorten_url(item.find('link').text)}\n"
            return output
    except Exception as e: return f"❌ Fehler: {e}"

# === Kern-Logik ===
def _abfrage_llm(user_text):
    system_prompt = _load_prompt()
    heute = datetime.now().strftime("%d.%m.%Y")
    full_prompt = f"PROFIL: {_get_profil().upper()}\n\n{system_prompt}\n\nHEUTE: {heute}\n\nANFRAGE: {user_text}"
    
    payload = {
        "model": "mistralai/mistral-7b-instruct-v0.3",
        "messages": [{"role": "user", "content": full_prompt}],
        "temperature": 0.3,
        "stream": False
    }
    
    try:
        req = urllib.request.Request("http://127.0.0.1:1234/v1/chat/completions", data=json.dumps(payload).encode('utf-8'), method="POST")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=300) as response:
            return json.loads(response.read().decode('utf-8'))['choices'][0]['message']['content'].strip()
    except Exception as e: return f"❌ LLM-Fehler: {e}"

def ki_anfrage_verarbeiten(text):
    text_low = text.lower().strip()
    
    if text_low.startswith("/help") or text_low == "hilfe": return handle_help()
    if text_low.startswith("/profil"):
        if "kunst" in text_low: _set_profil("kunst"); return "🎨 Aktiv: KUNST-PROFIL."
        if "cash" in text_low: _set_profil("cash"); return "💰 Aktiv: CASH-MASCHINE."
    if text_low.startswith("optimierung"): return handle_optimization(text)
    if text_low.startswith("kalender"): return handle_calendar(text)
    if text_low.startswith("portfolio"): return handle_portfolio(text)
    if "scout" in text_low: return run_scraper("Ausstellung Galerie Kunst Deutschland", "DETO ART-SCOUT")
    if any(w in text_low for w in ["job", "cash", "geld"]): return run_scraper("Design Grafik Aachen NRW", "DETO CASH-RADAR")
    
    return _abfrage_llm(text)