import os
import json
import csv
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime

# === Konfiguration ===
PROMPT_FILE = "prompt_kunst.txt"
CSV_PORTFOLIO = "portfolio.csv"
CSV_CALENDAR = "calendar.csv"

def _init_system():
    if not os.path.exists(PROMPT_FILE):
        with open(PROMPT_FILE, "w", encoding="utf-8") as f:
            f.write("Du bist der Kunst-Kurator. Fokus: Lava Flow Realism, Exklusivität.")
    # ... (Rest der Initialisierung wie oben)

def _load_prompt():
    with open(PROMPT_FILE, "r", encoding="utf-8") as f: return f.read()

# ... (Hier die Funktionen _shorten_url, handle_calendar, handle_portfolio, run_scraper, _abfrage_llm einfügen) ...

def ki_anfrage_verarbeiten(text):
    text_low = text.lower().strip()
    if text_low.startswith("/help"): return "🎨 **KUNST-BOT: BEFEHLSÜBERSICHT**\n\n- `portfolio list`\n- `kalender list`\n- `scout` (Galerie-Trends)"
    if text_low.startswith("kalender"): return handle_calendar(text)
    if text_low.startswith("portfolio"): return handle_portfolio(text)
    if "scout" in text_low: return run_scraper("Ausstellung Galerie Kunst Deutschland", "ART-SCOUT")
    
    return _abfrage_llm(text)