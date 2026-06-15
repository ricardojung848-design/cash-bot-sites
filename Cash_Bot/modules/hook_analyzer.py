# modules/hook_analyzer.py

from collections import defaultdict
from typing import Dict, List, Any
from modules.analytics_engine import load_events

def extract_hook_patterns() -> Dict[str, float]:
    """
    Analysiert alle Hooks aus Analytics-Events und berechnet Scores.
    Score basiert auf Engagement: likes, comments, shares, views.
    """
    events = load_events()
    pattern_scores = defaultdict(float)

    for ev in events:
        meta = ev.get("meta", {})
        hook = meta.get("hook")
        if not hook:
            continue

        metrics = ev.get("metrics", {})
        score = (
            metrics.get("likes", 0) * 1.5 +
            metrics.get("comments", 0) * 3 +
            metrics.get("shares", 0) * 4 +
            metrics.get("views", 0) * 0.1
        )

        pattern_scores[hook] += score

    return dict(pattern_scores)


def get_top_hooks(n: int = 5) -> List[str]:
    patterns = extract_hook_patterns()
    ranked = sorted(patterns.items(), key=lambda x: x[1], reverse=True)
    return [h for h, s in ranked[:n]]
