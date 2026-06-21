# core/Logik.py

import os
from datetime import datetime
from typing import List, Dict, Any, Optional

from core.utils import (
    BASE_DIR,
    load_json,
    save_json,
    log_worker,
    warn_worker,
    error_worker,
)

from modules.upload_engine import UploadEngine
from modules.instagram_poster import InstagramPoster
from modules.dialog_engine import DialogEngine

POSTING_QUEUE_FILE = os.path.join(BASE_DIR, "posting_queue.json")

IG_ACCESS_TOKEN = os.environ.get("IG_ACCESS_TOKEN", "").strip()
IG_USER_ID = os.environ.get("IG_USER_ID", "").strip()

dialog_engine = DialogEngine()
def load_posting_queue() -> List[Dict[str, Any]]:
    queue = load_json(POSTING_QUEUE_FILE, [])
    if not isinstance(queue, list):
        warn_worker("Posting-Queue war beschädigt – neu initialisiert.")
        queue = []
        save_posting_queue(queue)
    return queue


def save_posting_queue(queue: List[Dict[str, Any]]) -> None:
    save_json(POSTING_QUEUE_FILE, queue)


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
        "scheduled_at": scheduled_at,
        "auto_post": auto_post,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "posted_at": None,
        "last_error": None,
    }

    queue.append(entry)
    save_posting_queue(queue)
    log_worker(f"📝 Neuer Posting-Queue-Eintrag: {entry['id']}")
    return entry


def format_posting_queue() -> str:
    queue = load_posting_queue()
    if not queue:
        return "📭 Posting-Queue ist leer."

    lines = ["📋 Posting-Queue:"]
    for e in queue:
        lines.append(
            f"- ID: {e['id']} | Status: {e['status']} | Auto: {e['auto_post']} | "
            f"Geplant: {e['scheduled_at']} | Video: {e['video_path']}"
        )
    return "\n".join(lines)


def clear_posting_queue() -> str:
    save_posting_queue([])
    log_worker("🧹 Posting-Queue geleert.")
    return "🧹 Posting-Queue wurde geleert."
def get_instagram_poster() -> Optional[InstagramPoster]:
    if not IG_ACCESS_TOKEN or not IG_USER_ID:
        error_worker("❌ IG_ACCESS_TOKEN oder IG_USER_ID fehlt – kein Instagram-Posting möglich.")
        return None
    return InstagramPoster(IG_ACCESS_TOKEN, IG_USER_ID)


def perform_post(entry: Dict[str, Any]) -> bool:
    video_path = entry["video_path"]
    caption = entry["caption"]

    if not os.path.exists(video_path):
        msg = f"Video-Datei nicht gefunden: {video_path}"
        error_worker(msg)
        entry["status"] = "error"
        entry["last_error"] = msg
        return False

    uploader = UploadEngine()
    public_url = uploader.upload(video_path)
    if not public_url:
        msg = "Konnte öffentliche URL nicht erzeugen."
        error_worker(msg)
        entry["status"] = "error"
        entry["last_error"] = msg
        return False

    poster = get_instagram_poster()
    if not poster:
        msg = "InstagramPoster nicht verfügbar."
        error_worker(msg)
        entry["status"] = "error"
        entry["last_error"] = msg
        return False

    try:
        result = poster.post_reel(public_url, caption)
        if "id" not in result:
            msg = f"Instagram-API-Fehler: {result}"
            error_worker(msg)
            entry["status"] = "error"
            entry["last_error"] = msg
            return False

        entry["status"] = "posted"
        entry["posted_at"] = datetime.now().isoformat()
        entry["last_error"] = None
        log_worker(f"🎉 Reel veröffentlicht: {result['id']}")
        return True

    except Exception as e:
        msg = f"Exception beim Posten: {e}"
        error_worker(msg)
        entry["status"] = "error"
        entry["last_error"] = msg
        return False
def auto_posting_tick() -> None:
    queue = load_posting_queue()
    if not queue:
        return

    now = datetime.now()
    changed = False

    for entry in queue:
        if entry["status"] in ("posted", "error"):
            continue

        sched = entry["scheduled_at"]
        auto = entry["auto_post"]

        sched_ok = False
        if sched:
            try:
                sched_dt = datetime.fromisoformat(sched)
                if now >= sched_dt:
                    sched_ok = True
            except Exception:
                warn_worker(f"⚠️ Ungültiges Datum: {sched}")

        if auto and (sched_ok or not sched):
            log_worker(f"⏰ Auto-Posting fällig für ID {entry['id']}")
            perform_post(entry)
            changed = True

    if changed:
        save_posting_queue(queue)
def process_ki_anfrage(text: str) -> str:
    if not text:
        return "Kein Text übergeben."

    intent = dialog_engine.detect_intent(text)

    if intent == "queue_add":
        video_path, caption, scheduled_at = dialog_engine.extract_queue_add(text)
        if not video_path:
            return "❌ Format: queue add <video> | <caption> | [YYYY-MM-DDTHH:MM]"
        entry = add_to_posting_queue(video_path, caption, scheduled_at)
        return dialog_engine.generate_response("queue_add", entry)

    if intent == "queue_list":
        return dialog_engine.generate_response("queue_list", format_posting_queue())

    if intent == "queue_clear":
        clear_posting_queue()
        return dialog_engine.generate_response("queue_clear")

    if intent in ("ping", "greeting", "thanks"):
        return dialog_engine.generate_response(intent)

    return dialog_engine.generate_response("chat", text)


# Worker-Kompatibilität (dein Worker importiert diesen Namen!)
process_ki_Anfrage = process_ki_anfrage
