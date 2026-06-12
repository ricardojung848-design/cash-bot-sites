import os
import json
import subprocess
import requests
import csv
import io
from datetime import datetime

# Fabrik + Keyword Engine
from fabrik_engine import FABRIK
from seo_keywords import generate_keyword_cluster

# === VERZEICHNISSE ===
DATA_DIR = "scraped_data"
OUTPUT_DIR = "generated_content"
SOCIAL_DIR = "social_media"
CONFIG_FILE = "cashbot_config.json"
POSTING_QUEUE_FILE = os.path.join(SOCIAL_DIR, "posting_queue.json")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SOCIAL_DIR, exist_ok=True)

# === CONFIG LADEN ===
def load_config():
    default = {
        "nische": "Business Automation",
        "produkt_typ": "Automations-Dienstleistungen & KI-Beratung",
        "social_media": {
            "instagram_reels": True,
            "auto_store_posts": True,
            "auto_post": False
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
        lines.append(f"- ID {item['id']}: {item['thema']} [{item['status']}]")
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
    return f"✅ Eintrag für '{thema}' als 'posted' markiert."
# === KI-ANFRAGE: REEL GENERIEREN ===
def generate_reel_script(thema: str):
    thema_clean = thema.strip()
    script = {
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
    return script

def save_reel_script(script: dict):
    thema = script["thema"].replace(" ", "_").lower()
    json_path = os.path.join(SOCIAL_DIR, f"{thema}.json")
    txt_path = os.path.join(SOCIAL_DIR, f"{thema}.txt")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(script, f, indent=4, ensure_ascii=False)

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

# ===# === TELEGRAM-BEFEHLE ===

def handle_reel_command(text: str):
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


def handle_fabrik_command(text: str):
    cmd = text.lower().strip()

    if cmd == "fabrik start":
        return FABRIK.start()

    if cmd == "fabrik stop":
        return FABRIK.stop()

    if cmd == "fabrik status":
        return FABRIK.status()

    if cmd.startswith("fabrik add "):
        thema = text.split(" ", 2)[2].strip()
        return FABRIK.add_task(thema, fabrik_callback)

    return "❌ Unbekannter Fabrik-Befehl."


def handle_cluster_command(text: str):
    parts = text.split(" ", 1)
    if len(parts) < 2:
        return "❌ Bitte nutze: cluster <Thema>"
    thema = parts[1].strip()
    return create_cluster_tasks(thema)


def handle_queue_command():
    return get_queue_overview()


def handle_post_command(text: str):
    parts = text.split(" ", 1)
    if len(parts) < 2:
        return "❌ Bitte nutze: post <Thema>"
    thema = parts[1].strip()
    return mark_posted_by_thema(thema)


# === KI-ANFRAGE ROUTER ===

def process_ki_anfrage(text: str):
    text_low = text.lower().strip()

    # Reel
    if text_low.startswith("reel "):
        return handle_reel_command(text)

    # Fabrik
    if text_low.startswith("fabrik"):
        return handle_fabrik_command(text)

    # Cluster
    if text_low.startswith("cluster"):
        return handle_cluster_command(text)

    # Queue
    if text_low == "queue":
        return handle_queue_command()

    # Post
    if text_low.startswith("post "):
        return handle_post_command(text)

    # Fallback
    return (
        f"Verstanden. Du hast geschrieben: '{text}'.\n"
        "Nutze:\n"
        "· 'scout' → Daten