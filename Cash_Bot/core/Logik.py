import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Sicherstellen, dass das Root-Verzeichnis im Systempfad liegt
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from doctor_core.logging import log_doctor
from doctor_core.engine_manager import EngineManager
from core.utils import load_json, save_json

# Definition der Queue-Datei im Hauptverzeichnis
POSTING_QUEUE_FILE = os.path.join(str(BASE_DIR), "posting_queue.json")

# Token-Abfrage aus den System-Umgebungsvariablen
IG_ACCESS_TOKEN = os.environ.get("IG_ACCESS_TOKEN", "").strip()
IG_USER_ID = os.environ.get("IG_USER_ID", "").strip()


# ---------------------------------------------------------
# Posting-Queue Operationen
# ---------------------------------------------------------
def load_posting_queue() -> List[Dict[str, Any]]:
    """Lädt die anstehenden Instagram-Posts aus der JSON-Warteschlange."""
    queue = load_json(POSTING_QUEUE_FILE, [])
    if not isinstance(queue, list):
        log_doctor("Logik-Warnung: Posting-Queue war beschädigt – neu initialisiert.")
        queue = []
        save_posting_queue(queue)
    return queue


def save_posting_queue(queue: List[Dict[str, Any]]) -> None:
    """Speichert den aktuellen Zustand der Posting-Queue im Dateisystem."""
    save_json(POSTING_QUEUE_FILE, queue)


def add_to_posting_queue(
    video_path: str,
    caption: str,
    scheduled_at: Optional[str] = None,
    auto_post: bool = True,
) -> Dict[str, Any]:
    """Erstellt einen neuen Eintrag und reiht ihn in die Warteschlange ein."""
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
    log_doctor(f"Logik: 📝 Neuer Posting-Queue-Eintrag registriert: {entry['id']}")
    return entry


def format_posting_queue() -> str:
    """Erstellt eine lesbare Zusammenfassung der Queue für Chat-Interfaces."""
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
    """Leert die gesamte Content-Pipeline."""
    save_posting_queue([])
    log_doctor("Logik: 🧹 Posting-Queue vollständig geleert.")
    return "🧹 Posting-Queue wurde geleert."


# ---------------------------------------------------------
# Posting-Ausführung über Engines
# ---------------------------------------------------------
def perform_post(entry: Dict[str, Any], manager: EngineManager) -> bool:
    """
    Führt den eigentlichen Upload- und Instagram-Posting-Prozess aus.
    Nutzt den übergebenen EngineManager für eine saubere Ressourcenverwaltung.
    """
    video_path = entry["video_path"]
    caption = entry["caption"]

    if not os.path.exists(video_path):
        msg = f"Video-Datei nicht gefunden: {video_path}"
        log_doctor(f"Logik-Fehler: {msg}")
        entry["status"] = "error"
        entry["last_error"] = msg
        return False

    # 1) Video über UploadEngine ins öffentliche CDN schieben
    try:
        from modules.upload_engine import UploadEngine
        uploader = UploadEngine(manager)
        public_url = uploader.upload(video_path)
    except Exception as e:
        public_url = None
        log_doctor(f"Logik-Fehler: UploadEngine konnte nicht geladen werden: {e}")

    if not public_url:
        msg = "Konnte öffentliche CDN-URL nicht erzeugen."
        log_doctor(f"Logik-Fehler: {msg}")
        entry["status"] = "error"
        entry["last_error"] = msg
        return False

    # 2) Video über InstagramPoster via Meta Graph API veröffentlichen
    if not IG_ACCESS_TOKEN or not IG_USER_ID:
        msg = "Instagram-Credentials (Token/ID) fehlen in den Umgebungsvariablen."
        log_doctor(f"Logik-Fehler: {msg}")
        entry["status"] = "error"
        entry["last_error"] = msg
        return False

    try:
        from modules.instagram_poster import InstagramPoster
        poster = InstagramPoster(IG_ACCESS_TOKEN, IG_USER_ID)
        result = poster.post_reel(public_url, caption)
        
        if "id" not in result:
            msg = f"Instagram-API-Fehler: {result}"
            log_doctor(f"Logik-Fehler: {msg}")
            entry["status"] = "error"
            entry["last_error"] = msg
            return False

        entry["status"] = "posted"
        entry["posted_at"] = datetime.now().isoformat()
        entry["last_error"] = None
        log_doctor(f"Logik: 🎉 Reel erfolgreich auf Instagram veröffentlicht! ID: {result['id']}")
        return True

    except Exception as e:
        msg = f"Exception beim Instagram-Posting-Vorgang: {e}"
        log_doctor(f"Logik-Kritisch: {msg}")
        entry["status"] = "error"
        entry["last_error"] = msg
        return False


# ---------------------------------------------------------
# Core-Schnittstellen für den Agent_Worker
# ---------------------------------------------------------
def auto_posting_tick(manager: EngineManager) -> None:
    """Überprüft zeitgesteuerte Einträge in der Queue und triggert fällige Uploads."""
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
                log_doctor(f"Logik-Warnung: Ungültiges ISO-Datum in Queue gefunden: {sched}")

        if auto and (sched_ok or not sched):
            log_doctor(f"Logik: ⏰ Auto-Posting-Event ausgelöst für ID {entry['id']}")
            # Hier den Manager direkt an perform_post weitergeben
            perform_post(entry, manager)
            changed = True

    if changed:
        save_posting_queue(queue)


def process_ki_anfrage(text: str) -> str:
    """Verarbeitet eingehende Chatanfragen mithilfe der DialogEngine NLP-Struktur."""
    if not text:
        return "Kein Text übergeben."

    try:
        from modules.dialog_engine import DialogEngine
        dialog_engine = DialogEngine()
    except Exception as e:
        log_doctor(f"Logik-Kritisch: DialogEngine konnte nicht initialisiert werden: {e}")
        return "🤖 Interner Systemfehler: DialogEngine offline."

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

    # Fallback für alle Standard-Intents (ping, greeting, thanks, etc.)
    return dialog_engine.generate_response(intent, text)


# Abwärtskompatibilität für alternative CamelCase-Schreibweisen im Altsystem sichern
process_ki_Anfrage = process_ki_anfrage