from typing import Any, Dict, List, Tuple
from collections import defaultdict

from doctor_core.logging import log_doctor
from doctor_core.engine_manager import EngineManager
from modules.analytics_engine import AnalyticsEngine


class OptimizerEngine:
    """
    PRO-Version der OptimizerEngine:
    - Analysiert Content-Performance basierend auf einer gewichteten Conversion-Matrix (Leads & Sales).
    - Greift über den EngineManager direkt auf die relationale AnalyticsEngine zu.
    - Generiert strukturierte Rankings für Evergreen- und Weekly-Kampagnen.
    """

    def __init__(self, engine_manager: EngineManager):
        self.engines = engine_manager
        
        # Sicherstellen, dass die AnalyticsEngine im System registriert ist
        if not self.engines.has("analytics"):
            self.analytics = AnalyticsEngine(self.engines)
        else:
            self.analytics = self.engines.get("analytics")

    def _score_metrics(self, metrics: Dict[str, Any]) -> float:
        """
        Berechnet den Performance-Score eines Events.
        Berücksichtigt Leads und Sales mit starker Gewichtung.
        """
        try:
            views = float(metrics.get("views", 0))
            likes = float(metrics.get("likes", 0))
            comments = float(metrics.get("comments", 0))
            shares = float(metrics.get("shares", 0))
            leads = float(metrics.get("leads", 0))
            sales = float(metrics.get("sales", 0))

            return (
                views * 0.1
                + likes * 1.0
                + comments * 2.0
                + shares * 3.0
                + leads * 10.0
                + sales * 20.0
            )
        except (ValueError, TypeError) as e:
            log_doctor(f"OptimizerEngine-Warnung: Fehler beim Parsen der Metriken: {e}")
            return 0.0

    def aggregate_scores_by_prefix(self, prefix: str) -> Dict[str, float]:
        """
        Filtert Events nach einem ID-Präfix (z.B. 'evergreen_') und summiert die Scores.
        """
        events = self.analytics.load_events()
        scores: Dict[str, float] = defaultdict(float)

        log_doctor(f"OptimizerEngine: Aggregiere Scores für Präfix '{prefix}' aus {len(events)} Events...")

        for ev in events:
            cid = ev.get("content_id", "")
            if not cid.startswith(prefix):
                continue
                
            score = self._score_metrics(ev.get("metrics", {}))
            scores[cid] += score

        return dict(scores)

    def rank_ids_by_score(self, prefix: str) -> List[Tuple[str, float]]:
        """Gibt eine sortierte Liste von Content-IDs und deren Scores zurück."""
        scores = self.aggregate_scores_by_prefix(prefix)
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked

    def build_evergreen_ranking(self) -> str:
        """Erstellt einen formatierten Bericht für das Evergreen-Content-Ranking."""
        ranked = self.rank_ids_by_score("evergreen_")
        if not ranked:
            return "📊 Noch keine Analytics-Daten für Evergreen-Themen vorhanden."

        lines = ["📊 **Evergreen-Ranking nach Performance:**"]
        for cid, score in ranked:
            lines.append(f"- {cid}: Score {score:.2f}")
        return "\n".join(lines)

    def build_weekly_ranking(self) -> str:
        """Erstellt einen formatierten Bericht für das wöchentliche Content-Ranking."""
        ranked = self.rank_ids_by_score("weekly_")
        if not ranked:
            return "📊 Noch keine Analytics-Daten für Weekly-Themen vorhanden."

        lines = ["📊 **Weekly-Ranking nach Performance:**"]
        for cid, score in ranked:
            lines.append(f"- {cid}: Score {score:.2f}")
        return "\n".join(lines)


# Abwärtskompatible Funktionen für Altsysteme
def build_evergreen_ranking_legacy(engine_manager: EngineManager) -> str:
    """Erlaubt Legacy-Modulen den Aufruf des Evergreen-Rankings."""
    optimizer = OptimizerEngine(engine_manager)
    return optimizer.build_evergreen_ranking()


def build_weekly_ranking_legacy(engine_manager: EngineManager) -> str:
    """Erlaubt Legacy-Modulen den Aufruf des Weekly-Rankings."""
    optimizer = OptimizerEngine(engine_manager)
    return optimizer.build_weekly_ranking()