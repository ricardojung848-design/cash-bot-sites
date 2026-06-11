import os
import json
import csv
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime

# === Konfiguration ===
PROMPT_FILE = "prompt_cash.txt"
CSV_PORTFOLIO = "portfolio.csv"
CSV_CALENDAR = "calendar.csv"

def _init_system():
    if not os.path.exists(PROMPT_FILE):
        with open(PROMPT_FILE, "w", encoding="utf-8") as f:
            f.write("Du bist der Cash-Manager. Fokus: Monetarisierung, virale Trends, Automatisierung.")
    if not os.path.exists(CSV_PORTFOLIO):
        with open(CSV_PORTFOLIO, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["Titel", "Format", "Preis", "Status", "Interessent"])
    if not os.path.exists(CSV_CALENDAR):
        with open(CSV_CALENDAR, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["Datum", "Ereignis", "Status"])

def _load_prompt():
    with open(PROMPT_FILE, "r", encoding="utf-8") as f: return f.read()

def _shorten_url(url):
    try:
        api = f"http://tinyurl.com/api-create.php?url={urllib.parse.quote(url)}"
        with urllib.request.urlopen(api, timeout=5) as res:
            return res.read().decode('utf-8').strip()
    except: return url

def handle_help():
    return "💰 **CASH-BOT: BEFEHLSÜBERSICHT**\n\n- `kalender list` / `kalender add; DD.MM.YYYY; Ereignis`\n- `portfolio list` / `portfolio add; ...`\n- `scout` (Trends)\n- `cash` (Einkommens-Radar)"

# ... (Hier den Rest der Funktionen handle_calendar, handle_portfolio, run_scraper, _abfrage_llm wie gehabt einfügen) ...

def ki_anfrage_verarbeiten(text):
    text_low = text.lower().strip()
    if text_low.startswith("/help"): return handle_help()
    if text_low.startswith("kalender"): return handle_calendar(text)
    if text_low.startswith("portfolio"): return handle_portfolio(text)
    if "scout" in text_low: return run_scraper("Passive Income Business Trends", "CASH-SCOUT")
    if any(w in text_low for w in ["job", "cash", "geld"]): return run_scraper("Business Automation NRW", "CASH-RADAR")
    
    return _abfrage_llm(text)