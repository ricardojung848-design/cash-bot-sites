# modules/analytics_engine.py

import os
from datetime import datetime
from typing import Any, Dict, List

from core.utils import DATA_DIR, load_json, save_json, log_worker, warn_worker

ANALYTICS_FILE = os.path.join(DATA_DIR, "analytics_events.json")


def _ensure_file() -> None:
    data = load_json(ANALYTICS_FILE, [])
    if not isinstance(data, list):
        warn_worker("Analytics-Datei war beschädigt – neu initialisiert.")
        data = []
        save_json(ANALYTICS_FILE, data)


def log_event(
    content_id: str,
    platform: str,
    metrics: Dict[str, Any],
    meta: Dict[str, Any] | None = None,
) -> None:
    """
    content_id: z.B. 'evergreen_12', 'weekly_3', 'reel_automation_basics'
    platform: 'instagram', 'tiktok', 'blog', ...
    metrics: z.B. {"views": 1200, "likes": 130, "comments": 5}
    meta: optional, z.B. {"hook": "...", "cta": "..."}
    """
    _ensure_file()
    events = load_json(ANALYTICS_FILE, [])
    if not isinstance(events, list):
        events = []

    event = {
        "content_id": content_id,
        "platform": platform,
        "metrics": metrics,
        "meta": meta or {},
        "timestamp": datetime.now().isoformat(),
    }
    events.append(event)
    save_json(ANALYTICS_FILE, events)
    log_worker(f"[Analytics] Event geloggt für {content_id} @ {platform}: {metrics}")


def load_events() -> List[Dict[str, Any]]:
    _ensure_file()
    events = load_json(ANALYTICS_FILE, [])
    if not isinstance(events, list):
        events = []
        save_json(ANALYTICS_FILE, events)
    return events
