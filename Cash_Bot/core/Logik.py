"""
core/Logik.py – CashBot / Logik (Version B+ – Agentur-Level, mit Fabrik-Pipelines + Phase 10 Analytics)

Enthält:
- JSON-basierte Posting-Queue (pending, scheduled, posted, cancelled)
- Auto-Posting-Engine (auto_posting_tick)
- Reel-Engine (Reel-Skripte generieren + speichern)
- Fabrik-Engine 2.0 (Templates, Auto-Content, Multi-Output)
- Cluster-Engine (Keyword-Cluster + FABRIK-Tasks)
- Pipeline-Engine (Daily + Weekly Pipelines: C1 + C2)
- Scheduler-Engine (Daily, Weekly, Evergreen – Mo–Sa, 18:00)
- Scheduler-Command-Engine (inkl. Analytics-Commands)
- KI-Router (process_ki_anfrage) für Telegram-/KI-Befehle

Kompatibel mit:
from core.Logik import process_ki_anfrage, auto_posting_tick
"""

from __future__ import annotations

import os
from datetime import datetime, time as dtime
from typing import Any, Dict, List, Optional, Tuple

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
from modules.analytics_engine import log_event
from modules.optimizer_engine import build_evergreen_ranking, build_weekly_ranking


# ---------------------------------------------------------------------------
# Konfiguration laden
# ---------------------------------------------------------------------------

CONFIG_FILE = os.path.join(CONFIG_DIR, "cashbot_config.json")

DEFAULT_CONFIG = {
    "nische": "Business Automation",
    "produkt_typ": "Automations-Dienstleistungen & KI-Beratung",
    "social_media": {
        "instagram_reels": True,
        "auto_store_posts": True,
        "auto_post": False,
    },
}

CONFIG = load_json(CONFIG_FILE, DEFAULT_CONFIG)
NISCHE = CONFIG["nische"]
PRODUKT_TYP = CONFIG["produkt_typ"]
SOCIAL_CFG = CONFIG["social_media"]


# ---------------------------------------------------------------------------
# Posting-Queue (JSON-basiert)
# ---------------------------------------------------------------------------

POSTING_QUEUE_FILE = os.path.join(SOCIAL_DIR, "posting_queue.json")


class PostingQueue:
    """
    JSON-basierte Posting-Queue.
    Status: pending | scheduled | posted | cancelled
    """

    def __init__(self, path: str) -> None:
        self.path = path
        self._ensure_file()

    def _ensure_file(self) -> None:
        queue = load_json(self.path, [])
        if not isinstance(queue, list):
            warn_worker("Posting-Queue war beschädigt – neu initialisiert.")
            queue = []
            save_json(self.path, queue)

    def _load(self) -> List[Dict[str, Any]]:
        queue = load_json(self.path, [])
        if not isinstance(queue, list):
            warn_worker("Posting-Queue war beschädigt – neu initialisiert.")
            queue = []
            save_json(self.path, queue)
        return queue

    def _save(self, queue: List[Dict[str, Any]]) -> None:
        save_json(self.path, queue)

    def _next_id(self, queue: List[Dict[str, Any]]) -> int:
        if not queue:
            return 1
        return max(item.get("id", 0) for item in queue) + 1

    def add_entry(
        self,
        script: Dict[str, Any],
        json_path: str,
        txt_path: str,
        auto_post: bool = False,
    ) -> Dict[str, Any]:
        queue = self._load()
        entry = {
            "id": self._next_id(queue),
            "thema": script["thema"],
            "nische": script["nische"],
            "produkt_typ": script["produkt_typ"],
            "json_path": json_path,
            "txt_path": txt_path,
            "status": "pending",  # pending | scheduled | posted | cancelled
            "scheduled_at": None,
            "platforms": ["instagram"],
            "auto_post": auto_post,
            "created_at": datetime.now().isoformat(),
            "posted_at": None,
            "cancelled_at": None,
        }
        queue.append(entry)
        self._save(queue)
        return entry

    def list_entries(self) -> List[Dict[str, Any]]:
        return self._load()

    def save_entries(self, queue: List[Dict[str, Any]]) -> None:
        self._save(queue)

    def clear(self) -> None:
        self._save([])

    def cancel_by_id(self, post_id: int) -> str:
        queue = self._load()
        for item in queue:
            if item.get("id") == post_id and item["status"] in ("pending", "scheduled"):
                item["status"] = "cancelled"
                item["cancelled_at"] = datetime.now().isoformat()
                self._save(queue)
                return f"🛑 Posting mit ID {post_id} wurde abgebrochen."
        return f"❌ Kein aktiver Eintrag mit ID {post_id} gefunden."

    def overview_text(self) -> str:
        queue = self._load()
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

    def status_text(self) -> str:
        queue = self._load()
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


# ---------------------------------------------------------------------------
# Posting-Engine (Auto-Posting + Commands)
# ---------------------------------------------------------------------------

class PostingEngine:
    def __init__(self, queue: PostingQueue) -> None:
        self.queue = queue

    # --- Auto-Posting ------------------------------------------------------

    def _perform_post(self, entry: Dict[str, Any]) -> str:
        log_worker(f"Simuliere Posting für: {entry['thema']}")
        msg = f"💥 Simuliertes Posting veröffentlicht für: {entry['thema']}"
        log_worker(msg)
        return msg

    def _mark_posted(self, entry: Dict[str, Any]) -> None:
        entry["status"] = "posted"
        entry["posted_at"] = datetime.now().isoformat()

    def auto_posting_tick(self) -> None:
        queue = self.queue.list_entries()
        changed = False
        now = datetime.now()

        for entry in queue:
            status = entry.get("status", "pending")

            if status not in ("pending", "scheduled"):
                continue

            # Sofort posten, wenn auto_post=True
            if entry.get("auto_post") is True:
                result = self._perform_post(entry)
                self._mark_posted(entry)
                changed = True
                log_worker(result)
                continue

            # Geplante Zeit prüfen
            sched_str = entry.get("scheduled_at")
            if sched_str:
                try:
                    sched = datetime.fromisoformat(sched_str)
                    if now >= sched:
                        result = self._perform_post(entry)
                        self._mark_posted(entry)
                        changed = True
                        log_worker(result)
                except Exception as e:
                    warn_worker(
                        f"Fehler beim Lesen von scheduled_at für ID {entry.get('id')}: {e}"
                    )

        if changed:
            self.queue.save_entries(queue)

    # --- Commands ----------------------------------------------------------

    def handle_post_now(self, text: str) -> str:
        parts = text.split(" ", 2)
        if len(parts) < 3:
            return "❌ Bitte nutze: post now <Thema>"

        thema = parts[2].strip()
        queue = self.queue.list_entries()

        for entry in queue:
            if entry["thema"].lower() == thema.lower() and entry["status"] in (
                "pending",
                "scheduled",
            ):
                entry["auto_post"] = True
                self.queue.save_entries(queue)
                return f"🚀 Posting für '{thema}' wird sofort ausgeführt."

        return f"❌ Kein aktiver Eintrag für '{thema}' gefunden."

    def handle_post_schedule(self, text: str) -> str:
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

        queue = self.queue.list_entries()
        for entry in queue:
            if entry["thema"].lower() == thema.lower() and entry["status"] in (
                "pending",
                "scheduled",
            ):
                entry["scheduled_at"] = sched.isoformat()
                entry["status"] = "scheduled"
                self.queue.save_entries(queue)
                return f"📅 Posting für '{thema}' geplant am {sched}."

        return f"❌ Kein aktiver Eintrag für '{thema}' gefunden."

    def handle_post_cancel(self, text: str) -> str:
        parts = text.split(" ", 2)
        if len(parts) < 3:
            return "❌ Bitte nutze: post cancel <ID>"

        try:
            post_id = int(parts[2].strip())
        except ValueError:
            return "❌ ID muss eine Zahl sein."

        return self.queue.cancel_by_id(post_id)

    def handle_post_clear(self) -> str:
        self.queue.clear()
        return "🧹 Posting-Queue wurde komplett geleert."

    def handle_post_status(self) -> str:
        return self.queue.status_text()

    def handle_post_list(self) -> str:
        return self.queue.overview_text()

    def handle_post_command(self, text: str) -> str:
        t = text.lower().strip()

        if t.startswith("post now"):
            return self.handle_post_now(text)
        if t.startswith("post schedule"):
            return self.handle_post_schedule(text)
        if t.startswith("post cancel"):
            return self.handle_post_cancel(text)
        if t.startswith("post clear"):
            return self.handle_post_clear()
        if t.startswith("post status"):
            return self.handle_post_status()
        if t.startswith("post list"):
            return self.handle_post_list()

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


# ---------------------------------------------------------------------------
# Reel-Engine
# ---------------------------------------------------------------------------

class ReelEngine:
    def __init__(self, queue: PostingQueue) -> None:
        self.queue = queue

    def generate_reel_script(self, thema: str) -> Dict[str, Any