import os
from datetime import datetime, time as dtime

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
    queue = load_json(POSTING_QUEUE_FILE, [])
    if not isinstance(queue, list):
        queue = []
        save_json(POSTING_QUEUE_FILE, queue)
    return queue


def save_posting_queue(queue):
    save_json(POSTING_QUEUE_FILE, queue)


def _next_queue_id(queue):
    if not queue:
        return 1
    return max(item.get("id", 0) for item in queue) + 1


def add_to_posting_queue(script, json_path, txt_path):
    queue = load_posting_queue()
    entry = {
        "id": _next_queue_id(queue),
        "thema": script["thema"],
        "nische": script["nische"],
        "produkt_typ": script["produkt_typ"],
        "json_path": json_path,
        "txt_path": txt_path,
        "status": "pending",  # pending | scheduled | posted | cancelled
        "scheduled_at": None,
        "platforms": ["instagram"],
        "auto_post": False,
        "created_at": datetime.now().isoformat(),
        "posted_at": None,
        "cancelled_at": None,
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
        sched = item.get("scheduled_at")
        sched_str = f"📅 {sched}" if sched else ""
        lines.append(
            f"- ID {item['id']}: {item['thema']} "
            f"[{item['status']}] {sched_str}"
        )
    return "\n".join(lines)


def mark_posted(entry):
    entry["status"] = "posted"
    entry["posted_at"] = datetime.now().isoformat()


def cancel_post_by_id(post_id: int):
    queue = load_posting_queue()
    for item in queue:
        if item.get("id") == post_id and item["status"] in ("pending", "scheduled"):
            item["status"] = "cancelled"
            item["cancelled_at"] = datetime.now().isoformat()
            save_posting_queue(queue)
            return f"🛑 Posting mit ID {post_id} wurde abgebrochen."
    return f"❌ Kein aktiver Eintrag mit ID {post_id} gefunden."


def clear_queue():
    save_posting_queue([])
    return "🧹 Posting-Queue wurde komplett geleert."


def queue_status():
    queue = load_posting_queue()
    if not queue:
        return "📭 Keine Einträge in der Posting-Queue."

    total = len(queue)
    pending = sum(1 for x in queue if x["status"] == "pending")
    scheduled = sum(1 for x in queue if x["status"] == "scheduled")
    posted = sum(1 for x in queue if x["status"] == "posted")
    cancelled = sum(1 for x in queue if x["status"] == "cancelled")

    return (
        "📊 Posting-Status:\n"
        f"• Gesamt: {total}\n"
        f"• Pending: {pending}\n"
        f"• Scheduled: {scheduled}\n"
        f"• Posted: {posted}\n"
        f"• Cancelled: {cancelled}"
    )


# === AUTO-POSTING ENGINE ===
def perform_post(entry):
    log_worker(f"Simuliere Posting für: {entry['thema']}")
    msg = f"💥 Simuliertes Posting veröffentlicht für: {entry['thema']}"
    log_worker(msg)
    return msg


def auto_posting_tick():
    queue = load_posting_queue()
    changed = False
    now = datetime.now()

    for entry in queue:
        status = entry.get("status", "pending")

        if status not in ("pending", "scheduled"):
            continue

        if entry.get("auto_post") is True:
            result = perform_post(entry)
            mark_posted(entry)
            changed = True
            log_worker(result)
            continue

        sched_str = entry.get("scheduled_at")
        if sched_str:
            try:
                sched = datetime.fromisoformat(sched_str)
                if now >= sched:
                    result = perform_post(entry)
                    mark_posted(entry)
                    changed = True
                    log_worker(result)
            except Exception as e:
                warn_worker(f"Fehler beim Lesen von scheduled_at für ID {entry.get('id')}: {e}")

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


# === TELEGRAM-BEFEHLE: REEL ===
def handle_reel_command(text):
    parts = text.split(" ", 1)
    if len(parts) < 2:
        return "❌ Bitte nutze: reel <Thema>"

    thema = parts[1].strip()
    script = generate_reel_script(thema)
    json_path, txt_path = save_reel_script(script)

    if SOCIAL_CFG.get("auto_store_posts", True):
        add_to_posting_queue(script, json_path, txt_path)

    return (
        f"🎬 Reel-Skript erstellt für: {thema}\n"
        f"📁 Gespeichert unter:\n"
        f"- {json_path}\n"
        f"- {txt_path}"
    )


# === TELEGRAM-BEFEHLE: POSTING ===
def handle_post_now(text):
    parts = text.split(" ", 2)
    if len(parts) < 3:
        return "❌ Bitte nutze: post now <Thema>"

    thema = parts[2].strip()
    queue = load_posting_queue()

    for entry in queue:
        if entry["thema"].lower() == thema.lower() and entry["status"] in ("pending", "scheduled"):
            entry["auto_post"] = True
            save_posting_queue(queue)
            return f"🚀 Posting für '{thema}' wird sofort ausgeführt."

    return f"❌ Kein aktiver Eintrag für '{thema}' gefunden."


def handle_post_schedule(text):
    # Format: post schedule <YYYY-MM-DD> <HH:MM> <Thema...>
    parts = text.split(" ", 4)
    if len(parts) < 5:
        return "❌ Bitte nutze: post schedule <YYYY-MM-DD> <HH:MM> <Thema>"

    date_str = parts[2].strip()
    time_str = parts[3].strip()
    thema = parts[4].strip()

    try:
        sched = datetime.fromisoformat(f"{date_str} {time_str}")
    except Exception:
        return "❌ Datum/Uhrzeit ungültig. Format: YYYY-MM-DD HH:MM"

    queue = load_posting_queue()
    for entry in queue:
        if entry["thema"].lower() == thema.lower() and entry["status"] in ("pending", "scheduled"):
            entry["scheduled_at"] = sched.isoformat()
            entry["status"] = "scheduled"
            save_posting_queue(queue)
            return f"📅 Posting für '{thema}' geplant am {sched}."

    return f"❌ Kein aktiver Eintrag für '{thema}' gefunden."


def handle_post_cancel(text):
    parts = text.split(" ", 2)
    if len(parts) < 3:
        return "❌ Bitte nutze: post cancel <ID>"

    try:
        post_id = int(parts[2].strip())
    except ValueError:
        return "❌ ID muss eine Zahl sein."

    return cancel_post_by_id(post_id)


def handle_post_clear():
    return clear_queue()


def handle_queue_command():
    return get_queue_overview()


def handle_post_status():
    return queue_status()


def handle_post_list():
    return get_queue_overview()


def handle_post_command(text):
    t = text.lower().strip()

    if t.startswith("post now"):
        return handle_post_now(text)
    if t.startswith("post schedule"):
        return handle_post_schedule(text)
    if t.startswith("post cancel"):
        return handle_post_cancel(text)
    if t.startswith("post clear"):
        return handle_post_clear()
    if t.startswith("post status"):
        return handle_post_status()
    if t.startswith("post list"):
        return handle_post_list()

    return (
        "❌ Unbekannter Post-Befehl.\n"
        "Verfügbar:\n"
        "· post now <Thema>\n"
        "· post schedule <YYYY-MM-DD> <HH:MM> <Thema>\n"
        "· post cancel <ID>\n"
        "· post clear\n"
        "· post status\n"
        "· post list\n"
    )


# === FABRIK & CLUSTER TELEGRAM-BEFEHLE ===
def handle_fabrik_command(text):
    parts = text.split(" ", 1)
    if len(parts) < 2:
        return "❌ Bitte nutze: fabrik <Thema>"
    thema = parts[1].strip()
    FABRIK.add_task(thema, fabrik_callback)
    return f"🏭 Fabrik-Task erstellt für: {thema}"


def handle_cluster_command(text):
    parts = text.split(" ", 1)
    if len(parts) < 2:
        return "❌ Bitte nutze: cluster <Thema>"
    thema = parts[1].strip()
    return create_cluster_tasks(thema)


# === SCHEDULER (Phase 7D) ===

SCHEDULER_STATE_FILE = os.path.join(CONFIG_DIR, "scheduler_state.json")

# Daily-Time (Serverzeit)
DAILY_TIME_STR = "10:00"  # HH:MM
DAILY_TIME = dtime.fromisoformat(DAILY_TIME_STR)

# Weekly Topics (0=Montag ... 6=Sonntag)
WEEKLY_TOPICS = {
    0: "Automation Basics",
    1: "KI Tools",
    2: "Business Automation",
    3: "Marketing Automation",
    4: "Mindset & Systems",
}

# Evergreen-Themenliste
EVERGREEN_TOPICS = [
    "KI Automation",
    "Content Automation",
    "Lead Generierung mit Automation",
    "Sales Funnels automatisieren",
    "Onboarding automatisieren",
    "Reporting automatisieren",
    "Social Media Automation",
    "E-Mail Automation",
    "Prozessdokumentation mit KI",
    "Agenten-Systeme im Business",
]


def load_scheduler_state():
    default = {
        "paused": False,
        "last_daily_date": None,
        "last_weekly_date": None,
        "evergreen_index": 0,
    }
    state = load_json(SCHEDULER_STATE_FILE, default)
    if not isinstance(state, dict):
        state = default
        save_scheduler_state(state)
    return state


def save_scheduler_state(state):
    save_json(SCHEDULER_STATE_FILE, state)


def scheduler_run_daily(state=None):
    if state is None:
        state = load_scheduler_state()

    idx = state.get("evergreen_index", 0)
    if not EVERGREEN_TOPICS:
        return "❌ Keine Evergreen-Themen definiert."

    thema = EVERGREEN_TOPICS[idx % len(EVERGREEN_TOPICS)]

    FABRIK.add_task(thema, fabrik_callback)

    script = generate_reel_script(thema)
    json_path, txt_path = save_reel_script(script)
    add_to_posting_queue(script, json_path, txt_path)

    state["evergreen_index"] = idx + 1
    state["last_daily_date"] = datetime.now().date().isoformat()
    save_scheduler_state(state)

    return f"📆 Daily-Scheduler ausgeführt für Thema: {thema}"


def scheduler_run_weekly(state=None):
    if state is None:
        state = load_scheduler_state()

    now = datetime.now()
    weekday = now.weekday()
    thema = WEEKLY_TOPICS.get(weekday)

    if not thema:
        return "ℹ️ Kein Weekly-Thema für diesen Wochentag definiert."

    FABRIK.add_task(thema, fabrik_callback)

    script = generate_reel_script(thema)
    json_path, txt_path = save_reel_script(script)
    add_to_posting_queue(script, json_path, txt_path)

    state["last_weekly_date"] = now.date().isoformat()
    save_scheduler_state(state)

    return f"📆 Weekly-Scheduler ausgeführt für Thema: {thema}"


def scheduler_run_evergreen(state=None):
    if state is None:
        state = load_scheduler_state()

    idx = state.get("evergreen_index", 0)
    if not EVERGREEN_TOPICS:
        return "❌ Keine Evergreen-Themen definiert."

    thema = EVERGREEN_TOPICS[idx % len(EVERGREEN_TOPICS)]

    FABRIK.add_task(thema, fabrik_callback)

    script = generate_reel_script(thema)
    json_path, txt_path = save_reel_script(script)
    add_to_posting_queue(script, json_path, txt_path)

    state["evergreen_index"] = idx + 1
    save_scheduler_state(state)

    return f"🔁 Evergreen-Scheduler ausgeführt für Thema: {thema}"


def scheduler_tick():
    state = load_scheduler_state()
    if state.get("paused"):
        return

    now = datetime.now()
    today_str = now.date().isoformat()
    current_time = now.time()

    last_daily = state.get("last_daily_date")
    last_weekly = state.get("last_weekly_date")

    if current_time >= DAILY_TIME and last_daily != today_str:
        msg = scheduler_run_daily(state)
        log_worker(msg)

    weekday = now.weekday()
    if current_time >= DAILY_TIME and last_weekly != today_str and weekday in WEEKLY_TOPICS:
        msg = scheduler_run_weekly(state)
        log_worker(msg)


def scheduler_status():
    state = load_scheduler_state()
    paused = state.get("paused", False)
    last_daily = state.get("last_daily_date")
    last_weekly = state.get("last_weekly_date")
    evergreen_index = state.get("evergreen_index", 0)

    next_evergreen = None
    if EVERGREEN_TOPICS:
        next_evergreen = EVERGREEN_TOPICS[evergreen_index % len(EVERGREEN)