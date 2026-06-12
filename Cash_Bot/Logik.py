import os
import json
import subprocess
import requests
import csv
import io
from datetime import datetime

# === KONFIGURATION ===
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRdlTbob3aK0v7xyUtKn__RymdItFQmOqcV1Q6_74w3Frn8fORnIbSnVIJey_uZ5LT1C4f9yD3HOAPO/pub?output=csv"
DATA_DIR = "scraped_data"
OUTPUT_DIR = "generated_content"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

SHARED_CSS = """
:root { --bg-color: #0f172a; --card-bg: #1e293b; --text-main: #f8fafc; --accent: #38bdf8; --cta-bg: #22c55e; }
body { font-family: 'Segoe UI', sans-serif; background-color: var(--bg-color); color: var(--text-main); margin: 0; padding: 40px; }
.container { max-width: 800px; margin: 0 auto; }
.card { background: var(--card-bg); border-radius: 12px; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
.btn-cta { display: inline-block; background-color: var(--cta-bg); color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: bold; margin-top: 15px; }
"""

# --- 1. DATEN HOLEN ---
def fetch_data_from_sheet():
    try:
        response = requests.get(SHEET_URL, timeout=10)
        response.raise_for_status()
        reader = csv.DictReader(io.StringIO(response.text))
        data_list = list(reader)
        if not data_list: return "❌ Fehler: Tabelle ist leer!"
        formatted_data = {
            "nische": data_list[0].get('Nische', 'Business Automation'),
            "tools": [{"name": row['Name'], "kategorie": row['Kategorie'], "link": row['Link']} for row in data_list if row.get('Name')]
        }
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
        if not os.path.exists("github_token.txt") or not os.path.exists("github_repo.txt"):
            return "❌ Fehler: Zugangsdaten fehlen!"
        with open("github_token.txt", "r") as f: token = f.read().strip()
        with open("github_repo.txt", "r") as f: repo_url = f.read().strip()
        auth_url = repo_url.replace("https://", f"https://{token}@")
        
        # Git vorbereiten
        if not os.path.exists(os.path.join(OUTPUT_DIR, ".git")):
            subprocess.run(["git", "init"], cwd=OUTPUT_DIR, check=True)
            subprocess.run(["git", "remote", "add", "origin", auth_url], cwd=OUTPUT_DIR, check=True)
            subprocess.run(["git", "branch", "-M", "main"], cwd=OUTPUT_DIR, check=True)

        subprocess.run(["git", "add", "."], cwd=OUTPUT_DIR, check=True)
        status = subprocess.run(["git", "status", "--porcelain"], cwd=OUTPUT_DIR, capture_output=True, text=True)
        
        if status.stdout.strip():
            subprocess.run(["git", "commit", "-m", "Auto-Update: " + datetime.now().strftime("%Y-%m-%d")], cwd=OUTPUT_DIR, check=True)
            # Erst synchronisieren (Fetch + Reset), dann erzwingen
            subprocess.run(["git", "fetch", "origin"], cwd=OUTPUT_DIR, check=True)
            subprocess.run(["git", "reset", "--hard", "origin/main"], cwd=OUTPUT_DIR, check=True)
            subprocess.run(["git", "push", "-u", "origin", "main", "--force"], cwd=OUTPUT_DIR, check=True)
            return "🚀 **FABRIK LIVE:** Erfolgreich synchronisiert!"
        return "ℹ️ Keine neuen Änderungen."
    except Exception as e:
        return f"❌ Git-Fehler: {str(e)}"

# --- 3. GENERATOR ---
def generate_programmatic_pages(source_json_path):
    try:
        with open(source_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        generated_links = []
        for tool in data.get("tools", []):
            clean_name = tool['name'].lower().replace(' ', '-').replace('.', '')
            filename = f"beste-software-{clean_name}.html"
            filepath = os.path.join(OUTPUT_DIR, filename)
            html_content = f"""<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8"><title>{tool['name']}</title><style>{SHARED_CSS}</style></head>
<body><div class="container"><h1>{tool['name']}</h1>
<div class="card"><p>Beste Lösung für {data.get('nische', 'Business')}. Kategorie: {tool['kategorie']}</p>
<a href="{tool['link']}" class="btn-cta" target="_blank">Jetzt testen</a></div>
<a href="index.html">← Zurück zur Übersicht</a></div></body></html>"""
            with open(filepath, "w", encoding="utf-8") as out:
                out.write(html_content)
            generated_links.append({"title": tool['name'], "url": filename})
        index_html = f"""<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8"><style>{SHARED_CSS}</style></head>
<body><div class="container"><h1>Business Automation Hub</h1>
<div class="card"><ul>{"".join([f"<li><a href='{l['url']}'>{l['title']}</a></li>" for l in generated_links])}</ul></div></div></body></html>"""
        with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as out:
            out.write(index_html)
        return git_push_content()
    except Exception as e:
        return f"❌ Fehler in der Fabrik: {str(e)}"

# --- 4. BRÜCKE ZUM WORKER ---
def ki_anfrage_verarbeiten(text):
    text_low = text.lower().strip()
    if "scout" in text_low:
        return fetch_data_from_sheet()
    elif "fabrik" in text_low:
        files = [os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR) if f.endswith(".json")]
        if files:
            neueste_datei = max(files, key=os.path.getctime)
            return generate_programmatic_pages(neueste_datei)
        else:
            return "❌ Keine Daten gefunden. Bitte erst 'scout' ausführen."
    else:
        return f"Verstanden. Du hast geschrieben: '{text}'. Nutze bitte 'scout' oder 'fabrik'."