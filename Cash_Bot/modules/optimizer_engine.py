# modules/optimizer_engine.py

from typing import Any, Dict, List, Tuple
from collections import defaultdict

from core.utils import log_worker
from modules.analytics_engine import load_events


def _score_metrics(metrics: Dict[str, Any]) -> float:
    """
    Ein einfacher Score:
    views * 0.1 + likes * 1 + comments * 2 + shares * 3 + leads * 10 + sales * 20
    Alles optional, wenn nicht vorhanden -> 0.
    """
    views = metrics.get("views", 0)
    likes = metrics.get("likes", 0)
    comments = metrics.get("comments", 0)
    shares = metrics.get("shares", 0)
    leads = metrics.get("leads", 0)
    sales = metrics.get("sales", 0)

    return (
        views * 0.1
        + likes * 1.0
        + comments * 2.0
        + shares * 3.0
        + leads * 10.0
        + sales * 20.0
    )


def aggregate_scores_by_prefix(prefix: str) -> Dict[str, float]:
    """
    prefix: z.B. 'evergreen_' oder 'weekly_'
    Gibt dict zurück: {content_id: score}
    """
    events = load_events()
    scores: Dict[str, float] = defaultdict(float)

    for ev in events:
        cid = ev.get("content_id", "")
        if not cid.startswith(prefix):
            continue
        score = _score_metrics(ev.get("metrics", {}))
        scores[cid] += score

    return dict(scores)


def rank_ids_by_score(prefix: str) -> List[Tuple[str, float]]:
    scores = aggregate_scores_by_prefix(prefix)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked


def build_evergreen_ranking() -> str:
    ranked = rank_ids_by_score("evergreen_")
    if not ranked:
        return "📊 Noch keine Analytics-Daten für Evergreen-Themen vorhanden."

    lines = ["📊 Evergreen-Ranking nach Performance:"]
    for cid, score in ranked:
        lines.append(f"- {cid}: Score {score:.2f}")
    return "\n".join(lines)


def build_weekly_ranking() -> str:
    ranked = rank_ids_by_score("weekly_")
    if not ranked:
        return "📊 Noch keine Analytics-Daten für Weekly-Themen vorhanden."

    lines = ["📊 Weekly-Ranking nach Performance:"]
    for cid, score in ranked:
        lines.append(f"- {cid}: Score {score:.2f}")
    return "\n".join(lines)
