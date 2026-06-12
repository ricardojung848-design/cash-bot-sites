import os
import subprocess
import re
from openai import OpenAI

# Verbindung zum lokalen LM Studio Server
client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

def generate_article(topic):
    print(f"[*] Generiere E-E-A-T Content über LM Studio für: {topic}...")
    
    prompt = f"""
    Du bist ein renommierter Experte für Business Automation und Software-Architektur. 
    Schreibe einen tiefgehenden, professionellen Fachartikel (HTML-Format) über das Thema: '{topic}'.
    
    WICHTIGE E-E-A-T REGELN:
    - Experience (Erfahrung): Schreibe aus der Ich-Perspektive. Berichte von echten Praxistests, Implementierungen und unerwarteten Hürden, die du gelöst hast.
    - Expertise: Nutze korrekte Fachbegriffe, bleibe konkret, vermeide oberflächliche Floskeln.
    - Structure: Nutze einleitende Absätze, mindestens drei detaillierte H2-Abschnitte, eine übersichtliche HTML-Tabelle mit Vor- und Nachteilen sowie eine FAQ-Sektion am Ende mit 3 klaren Fragen und Antworten.
    - Trust: Beende den Artikel mit einem dezenten Experten-Disclaimer.

    FORMATIERUNGS-REGEL:
    Antworte AUSSCHLIESSLICH mit dem sauberen HTML-Inhalt für den Artikel (Nutze <h1>, <h2>, <p>, <table>, etc.). 
    Erzeuge KEINE Markdown-Code-Blöcke (wie ```html), keine Erklärungen drumherum. Beginne direkt mit dem Inhalt.
    """

    completion = client.chat.completions.create(
        model="local-model",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    raw_content = completion.choices[0].message.content
    
    # Sicherheits-Bereinigung: Falls das Modell trotz Anweisung Markdown-Tags liefert
    clean_content = re.sub(r"```html|```", "", raw_content).strip()
    return clean_content

def build_full_page(title, body_content):
    # Generiert das exakt gleiche edle CSS-Design für die Unterseiten
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
        .article-card {{ background: var(--card-bg); border-radius: 16px; padding: 40px; border: 1px solid var(--border); }}
        h1 {{ color: var(--text-main); font-size: 2.2rem; margin-bottom: 20px; letter-spacing: -0.04em; }}
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
    
    # Neuer Link-Eintrag für die Liste
    new_link = f'<li><a href="{filename}">{title}</a></li>'
    
    # Nur einfügen, wenn der Link noch nicht existiert
    if new_link not in content:
        updated_content = content.replace('<ul id="project-list" class="links-list">', f'<ul id="project-list" class="links-list">\n        {new_link}')
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(updated_content)
        print(f"[+] 'index.html' erfolgreich aktualisiert und verlinkt.")

def main():
    if not os.path.exists("themen.txt"):
        print("[-] Fehler: Erstelle bitte zuerst die Datei 'themen.txt' mit deinen Themen!")
        return

    with open("themen.txt", "r", encoding="utf-8") as f:
        themen = [line.strip() for line in f if line.strip()]

    if not themen:
        print("[-] 'themen.txt' ist leer. Bitte Themen eintragen!")
        return

    print(f"[+] Starte Batch-Generierung für {len(themen)} Themen...\n")

    for thema in themen:
        # Erstellt sauberen Dateinamen (z.B. "ki_im_marketing.html")
        clean_filename = thema.lower().replace(" ", "_").replace("ä","ae").replace("ü","ue").replace("ö","oe") + ".html"
        
        # 1. Content über LM Studio generieren
        article_body = generate_article(thema)
        
        # 2. In das Premium-Layout einbetten
        full_html = build_full_page(thema, article_body)
        
        # 3. Speichern
        with open(clean_filename, "w", encoding="utf-8") as f:
            f.write(full_html)
        
        # 4. Automatisch auf der Startseite verlinken
        update_index(thema, clean_filename)
        print(f"[+] Artikel '{clean_filename}' fertiggestellt.\n" + "-"*40)

    # 5. Automatischer Git Push für das gesamte Update
    print("[*] Übertrage alle neuen Seiten gesammelt an GitHub...")
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", f"Auto-Gen Hub-Update: {len(themen)} neue Artikel veroffentlicht"])
    subprocess.run(["git", "push"])
    print("\n--- GRANDIOS! Alle Artikel sind live und auf Vercel verfügbar! ---")

if __name__ == "__main__":
    main()