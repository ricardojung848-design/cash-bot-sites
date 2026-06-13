# === VERSION HEADER ===
LOGIK_VERSION = "Logik.py v1.0 – 13.06.2026 – Ricardo Build"

import os
import json
from datetime import datetime
from fabrik_engine import FABRIK
from seo_keywords import generate_keyword_cluster

# === PFAD KONFIGURATION ===
BASE_DIR = os.getcwd()
OUTPUT_DIR = os.path.join(BASE_DIR, "generated_pages")
SOCIAL_DIR = os.path.join(BASE_DIR, "social_media")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SOCIAL_DIR, exist_ok=True)

# === GRUNDKONFIGURATION ===
NISCHE = "KI Automation"
PRODUKT_TYP = "Automatisierte Workflows"

SOCIAL_CFG = {
    "auto_store_posts": True
}

# ============================================================
# === REEL ENGINE ============================================
# ============================================================

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


# ============================================================
# === SEO SEITEN GENERATOR ===================================
# ============================================================

def generate_seo_page(thema: str):
    thema_clean = thema.strip()
    filename = thema_clean.replace(" ", "_").lower