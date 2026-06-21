# core/Logik.py

import os
from datetime import datetime
from typing import List, Dict, Any, Optional

# === interne Utils ===
from core.utils import (
    BASE_DIR,
    load_json,
    save_json,
    log_worker,
    warn_worker,
    error_worker,
)

# === Module für Posting ===
from modules.upload_engine import UploadEngine
from modules.instagram_poster import InstagramPoster

# === Pfad für Posting-Queue ===
POSTING_QUEUE_FILE = os.path.join(BASE_DIR, "posting_queue.json")

# === Env-Variablen für Instagram ===
IG_ACCESS_TOKEN = os.environ.get("IG_ACCESS_TOKEN", "").strip()
IG_USER_ID = os.environ.get("IG_USER_ID", "").strip()
# === Posting-Queue laden ===
def load_posting_queue() -> List[Dict[str, Any]]:
    queue = load_json(POSTING_QUEUE_FILE, [])
    if not isinstance(queue, list):
        warn_worker("Posting-Queue war beschädigt – neu initialisiert.")
        queue = []
        save_posting_queue(queue)
    return queue


# === Posting-Queue speichern ===
def save_posting_queue(queue: List[Dict[str, Any]]) -> None:
    save_json(POSTING_QUEUE_FILE, queue)


# === Eintrag zur Queue hinzufügen ===
def add_to_posting_queue(
    video_path: str,
    caption: str,
    scheduled_at: Optional[str] = None,
    auto_post: bool = True,
) -> Dict[str, Any]:
    queue = load_posting_queue()

    entry = {
        "id": f"{int(datetime.now().timestamp())}",
        "video_path": video_path,
        "caption": caption,
        "scheduled_at": scheduled_at,  # ISO-String oder None
        "auto_post": auto_post,
        "status": "pending",  # pending | scheduled | posted | error
        "created_at": datetime.now().isoformat(),
        "posted_at": None,
        "last_error": None,
    }

    queue.append(entry)
    save_posting_queue(queue)
    log_worker(f"📝 Neuer Posting-Queue-Eintrag: {entry['id']}")
    return entry


# === Queue als Text auflisten (für KI-Antwort) ===
def format_posting_queue() -> str:
    queue = load_posting_queue()
    if not queue:
        return "📭 Posting-Queue ist leer."

    lines = ["📋 Posting-Queue:"]
    for e in queue:
        lines.append(
            f"- ID: {e.get('id')} | Status: {e.get('status')} | "
            f"Auto: {e.get('auto_post')} | Geplant: {e.get('scheduled_at')} | "
            f"Video: {e.get('video_path')}"
        )
    return "\n".join(lines)


# === Queue leeren ===
def clear_posting_queue() -> str:
    save_posting_queue([])
    log_worker("🧹 Posting-Queue geleert.")
    return "🧹 Posting-Queue wurde geleert."
# === InstagramPoster-Instanz holen ===
def get_instagram_poster() -> Optional[InstagramPoster]:
    if not IG_ACCESS_TOKEN or not IG_USER_ID:
        error_worker("❌ IG_ACCESS_TOKEN oder IG_USER_ID fehlt – kein Instagram-Posting möglich.")
        return None
    return InstagramPoster(IG_ACCESS_TOKEN, IG_USER_ID)


# === Einzelnen Post wirklich ausführen ===
def perform_post(entry: Dict[str, Any]) -> bool:
    video_path = entry.get("video_path")
    caption = entry.get("caption", "")

    if not video_path or not os.path.exists(video_path):
        msg = f"Video-Datei nicht gefunden: {video_path}"
        error_worker(f"❌ {msg}")
        entry["status"] = "error"
        entry["last_error"] = msg
        return False

    # 1) Upload zu GitHub-CDN via UploadEngine
    uploader = UploadEngine()
    public_url = uploader.upload(video_path)
    if not public_url:
        msg = "Konnte öffentliche URL nicht erzeugen."
        error_worker(f"❌ {msg}")
        entry["status"] = "error"
        entry["last_error"] = msg
        return False

    # 2) Reel zu Instagram posten
    poster = get_instagram_poster()
    if not poster:
        msg = "InstagramPoster nicht verfügbar (Env-Variablen fehlen)."
        error_worker(f"❌ {msg}")
        entry["status"] = "error"
        entry["last_error"] = msg
        return False

    try:
        result = poster.post_reel(public_url, caption)
        if "id" not in result:
            msg = f"Instagram-API-Fehler: {result}"
            error_worker(f"❌ {msg}")
            entry["status"] = "error"
            entry["last_error"] = msg
            return False

        log_worker(f"🎉 Reel erfolgreich gepostet. ID: {result['id']}")
        entry["status"] = "posted"
        entry["posted_at"] = datetime.now().isoformat()
        entry["last_error"] = None
        return True

    except Exception as e:
        msg = f"Exception beim Posten: {e}"
        error_worker(f"❌ {msg}")
        entry["status"] = "error"
        entry["last_error"] = msg
        return False
# === Auto-Posting-Tick (vom Worker aufgerufen) ===
def auto_posting_tick() -> None:
    """
    Wird vom Agent_Worker in jeder Schleife aufgerufen.
    Prüft die Posting-Queue und führt fällige Posts aus.
    """
    queue = load_posting_queue()
    if not queue:
        return

    now = datetime.now()
    changed = False

    for entry in queue:
        status = entry.get("status", "pending")
        auto_post = entry.get("auto_post", False)
        sched_str = entry.get("scheduled_at")

        # Bereits gepostet oder Fehler -> überspringen
        if status in ("posted", "error"):
            continue

        # Geplanter Zeitpunkt
        sched_ok = False
        if sched_str:
            try:
                sched_dt = datetime.fromisoformat(sched_str)
                if now >= sched_dt:
                    sched_ok = True
            except Exception as e:
                warn_worker(f"⚠️ Ungültiges Datum in scheduled_at: {sched_str} ({e})")

        # Bedingungen:
        # - auto_post ohne Datum -> sofort
        # - auto_post mit Datum -> ab Zeitpunkt
        if auto_post and (sched_ok or not sched_str):
            log_worker(f"⏰ Auto-Posting fällig für ID {entry.get('id')}")
            success = perform_post(entry)
            if success:
                changed = True
            else:
                changed = True  # Status wurde auf error gesetzt

    if changed:
        save_posting_queue(queue)
# === KI-Anfrage verarbeiten ===
def process_ki_anfrage(text: str) -> str:
    """
    Einfacher Router für KI-Befehle.
    Hier kannst du später Scheduler-, Fabrik-, Cluster- usw. Befehle ergänzen.
    """
    if not text:
        return "Kein Text übergeben."

    raw = text.strip()
    lower = raw.lower()

    # --- Posting-Queue-Befehle ---
    if lower.startswith("queue add "):
        # Format: queue add <video_path> | <caption> | [YYYY-MM-DDTHH:MM]
        try:
            payload = raw[len("queue add "):].strip()
            parts = [p.strip() for p in payload.split("|")]

            video_path = parts[0]
            caption = parts[1] if len(parts) > 1 else ""
            scheduled_at = parts[2] if len(parts) > 2 and parts[2] else None

            entry = add_to_posting_queue(video_path, caption, scheduled_at, auto_post=True)
            return (
                "✅ Posting zur Queue hinzugefügt:\n"
                f"ID: {entry['id']}\n"
                f"Video: {entry['video_path']}\n"
                f"Caption: {entry['caption']}\n"
                f"Geplant: {entry['scheduled_at']}\n"
                f"Auto-Post: {entry['auto_post']}"
            )
        except Exception as e:
            error_worker(f"❌ Fehler bei 'queue add': {e}")
            return f"❌ Fehler beim Hinzufügen zur Queue: {e}"

    if lower == "queue list":
        return format_posting_queue()

    if lower == "queue clear":
        return clear_posting_queue()

    # --- Systemcheck ---
    if lower == "ping":
        return "🏓 Pong – System läuft."

    # --- Fallback ---
    return f"Unbekannter Befehl oder noch nicht implementiert: {raw}"
