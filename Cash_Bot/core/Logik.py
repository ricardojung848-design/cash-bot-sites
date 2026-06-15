import os
import json
from datetime import datetime

# === interne Utils ===
from core.utils import (
    BASE_DIR,
    DATA_DIR,
    OUTPUT_DIR,
    SOCIAL_DIR,
    CONFIG_DIR,
    load_json,
    save_json,
    log_worker,
    warn_worker,
    error_worker,
)

# === Module ===
from modules.fabrik_engine import FABRIK
from modules.seo_keywords import generate_keyword_cluster


# === CONFIG LADEN ===
CONFIG_FILE = os.path.join(CONFIG_DIR, "cashbot_config.json")

DEFAULT_CONFIG = {
    "nische": "Business Automation",
    "produkt_typ": "Automations-Dienstleistungen & KI-Beratung",
    "social_media": {
        "instagram_reels": True,
        "auto_store_posts": True,
        "auto_post": False
    }
}

CONFIG = load_json(CONFIG_FILE, DEFAULT_CONFIG)
NISCHE = CONFIG["nische"]
PRODUKT_TYP = CONFIG["produkt_typ"]
SOCIAL_CFG = CONFIG["social_media"]


# === POSTING-QUEUE ===
POSTING_QUEUE_FILE = os.path.join(SOCIAL_DIR, "posting_queue.json")

def load_posting_queue():
    return load_json(POSTING_QUEUE_FILE, [])

def save_posting_queue(queue):
    save_json(POSTING_QUEUE_FILE, queue)

def add_to_posting_queue(script, json_path, txt_path):
    queue = load_posting_queue()
    entry = {
        "id": len(queue) + 1,
        "thema": script["thema"],
        "nische": script["nische"],
        "produkt_typ": script["produkt_typ"],
        "json_path": json_path,
        "txt_path": txt_path,
        "status": "pending",
        "scheduled_at": None,
        "platforms": ["instagram"],
        "auto_post": False,
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
        lines.append(f"- ID {item['id']}: {item['thema']} [{item['status']}]")
    return "\n".join(lines)

def mark_posted(entry):
    entry["status"] = "posted"
    entry["posted_at"] = datetime.now().isoformat()

def mark_posted_by_thema(thema):
    queue = load_posting_queue()
    thema_low = thema.lower().strip()
    for item in queue:
        if item["status"] == "pending" and item["thema"].lower() == thema_low:
            mark_posted(item)
            save_posting_queue(queue)
            return f"✅ Eintrag für '{thema}' als 'posted' markiert."
    return f"❌ Kein pending-Eintrag mit Thema '{thema}' gefunden."


# === AUTO-POSTING ENGINE ===
def perform_post(entry):
    """
    A) Simuliertes Posting
    """
    log_worker(f"Simuliere Posting für: {entry['thema']}")
    return f"📢 Simuliertes Posting veröffentlicht für: {entry['thema']}"

def auto_posting_tick():
    queue = load_posting_queue()
    changed = False

    for entry in queue:
        if entry["status"] != "pending":
            continue

        # Sofort posten
        if entry["auto_post"] is True:
            result = perform_post(entry)
            mark_posted(entry)
            changed = True
            log_worker(result)

        # Zeitgesteuertes Posting
        elif entry["scheduled_at"]:
            try:
                sched = datetime.fromisoformat(entry["scheduled_at"])
                if datetime.now() >= sched:
                    result = perform_post(entry)
                    mark_posted(entry)
                    changed = True
                    log_worker(result)
            except:
                pass

    if changed:
        save_posting_queue(queue)


# === REEL ENGINE ===
def generate_reel_script(thema):
    thema_clean = thema.strip()
    return {
        "thema": thema_clean,
        "nische": NISCHE,
        "produkt_typ": PRODUKT_TYP,
        "hook": f"🔥 Du willst {thema_clean} endlich meistern – aber weißt nicht, wo du anfangen sollst?",
        "content": [
            f"{thema_clean} ist einer der schnellsten Wege, um Prozesse zu automatisieren.",
            f"Viele machen Fehler, weil sie ohne System starten.",
            f"Mit einem klaren Workflow kannst du {thema_clean} in wenigen Tagen umsetzen."
        ],
        "cta": f"Wenn du {PRODUKT_TYP} ernsthaft skalieren willst, fang mit einem kleinen Workflow rund um {thema_clean} an.",
        "hashtags": [
            "#automation", "#businessautomation", "#kiberatung",
            "#onlineskalierung", "#prozesse", "#cashbot"
        ],
        "timestamp": datetime.now().isoformat()
    }

def save_reel_script(script):
    thema = script["thema"].replace(" ", "_").lower()
    json_path = os.path.join(SOCIAL_DIR, f"{thema}.json")
    txt_path = os.path.join(SOCIAL_DIR, f"{thema}.txt")

    save_json(json_path, script)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"Reel für Thema: {script['thema']}\n")
        f.write(f"Hook: {script['hook']}\n\n")
        f.write("Content:\n")
        for line in script["content"]:
            f.write(f"- {line}\n")
        f.write(f"\nCTA: {script['cta']}\n")
        f.write("\nHashtags:\n")
        f.write(" ".join(script["hashtags"]))

    return json_path, txt_path


# === FABRIK CALLBACK ===
def fabrik_callback(thema):
    filename = thema.replace(" ", "_").lower() + ".html"
    path = os.path.join(OUTPUT_DIR, filename)

    html = f"""
    <html>
    <head>
        <title>{thema} – {NISCHE}</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>{thema}</h1>
        <p>Diese Seite wurde automatisch generiert durch den DETO CashBot.</p>
        <p>Nische: {NISCHE}</p>
        <p>Produkt-Typ: {PRODUKT_TYP}</p>
        <p>Erstellt am: {datetime.now().isoformat()}</p>
    </body>
    </html>
    """

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    return path


# === CLUSTER ENGINE ===
def create_cluster_tasks(thema):
    cluster = generate_keyword_cluster(thema)
    keywords = cluster["keywords"]

    for kw in keywords:
        FABRIK.add_task(kw, fabrik_callback)

    return (
        f"🔗 Cluster erstellt für '{thema}'\n"
        f"📌 Keywords: {len(keywords)}\n"
        f"🚀 Tasks in Fabrik-Queue gelegt."
    )


# === TELEGRAM-BEFEHLE ===
def handle_reel_command(text):
    parts = text.split(" ", 1)
    if len(parts) < 2:
        return "❌ Bitte nutze: reel <Thema>"

    thema = parts[1].strip()
    script = generate_reel_script(thema)
    json_path, txt_path = save_reel_script(script)

    if SOCIAL_CFG["auto_store_posts"]:
        add_to_posting_queue(script, json_path, txt_path)

    return (
        f"🎬 Reel-Skript erstellt für: {thema}\n"
        f"📁 Gespeichert unter:\n"
        f"- {json_path}\n"
        f"- {txt_path}"
    )

def handle_post_now(text):
    parts = text.split(" ", 2)
    if len(parts) < 3:
        return "❌ Bitte nutze: post now <Thema>"

    thema = parts[2].strip()
    queue = load_posting_queue()

    for entry in queue:
        if entry["thema"].lower() == thema.lower():
            entry["auto_post"] = True
            save_posting_queue(queue)
            return f"🚀 Posting für '{thema}' wird sofort ausgeführt."

    return f"❌ Kein Eintrag für '{thema}' gefunden."

def handle_queue_command():
    return get_queue_overview()

def handle_post_command(text):
    if text.startswith("post now"):
        return handle_post_now(text)
    return "❌ Unbekannter Post-Befehl."


# === KI-ROUTER ===
def process_ki_anfrage(text):
    text_low = text.lower().strip()

    if text_low.startswith("reel "):
        return handle_reel_command(text)
    if text_low.startswith("fabrik"):
        return handle_fabrik_command(text)
    if text_low.startswith("cluster"):
        return handle_cluster_command(text)
    if text_low == "queue":
        return handle_queue_command()
    if text_low.startswith("post"):
        return handle_post_command(text)

    return (
        f"Verstanden. Du hast geschrieben: '{text}'.\n"
        "Nutze:\n"
        "· 'scout' → Daten holen\n"
        "· 'fabrik' → Seiten generieren\n"
        "· 'reel <Thema>' → Reel-Skript erzeugen\n"
        "· 'queue' → Posting-Queue anzeigen\n"
        "· 'post now <Thema>' → Sofort posten\n"
    )
