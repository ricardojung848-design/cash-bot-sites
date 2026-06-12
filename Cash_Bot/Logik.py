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
SOCIAL_DIR = "social_media"
CONFIG_FILE = "cashbot_config.json"
POSTING_QUEUE_FILE = os.path.join(SOCIAL_DIR, "posting_queue.json")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SOCIAL_DIR, exist_ok=True)

SHARED_CSS = """
:root { --bg-color: #0f172a; --card-bg: #1e293b; --text-main: #f8fafc; --accent: #38bdf8; --cta-bg: #22c55e; }
body { font-family: 'Segoe UI', sans-serif; background-color: var(--bg-color); color: var(--text-main); margin: 0; padding: 40px; }
.container { max-width: 900px; margin: 0 auto; }
.card { background: var(--card-bg); border-radius: 12px; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
.btn-cta { display: inline-block; background-color: var(--cta-bg); color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: bold; margin-top: 15px; }
.badge { display:inline-block; padding:4px 10px; border-radius:999px; background:#0ea5e9; color:#0f172a; font-size:12px; font-weight:600; margin-bottom:10px; }
h1 { font-size: 28px; margin-bottom: 10px; }
h2 { font-size: 22px; margin-top: 25px; }
ul { padding-left: 20px; }
a { color: var(--accent); }
.footer { margin-top: 40px; font-size: 13px; opacity: 0.7; }
"""

# === CONFIG LADEN ===
def load_config():
    default = {
        "nische": "Business Automation",
        "produkt_typ": "Automations-Dienstleistungen & KI-Beratung",
        "social_media": {
            "instagram_reels": True,
            "auto_store_posts": True,
            "auto_post": False  # halbautomatisch: kein echtes Autoposting
        }
    }
    if not os.path.exists(CONFIG_FILE):
        return default
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        sm = data.get("social_media", {})
        return {
            "nische": data.get("nische", default["nische"]),
            "produkt_typ": data.get("produkt_typ", default["produkt_typ"]),
            "social_media": {
                "instagram_reels": sm.get("instagram_reels", default["social_media"]["instagram_reels"]),
                "auto_store_posts": sm.get("auto_store_posts", default["social_media"]["auto_store_posts"]),
                "auto_post": sm.get("auto_post", default["social_media"]["auto_post"])
            }
        }
    except Exception:
        return default

CONFIG = load_config()
NISCHE = CONFIG["nische"]
PRODUKT_TYP = CONFIG["produkt_typ"]
SOCIAL_CFG = CONFIG["social_media"]


# === POSTING-QUEUE HELFER ===
def load_posting_queue():
    if not os.path.exists(POSTING_QUEUE_FILE):
        return []
    try:
        with open(POSTING_QUEUE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_posting_queue(queue):
    try:
        with open(POSTING_QUEUE_FILE, "w", encoding="utf-8") as f:
            json.dump(queue, f, indent=4, ensure_ascii=False)
    except Exception:
        pass


def add_to_posting_queue(script: dict, json_path: str, txt_path: str):
    queue = load_posting_queue()
    entry = {
        "id": len(queue) + 1,
        "thema": script["thema"],
        "nische": script["nische"],
        "produkt_typ": script["produkt_typ"],
        "json_path": json_path,
        "txt_path": txt_path,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "posted_at": None
    }
    queue.append(entry)
    save_posting_queue(queue)
    return entry


def get_queue_overview():
    queue = load_posting_queue()
    if not queue:
        return "📭 Posting-Queue ist leer."
    lines = ["📋 Posting-Queue:"]
    for item in queue:
        lines.append(
            f"- ID {item['id']}: {item['thema']} [{item['status']}]"
        )
    return "\n".join(lines)


def mark_posted_by_thema(thema: str):
    queue = load_posting_queue()
    if not queue:
        return "📭 Keine Einträge in der Posting-Queue."
    thema_low = thema.lower().strip()
    found = False
    for item in queue:
        if item["status"] == "pending" and item["thema"].lower() == thema_low:
            item["status"] = "posted"
            item["posted_at"] = datetime.now().isoformat()
            found = True
            break
    if not found:
        return f"❌ Kein pending-Eintrag mit Thema '{thema}' gefunden."
    save_posting_queue(queue)
    return f"✅ Eintrag für '{thema}' als 'posted' markiert (simulierter Post)."


# === SEO / CONTENT ENGINE ===
def generate_seo_content(thema: str, nische: str, produkt_typ: str):
    base_keyword = f"{thema} {nische}".strip()

    title = f"Beste Lösung für {thema} im Bereich {nische}"
    meta_description = (
        f"Entdecke, wie {thema} dir hilft, deine Prozesse im Bereich {nische} zu optimieren. "
        f"Ideal für {produkt_typ} mit Fokus auf Effizienz und Automatisierung."
    )
    h1 = f"{thema}: Smarte Lösung für {nische}"
    intro = (
        f"{thema} ist ein spannender Ansatz, um {nische.lower()} auf das nächste Level zu bringen. "
        f"In dieser Übersicht erfährst du, wie du {produkt_typ.lower()} mit Hilfe von Automatisierung "
        f"skalieren kannst – ohne dich in Technik zu verlieren."
    )

    abschnitt_1_titel = "Warum dieses Thema wichtig ist"
    abschnitt_1_text = (
        f"In der heutigen Zeit ist {nische.lower()} ein entscheidender Hebel, um Zeit zu sparen "
        f"und Fehler zu reduzieren. {thema} kann dir helfen, wiederkehrende Aufgaben zu automatisieren "
        f"und mehr Fokus auf strategische Entscheidungen zu legen."
    )

    abschnitt_2_titel = "Einsatzmöglichkeiten in deinem Alltag"
    abschnitt_2_text = (
        f"Ob du gerade erst mit {produkt_typ.lower()} startest oder bereits ein etabliertes Setup hast – "
        f"{thema} lässt sich flexibel integrieren. Typische Anwendungsfälle sind Lead-Generierung, "
        f"Onboarding, Reporting und die Verknüpfung verschiedener Tools."
    )

    abschnitt_3_titel = "Nächste Schritte und Umsetzung"
    abschnitt_3_text = (
        f"Der wichtigste Schritt ist, klein anzufangen und erste Prozesse mit {thema} zu testen. "
        f"Dokumentiere, was gut funktioniert, und skaliere dann gezielt. So baust du dir nach und nach "
        f"ein stabiles Automations-Setup auf, das dir langfristig Zeit und Geld spart."
    )

    faq = [
        {
            "frage": f"Ist {thema} für Einsteiger geeignet?",
            "antwort": (
                f"Ja. Du kannst mit einfachen Workflows starten und {thema} später Schritt für Schritt "
                f"ausbauen, sobald du dich sicherer fühlst."
            ),
        },
        {
            "frage": f"Wie passt {thema} zu {produkt_typ}?",
            "antwort": (
                f"{thema} kann dir helfen, {produkt_typ.lower()} effizienter zu vermarkten, zu liefern "
                f"oder zu skalieren – je nachdem, wie du es einsetzt."
            ),
        },
    ]

    return {
        "keyword": base_keyword,
        "title": title,
        "meta_description": meta_description,
        "h1": h1,
        "intro": intro,
        "abschnitte": [
            {"titel": abschnitt_1_titel, "text": abschnitt_1_text},
            {"titel": abschnitt_2_titel, "text": abschnitt_2_text},
            {"titel": abschnitt_3_titel, "text": abschnitt_3_text},
        ],
        "faq": faq,
    }


# === SOCIAL MEDIA ENGINE (Hybrid-Style Instagram Reels) ===
def sanitize_filename(text: str) -> str:
    forbidden = '<>:"/\\|?*'
    safe = text
    for ch in forbidden:
        safe = safe.replace(ch, "")
    safe = safe.strip()
    if not safe:
        safe = "thema"
    return safe


def generate_instagram_reel_script(thema: str, nische: str, produkt_typ: str):
    base_hashtags = [
        "#automation", "#businessautomation", "#kiberatung",
        "#onlineskalierung", "#prozesse", "#cashbot"
    ]
    hashtags_str = " ".join(base_hashtags)

    hook_varianten = [
        f"🔥 Du willst {nische.lower()} endlich automatisieren – aber weißt nicht, wo du anfangen sollst?",
        f"🚀 {thema} kann dein {nische.lower()}-Game komplett verändern, wenn du es richtig einsetzt.",
        f"⚡ Hör auf, Zeit mit Copy-Paste zu verschwenden – bau dir ein System, das für dich arbeitet."
    ]

    problem = (
        f"Die meisten {produkt_typ.lower()} hängen in manuellen Abläufen fest: Excel, E-Mails, "
        f"Copy-Paste. Genau da setzt {thema} an."
    )
    solution = (
        f"Mit {thema} kannst du Leads, Termine und Reports automatisieren. "
        f"Du baust dir Schritt für Schritt ein Setup, das für dich arbeitet – statt andersrum. 💻🤖"
    )

    cta_varianten = [
        f"Wenn du {produkt_typ.lower()} ernsthaft skalieren willst, fang mit einem kleinen Workflow rund um {thema} an. Mehr dazu auf deiner Website. 🔗",
        f"Speichere dieses Reel, wenn du {nische.lower()} endlich sauber automatisieren willst – und schick es jemandem, der gerade im Chaos steckt. 📲",
        f"Schreib dir {thema} auf deine To-Do-Liste für diese Woche – ein kleiner Automation-Schritt kann dein ganzes System verändern. ✅"
    ]

    script = {
        "thema": thema,
        "nische": nische,
        "produkt_typ": produkt_typ,
        "hooks": hook_varianten,
        "problem": problem,
        "solution": solution,
        "cta_varianten": cta_varianten,
        "hashtags": hashtags_str,
        "style": "hybrid",
        "timestamp": datetime.now().isoformat()
    }

    return script


def store_instagram_reel_script(script: dict):
    try:
        safe_name = sanitize_filename(script["thema"].lower().replace(" ", "-"))
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_filename = f"reel_{safe_name}_{ts}.json"
        txt_filename = f"reel_{safe_name}_{ts}.txt"

        json_path = os.path.join(SOCIAL_DIR, json_filename)
        txt_path = os.path.join(SOCIAL_DIR, txt_filename)

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(script, f, indent=4, ensure_ascii=False)

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"Thema: {script['thema']}\n")
            f.write(f"Nische: {script['nische']}\n")
            f.write(f"Produkt-Typ: {script['produkt_typ']}\n\n")
            f.write("Hooks:\n")
            for h in script["hooks"]:
                f.write(f"- {h}\n")
            f.write("\nProblem:\n")
            f.write(script["problem"] + "\n\n")
            f.write("Lösung:\n")
            f.write(script["solution"] + "\n\n")
            f.write("CTA-Varianten:\n")
            for c in script["cta_varianten"]:
                f.write(f"- {c}\n")
            f.write("\nHashtags:\n")
            f.write(script["hashtags"] + "\n")

        # in Posting-Queue eintragen
        entry = add_to_posting_queue(script, json_path, txt_path)

        return (
            f"📲 Instagram Reel-Skript gespeichert:\n"
            f"JSON: {json_path}\nTXT: {txt_path}\n"
            f"🧾 In Posting-Queue aufgenommen als ID {entry['id']} (Status: pending)."
        )
    except Exception as e:
        return f"❌ Fehler beim Speichern des Reel-Skripts: {e}"


def auto_generate_social_for_thema(thema: str):
    if not SOCIAL_CFG.get("instagram_reels", False):
        return "ℹ️ Social-Media-Generation ist deaktiviert."

    script = generate_instagram_reel_script(thema, NISCHE, PRODUKT_TYP)
    msg = ""
    if SOCIAL_CFG.get("auto_store_posts", True):
        msg = store_instagram_reel_script(script)
    else:
        msg = "📲 Reel-Skript generiert (Speichern deaktiviert)."

    short_preview = (
        f"🎬 Reel für Thema: {thema}\n"
        f"Hook-Beispiel: {script['hooks'][0]}\n"
        f"CTA-Beispiel: {script['cta_varianten'][0]}\n"
        f"Hashtags: {script['hashtags']}"
    )

    return msg + "\n\n" + short_preview


# --- 1. DATEN HOLEN ---
def fetch_data_from_sheet():
    try:
        response = requests.get(SHEET_URL, timeout=10)
        response.raise_for_status()
        reader = csv.DictReader(io.StringIO(response.text))
        data_list = list(reader)
        if not data_list:
            return "❌ Fehler: Tabelle ist leer!"
        formatted_data = {
            "nische": data_list[0].get("Nische", NISCHE),
            "tools": [
                {
                    "name": row["Name"],
                    "kategorie": row["Kategorie"],
                    "link": row["Link"],
                }
                for row in data_list
                if row.get("Name")
            ],
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
        with open("github_token.txt", "r", encoding="utf-8") as f:
            token = f.read().strip()
        with open("github_repo.txt", "r", encoding="utf-8") as f:
            repo_url = f.read().strip()
        auth_url = repo_url.replace("https://", f"https://{token}@")

        if not os.path.exists(os.path.join(OUTPUT_DIR, ".git")):
            subprocess.run(["git", "init"], cwd=OUTPUT_DIR, check=True)
            subprocess.run(["git", "remote", "add", "origin", auth_url], cwd=OUTPUT_DIR, check=True)
            subprocess.run(["git", "branch", "-M", "main"], cwd=OUTPUT_DIR, check=True)

        subprocess.run(["git", "add", "."], cwd=OUTPUT_DIR, check=True)
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=OUTPUT_DIR,
            capture_output=True,
            text=True,
        )

        if status.stdout.strip():
            subprocess.run(
                ["git", "commit", "-m", "Auto-Update: " + datetime.now().strftime("%Y-%m-%d")],
                cwd=OUTPUT_DIR,
                check=True,
            )
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

        nische = data.get("nische", NISCHE)
        generated_links = []

        for tool in data.get("tools", []):
            name = tool["name"]
            kategorie = tool.get("kategorie", "Allgemein")
            link = tool.get("link", "#")

            clean_name = (
                name.lower()
                .replace(" ", "-")
                .replace(".", "")
                .replace("/", "-")
            )
            filename = f"beste-software-{clean_name}.html"
            filepath = os.path.join(OUTPUT_DIR, filename)

            seo = generate_seo_content(name, nische, PRODUKT_TYP)

            faq_html = ""
            if seo["faq"]:
                faq_items = []
                for item in seo["faq"]:
                    faq_items.append(
                        f"<li><strong>{item['frage']}</strong><br>{item['antwort']}</li>"
                    )
                faq_html = "<h2>Häufige Fragen</h2><ul>" + "".join(faq_items) + "</ul>"

            abschnitte_html = ""
            for abschnitt in seo["abschnitte"]:
                abschnitte_html += f"<h2>{abschnitt['titel']}</h2><p>{abschnitt['text']}</p>"

            html_content = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>{seo['title']}</title>
    <meta name="description" content="{seo['meta_description']}">
    <style>{SHARED_CSS}</style>
</head>
<body>
<div class="container">
    <span class="badge">{nische}</span>
    <h1>{seo['h1']}</h1>
    <div class="card">
        <p>{seo['intro']}</p>
        <p><strong>Kategorie:</strong> {kategorie}</p>
        <a href="{link}" class="btn-cta" target="_blank">Jetzt {name} entdecken</a>
    </div>
    <div class="card">
        {abschnitte_html}
    </div>
    <div class="card">
        {faq_html}
    </div>
    <div class="footer">
        <a href="index.html">← Zurück zur Übersicht</a><br>
        <span>Diese Seite wurde automatisch von Cash_Bot generiert.</span>
    </div>
</div>
</body>
</html>"""

            with open(filepath, "w", encoding="utf-8") as out:
                out.write(html_content)

            generated_links.append({"title": name, "url": filename})

        links_html = "".join(
            [f"<li><a href='{l['url']}'>{l['title']}</a></li>" for l in generated_links]
        )
        index_html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>{nische} – Automation Hub</title>
    <meta name="description" content="Übersicht der besten Lösungen und Themen im Bereich {nische}.">
    <style>{SHARED_CSS}</style>
</head>
<body>
<div class="container">
    <span class="badge">{nische}</span>
    <h1>{nische} – Automation Hub</h1>
    <div class="card">
        <p>Hier findest du automatisch generierte Seiten rund um {nische}. Fokus: {PRODUKT_TYP} und skalierbare Automatisierung.</p>
        <ul>
            {links_html}
        </ul>
    </div>
    <div class="footer">
        <span>Generiert von Cash_Bot – Programmatic SEO & Automation.</span>
    </div>
</div>
</body>
</html>"""

        with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as out:
            out.write(index_html)

        return git_push_content()
    except Exception as e:
        return f"❌ Fehler in der Fabrik: {str(e)}"


# --- 3b. EINZEL-TASK-FABRIK ---
def fabrik_prozess_einzeltask(thema: str):
    try:
        data = {
            "nische": NISCHE,
            "tools": [
                {
                    "name": thema,
                    "kategorie": "Allgemein",
                    "link": "https://google.com"
                }
            ],
        }

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_json = os.path.join(DATA_DIR, f"single_task_{timestamp}.json")

        with open(temp_json, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        result_pages = generate_programmatic_pages(temp_json)
        result_social = auto_generate_social_for_thema(thema)

        return f"{result_pages}\n{result_social}"
    except Exception as e:
        return f"❌ Fehler im Einzel-Fabrikprozess: {str(e)}"


# --- 4. BRÜCKE ZUM WORKER ---
def ki_anfrage_verarbeiten(text):
    text_low = text.lower().strip()

    if "scout" in text_low:
        return fetch_data_from_sheet()

    elif "fabrik" in text_low:
        files = [
            os.path.join(DATA_DIR, f)
            for f in os.listdir(DATA_DIR)
            if f.endswith(".json")
        ]
        if files:
            neueste_datei = max(files, key=os.path.getctime)
            return generate_programmatic_pages(neueste_datei)
        else:
            return "❌ Keine Daten gefunden. Bitte erst 'scout' ausführen."

    elif text_low.startswith("reel"):
        thema = text.replace("reel", "", 1).strip() or "Automation"
        return auto_generate_social_for_thema(thema)

    elif text_low.startswith("queue"):
        return get_queue_overview()

    elif text_low.startswith("post "):
        thema = text[5:].strip()
        if not thema:
            return "❌ Bitte Thema angeben, z.B. 'post KI Automation'."
        return mark_posted_by_thema(thema)

    else:
        return (
            f"Verstanden. Du hast geschrieben: '{text}'.\n"
            f"Nutze:\n"
            f"- 'scout' → Daten holen\n"
            f"- 'fabrik' → Seiten generieren\n"
            f"- 'reel <Thema>' → Reel-Skript erzeugen\n"
            f"- 'queue' → Posting-Queue anzeigen\n"
            f"- 'post <Thema>' → Eintrag als gepostet markieren (halbautomatisch)"
        )


def check_system():
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        os.makedirs(SOCIAL_DIR, exist_ok=True)
        if not os.path.exists(POSTING_QUEUE_FILE):
            save_posting_queue([])
        return (
            f"✅ Systemcheck: Verzeichnisse vorhanden, Logik.py geladen. "
            f"Nische: {NISCHE}, Produkt-Typ: {PRODUKT_TYP}"
        )
    except Exception as e:
        return f"❌ Systemcheck-Fehler: {e}"
