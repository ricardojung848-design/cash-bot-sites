import os
import re
import shutil
import datetime
import ollama

MODUL_ORDNER = "Module"
ARCHIV_ORDNER = "Archiv"

def architekt_repariere_modul(name, fehler_meldung):
    pfad = os.path.join(MODUL_ORDNER, f"{name}.py")
    
    # Automatische Bau-Anweisungen für unsere Werkzeuge
    if name == "Gedaechtnis":
        code = """import sqlite3
def run_modul(): return "Gedächtnis aktiv."
def speichern(k, v):
    conn = sqlite3.connect("gedaechtnis.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS erinnerungen (key TEXT PRIMARY KEY, value TEXT)")
    c.execute("INSERT OR REPLACE INTO erinnerungen (key, value) VALUES (?, ?)", (k, v))
    conn.commit(); conn.close()
def abrufen(k):
    conn = sqlite3.connect("gedaechtnis.db")
    c = conn.cursor()
    c.execute("SELECT value FROM erinnerungen WHERE key = ?", (k,))
    r = c.fetchone(); conn.close()
    return r[0] if r else "Keine Erinnerung."
"""
        with open(pfad, "w", encoding="utf-8") as f: f.write(code)
        return True
        
    if name == "Suche":
        code = """from duckduckgo_search import DDGS
def run_modul(): return "Suchmodul bereit."
def suche(begriff):
    with DDGS() as ddgs:
        ergebnisse = list(ddgs.text(begriff, max_results=3))
        if not ergebnisse: return "Nichts gefunden."
        return "\\n".join([f"{r['title']}: {r['href']}" for r in ergebnisse])
"""
        with open(pfad, "w", encoding="utf-8") as f: f.write(code)
        return True

    # Standard-Reparatur
    prompt = f"Repariere '{name}'. NUR 'def run_modul():'. Fehler: {fehler_meldung}. Antworte NUR mit Code."
    try:
        res = ollama.generate(model="deto_agent", prompt=prompt)
        match = re.search(r"```python\s*(.*?)\s*```", res['response'], re.DOTALL)
        if match:
            with open(pfad, "w", encoding="utf-8") as f: f.write(match.group(1).strip())
            return True
        return False
    except: return False

def verbessere_modul(name):
    pfad = os.path.join(MODUL_ORDNER, f"{name}.py")
    if not os.path.exists(pfad): return "Modul existiert nicht."
    if not os.path.exists(ARCHIV_ORDNER): os.makedirs(ARCHIV_ORDNER)
    shutil.copy(pfad, os.path.join(ARCHIV_ORDNER, f"{name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py"))
    with open(pfad, "r", encoding="utf-8") as f: code = f.read()
    prompt = f"Optimiere diesen Code. KEINE KLASSEN. NUR 'def run_modul():'. Code:\n{code}"
    try:
        res = ollama.generate(model="deto_agent", prompt=prompt)
        match = re.search(r"```python\s*(.*?)\s*```", res['response'], re.DOTALL)
        if match:
            with open(pfad, "w", encoding="utf-8") as f: f.write(match.group(1).strip())
            return "Update erfolgreich!"
        return "Update fehlgeschlagen."
    except Exception as e: return f"Fehler: {e}"