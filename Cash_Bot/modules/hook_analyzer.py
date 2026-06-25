from collections import defaultdict
from typing import Dict, List, Any

from doctor_core.logging import log_doctor
from doctor_core.engine_manager import EngineManager
from modules.analytics_engine import AnalyticsEngine


class HookAnalyzer:
    """
    PRO-Version des HookAnalyzers:
    - Analysiert historische Performance-Daten aus der datenbankgestützten AnalyticsEngine
    - Berechnet gewichtete Engagement-Scores für genutzte Hooks und Formate
    - Liefert der Content-Generierung datenbasierte Empfehlungen für virale Hooks
    """

    def __init__(self, engine_manager: EngineManager):
        self.engines = engine_manager
        
        # Sicherstellen, dass die AnalyticsEngine im Ökosystem bereitsteht
        if not self.engines.has("analytics"):
            # Fallback-Instanziierung, falls noch nicht zentral registriert
            self.analytics = AnalyticsEngine(self.engines)
        else:
            self.analytics = self.engines.get("analytics")

    def extract_hook_patterns(self) -> Dict[str, float]:
        """
        Analysiert alle Hooks aus den DB-Analytics-Events und berechnet Scores.
        Der Score basiert auf einer gewichteten Engagement-Matrix.
        """
        events = self.analytics.load_events()
        pattern_scores = defaultdict(float)

        log_doctor(f"HookAnalyzer: Analysiere {len(events)} Events aus der Datenbank...")

        for ev in events:
            meta = ev.get("meta", {})
            hook = meta.get("hook")
            if not hook:
                continue

            metrics = ev.get("metrics", {})
            
            # Gewichtete Engagement-Formel für maximale Aussagekraft (Interaktion schlägt Views)
            try:
                score = (
                    float(metrics.get("likes", 0)) * 1.5 +
                    float(metrics.get("comments", 0)) * 3.0 +
                    float(metrics.get("shares", 0)) * 4.0 +
                    float(metrics.get("views", 0)) * 0.1
                )
                pattern_scores[hook] += score
            except (ValueError, TypeError) as e:
                log_doctor(f"HookAnalyzer-Warnung: Metriken für Hook '{hook}' fehlerhaft formatiert: {e}")
                continue

        return dict(pattern_scores)

    def get_top_hooks(self, n: int = 5) -> List[str]:
        """Gibt die Top 'n' erfolgreichsten Hooks sortiert nach ihrem Gesamt-Score zurück."""
        patterns = self.extract_hook_patterns()
        
        # Sortierung: Höchster Score zuerst
        ranked = sorted(patterns.items(), key=lambda x: x[1], reverse=True)
        
        top_hooks = [hook for hook, score in ranked[:n]]
        log_doctor(f"HookAnalyzer: Top-{n} Hooks erfolgreich ermittelt. Spitzenreiter: {top_hooks[:1]}")
        return top_hooks