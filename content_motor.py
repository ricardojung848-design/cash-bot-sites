import os
import subprocess
import re
from openai import OpenAI
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Verbindung zum lokalen LM Studio Server - Jetzt mit 5 Minuten Timeout-Schutz!
client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed", timeout=300.0)

def generate_article(topic):
    print(f"[*] Generiere E-E-A-T Content über LM Studio für: {topic}...")
    
    prompt = f"""
    Du bist ein renommierter Experte für Business Automation und Software-Architektur. 
    Schreibe einen tiefgehenden, professionellen Fachartikel (HTML-Format) über das Thema: '{topic}'.
    
    WICHTIGE E-E-A-T REGELN:
    - Experience (Erfahrung): Schreibe aus der Ich-Perspektive. Berichte von echten Praxistests und Implementierungen.
    - Expertise: Nutze korrekte Fachbegriffe, bleibe konkret.
    - Structure: Nutze einleitende Absätze, mindestens drei detaillierte H2-Abschnitte, eine HTML-Tabelle mit Vor- und Nachteilen sowie eine FAQ-Sektion am Ende.
    - Trust: Beende den Artikel mit einem dezenten Experten-Disclaimer.

    FORMATIERUNGS-REGEL:
    Antworte AUSSCHLIESSLICH mit dem sauberen HTML-Inhalt für den Artikel (Beginne direkt mit <h1>, dann <p>, <h2>, etc.). 
    Erzeuge KEINE Markdown-Code-Blöcke (wie ```html).
    """

    try:
        completion = client.chat.completions.create(
            model="local-model",
            messages=[{"role": "user", "content": prompt}]
        )
        raw_content = completion.choices[0].message.content
        clean_content = re.sub(r"```html|```", "", raw_content).strip()
        return clean_content
    except Exception as e:
        print(f"[-] Fehler bei der Generierung: {e}")
        return None

def build_full_page(title, body_content, image_url):
    if image_url and str(image_url).strip().startswith("http"):
        image_html = f'<img src="{image_url.strip()}" alt="{title}" class="article-image">'
    else:
        image_html = '<div class="article-image-placeholder">🤖 Business Automation Insights</div>'

    html_page = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Business Automation Hub</title>
    <style>
        :root {{ 
            --bg-color: #030712; --card-bg: #111827; --text-main: #f8fafc; 
            --text-muted: #94a3b8; --accent: #38bdf8; --border: #1e293b;
        }}
        body {{ 
            font-family: 'Inter', system-ui, -apple-system, sans-serif; 
            background-color: var(--bg-color); color: var(--text-main); 
            line-height: 1.7; margin: 0; padding: 40px 20px;
        }}
        .container {{ max-width: 700px; margin: 0 auto; width: 100%; }}
        .article-card {{ background: var(--card-bg); border-radius: 16px; padding: 40px; border: 1px solid var(--border); overflow: hidden; }}
        .article-image {{ width: 100%; max-height: 350px; object-fit: cover; border-radius: 12px; margin-bottom: 30px; border: 1px solid var(--border); }}
        .article-image-placeholder {{ width: 100%; height: 200px; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-radius: 12px; margin-bottom: 30px; display: flex; align-items: center; justify-content: center; color: var(--accent); font-weight: 600; letter-spacing: 0.05em; border: 1px solid var(--border); }}
        h1 {{ color: var(--text-main); font-size: 2.2rem; margin-top: 0; margin-bottom: 20px; letter-spacing: -0.04em; }}
        h2 {{ color: var(--accent); font-size: 1.5rem; margin-top: 30px; }}
        p {{ color: var(--text-main); }}
        table {{ width: 100%; border-collapse: collapse; margin: 25px 0; }}
        th, td {{ padding: 12px; border: 1px solid var(--border); text-align: left; }}
        th {{ background: var(--border); color: var(--accent); }}
        .back-link {{ display: inline-block; margin-top: 30px; color: var(--text-muted); text-decoration: none; font-size: 0.9rem; }}
        .back-link:hover {{ color: var(--accent); }}
    </style>
</head>
<body>
<div class="container">
    <div class="article-card">
        {image_html}
        {body_content}
        <a href="index.html" class="back-link">&larr; Zurück zum Hub</a>
    </div>
</div>
</body>
</html>"""
    return html_page

def update_index(title, filename):
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
    
    new_link = f'<li><a href="{filename}">{title}</a></li>'
    
    if new_link not in content:
        updated_content = content.replace('<ul id="project-list" class="links-list">', f'<ul id="project-list" class="links-list">\n        {new_link}')
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(updated_content)
        print(f"[+] 'index.html' erfolgreich aktualisiert und verlinkt.")

def main():
    print("[*] Verbinde mit Google Sheet für Content-Generierung...")
    scope = ["[https://spreadsheets.google.com/feeds](https://spreadsheets.google.com/feeds)", "[https://www.googleapis.com/auth/drive](https://www.googleapis.com/auth/drive)"]
    
    if not os.path.exists("credentials.json"):
        print("[-] Fehler: 'credentials.json' fehlt im Ordner!")
        return

    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    gc = gspread.authorize(creds)
    
    try:
        sheet = gc.open("CashBot_Trends").sheet1
    except Exception as e:
        print(f"[-] Fehler beim Öffnen des Google Sheets: {e}")
        return
    
    records = sheet.get_all_records()
    offene_themen = [r for r in records if r.get("Status") == "Offen"]
    
    if not offene_themen:
        print("[-] Keine offenen Themen mit dem Status 'Offen' im Google Sheet gefunden!")
        return

    print(f"[+] {len(offene_themen)} offene Themen geladen.\n")

    for index, row in enumerate(records, start=2):
        if row.get("Status") == "Offen":
            thema = row.get("Thema")
            image_url = row.get("Bild_URL", "").strip()
            
            clean_filename = thema.lower().replace(" ", "_").replace("ä","ae").replace("ü","ue").replace("ö","oe") + ".html"
            
            article_body = generate_article(thema)
            
            if not article_body:
                print(f"[-] Überspringe '{thema}' wegen Fehlers.")
                continue
                
            full_html = build_full_page(thema, article_body, image_url)
            
            with open(clean_filename, "w", encoding="utf-8") as f:
                f.write(full_html)
            
            update_index(thema, clean_filename)
            
            sheet.update_cell(index, 2, "Live")
            print(f"[+] Artikel '{clean_filename}' fertiggestellt und im Sheet auf 'Live' gesetzt.\n" + "-"*40)

    print("[*] Übertrage Änderungen an GitHub...")
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "Auto-Gen: Hub-Update aus Google Sheet"])
    subprocess.run(["git", "push"])
    print("\n--- FERTIG! Dein Content ist live! ---")

if __name__ == "__main__":
    main()