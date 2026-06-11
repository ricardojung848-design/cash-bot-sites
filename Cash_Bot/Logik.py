import os
import json
import subprocess
import requests
import csv
import io
from datetime import datetime

# === KONFIGURATION ===
# Dein Google Sheet ist jetzt direkt verbunden!
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRdlTbob3aK0v7xyUtKn__RymdItFQmOqcV1Q6_74w3Frn8fORnIbSnVIJey_uZ5LT1C4f9yD3HOAPO/pub?output=csv"
DATA_DIR = "scraped_data"
OUTPUT_DIR = "generated_content"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- CSS DESIGN ---
SHARED_CSS = """
:root { --bg-color: #0f172a; --card-bg: #1e293b; --text-main: #f8fafc; --accent: #38bdf8; --cta-bg: #22c55e; }
body { font-family: sans-serif; background-color: var(--bg-color); color: var(--text-main); margin: 0; padding: 40px; }
.container { max-width: 800px; margin: 0 auto; }
.card { background: var(--card-bg); border-radius: 12px; padding: 25px; margin-bottom: 20px; }
.btn-cta { display: inline-block; background-color: var(--cta-bg); color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: bold; }
"""

# --- 1. DATEN VON GOOGLE SHEETS HOLEN ---
def fetch_data_from_sheet():
    try:
        response = requests.get(SHEET_URL)
        response.raise_for_status()
        
        # CSV einlesen
        reader = csv.DictReader(io.StringIO(response.text))
        data_list = list(reader)
        
        if not data_list:
            return "❌ Fehler: Tabelle ist leer!"

        # Daten umformatieren für die Fabrik
        formatted_data = {
            "nische": data_list[0].get('Nische', 'Business Automation'),
            "tools": [{"name": row['Name'], "kategorie": row['Kategorie'], "link": row['Link']} for row in data_list]
        }
        
        # Als JSON speichern
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_file = os.path.join(DATA_DIR, f"sheet_data_{timestamp}.json")
        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(formatted_data, f, indent=4, ensure_ascii=False)
            
        return f"✅ Daten geladen: {target_file}"
    except Exception as e:
        return f"❌ Fehler beim Sheet-Download: {str(e)}"

# --- 2. GITHUB-UPLOAD ---
def git_push_content():
    try:
        with open("github_token.txt", "r") as f: token = f.read().strip()
        with open("github_repo.txt", "r") as f: repo_url = f.read().strip()
        
        auth_url = repo_url.replace("https://", f"https://{token}@")
        cwd = OUTPUT_DIR
        
        if not os.path.exists(os.path.join(cwd, ".git")):
            subprocess.run(["git", "init"], cwd=cwd, check=True)
            subprocess.run(["git", "remote", "add", "origin", auth_url], cwd=cwd, check=True)
            subprocess.run(["git", "branch", "-M", "main"], cwd=cwd, check=True)

        subprocess.run(["git", "add", "."], cwd=cwd, check=True)
        status = subprocess.run(["git", "status", "--porcelain"], cwd=cwd, capture_output=True, text=True)
        if status.stdout.strip():
            subprocess.run(["git", "commit", "-m", "Automated Update via Sheet"], cwd=cwd, check=True)
            subprocess.run(["git", "push", "-u", "origin", "main", "--force"], cwd=cwd, check=True)
            return "🚀 **FABRIK LIVE:** Neue Seiten online!"
        return "ℹ️ Keine neuen Änderungen."
    except Exception as e:
        return f"❌ Git-Fehler: {str(e)}"

# --- 3. GENERATOR ---
def generate_programmatic_pages(source_json_path):
    with open(source_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    generated_links = []
    for tool in data.get("tools", []):
        clean_name = tool['name'].lower().replace(' ', '-').replace('.', '')
        filename = f"beste-software-{clean_name}.html"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        html_content = f"""<!DOCTYPE html>
<html lang="de"><head><meta charset="UTF-8"><style>{SHARED_CSS}</style></head>
<body><div class="container"><h1>{tool['name']}</h1>
<div class="card"><p>Beste Lösung für {data.get('nische', 'Business')}.</p>
<a href="{tool['link']}" class="btn-cta" target="_blank">Jetzt testen</a></div>
<a href="index.html">Zurück zur Übersicht</a></div></body></html>"""
        
        with open(filepath, "w", encoding="utf-8") as out:
            out.write(html_content)
        generated_links.append({"title": tool['name'], "url": filename})
            
    # Index-Seite
    index_html = f"""<!DOCTYPE html>
<html lang="de"><head><meta charset="UTF-8"><style>{SHARED_CSS}</style></head>
<body><div class="container"><h1>Business Automation Hub</h1>
<div class="card"><ul>{"".join([f"<li><a href='{l['url']}'>{l['title']}</a></li>" for l in generated_links])}</ul></div></div></body></html>"""
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as out:
        out.write(index_html)
        
    return git_push_content()

# --- 4. TELEGRAM-INTERFACE ---
def ki_anfrage_verarbeiten(text):
    text_low = text.lower().strip()
    if "scout" in text_low:
        return fetch_data_from_sheet()
    if "fabrik" in text_low:
        files = [os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR) if f.endswith(".json")]
        return generate_programmatic_pages(max(files, key=os.path.getctime)) if files else "❌ Keine Daten gefunden."
    return "🤖 **System bereit.** Sende 'scout' zum Daten-Laden oder 'fabrik' zum Bauen."