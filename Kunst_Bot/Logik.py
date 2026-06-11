import os
import csv

# === Konfiguration ===
PROMPT_FILE = "prompt_kunst.txt"
CSV_PORTFOLIO = "portfolio.csv" # Hier für Kunstwerke
CSV_CALENDAR = "calendar.csv"   # Hier für Ausstellungen

# Initialisierung der Dateien
def _init_system():
    if not os.path.exists(PROMPT_FILE):
        with open(PROMPT_FILE, "w", encoding="utf-8") as f:
            f.write("Du bist der Kunst-Kurator. Fokus: Lava Flow Realism, Exklusivität, Analyse von Galerie-Trends.")
    if not os.path.exists(CSV_PORTFOLIO):
        with open(CSV_PORTFOLIO, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["Titel", "Stil", "Status", "Preis/Wert"])
    if not os.path.exists(CSV_CALENDAR):
        with open(CSV_CALENDAR, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["Datum", "Ausstellung", "Ort"])

_init_system() # Sofort ausführen beim Laden

# --- Hilfsfunktionen ---
def _load_prompt():
    with open(PROMPT_FILE, "r", encoding="utf-8") as f: return f.read()

def _abfrage_llm(text):
    prompt = _load_prompt()
    return f"🎨 [KUNST-KURATOR MODUS]\nAnalyse: '{text}'\n(Prompt aktiv: {prompt[:30]}...)\nDie KI bewertet nun deinen Kunst-Input."

# --- Modul: Kalender (Ausstellungen) ---
def handle_calendar(text):
    if "list" in text:
        if not os.path.exists(CSV_CALENDAR): return "Kalender ist leer."
        with open(CSV_CALENDAR, "r", encoding="utf-8") as f:
            return "📅 AUSSTELLUNGS-KALENDER:\n" + f.read()
    elif "add" in text:
        parts = text.split(";")
        if len(parts) >= 3:
            with open(CSV_CALENDAR, "a", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow([parts[1].strip(), parts[2].strip(), "geplant"])
            return f"✅ Ausstellung '{parts[2].strip()}' für den {parts[1].strip()} vorgemerkt."
    return "❓ Unbekannter Kalender-Befehl."

# --- Modul: Portfolio (Werke) ---
def handle_portfolio(text):
    if "list" in text:
        if not os.path.exists(CSV_PORTFOLIO): return "Portfolio ist leer."
        with open(CSV_PORTFOLIO, "r", encoding="utf-8") as f:
            return "🖼️ KUNST-PORTFOLIO:\n" + f.read()
    elif "add" in text:
        parts = text.split(";")
        if len(parts) >= 4:
            with open(CSV_PORTFOLIO, "a", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow([parts[1].strip(), parts[2].strip(), parts[3].strip(), "unbekannt"])
            return "✅ Werk zum Portfolio hinzugefügt."
    return "❓ Unbekannter Portfolio-Befehl."

# --- Modul: Scout ---
def run_scraper(suchbegriff, typ):
    return f"🔍 [ART-SCOUT]: Suche nach '{suchbegriff}' in der Kunstwelt...\n(Agent kuratiert gerade neue Trends für dich!)"

def check_system():
    return "✅ Systemstatus: Kunst-Kurator ist online. Lava Flow Realism bereit."

# --- Haupt-Verteiler ---
def ki_anfrage_verarbeiten(text):
    text_low = text.lower().strip()
    if text_low.startswith("/help"): return handle_help()
    if text_low.startswith("kalender"): return handle_calendar(text)
    if text_low.startswith("portfolio"): return handle_portfolio(text)
    if "scout" in text_low: return run_scraper("Ausstellung Galerie Kunst Deutschland", "ART-SCOUT")
    
    return _abfrage_llm(text)

def handle_help():
    return "🎨 **KUNST-BOT: BEFEHLSÜBERSICHT**\n\n- `kalender list` / `kalender add; Datum; Event`\n- `portfolio list` / `portfolio add; Titel; Stil; Status`\n- `scout` (Galerie-Trends)"