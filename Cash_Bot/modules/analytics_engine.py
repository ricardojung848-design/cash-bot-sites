from datetime import datetime
from typing import Any, Dict, List
from doctor_core.logging import log_doctor
from doctor_core.engine_manager import EngineManager


class AnalyticsEngine:
    """
    PRO-Version der AnalyticsEngine:
    - Trackt Performance-Metriken (Views, Likes, Comments) von Social-Media-Content
    - Eliminiert die fehleranfällige 'analytics_events.json' vollständig
    - Schreibt Events transaktionssicher direkt in den relationalen SQLite-Zustand
    """

    def __init__(self, engine_manager: EngineManager):
        self.engines = engine_manager
        if not self.engines.has("state"):
            raise RuntimeError("AnalyticsEngine benötigt einen registrierten State-Manager im EngineManager!")
        self.state = self.engines.get("state")

    def log_event(
        self,
        content_id: str,
        platform: str,
        metrics: Dict[str, Any],
        meta: Dict[str, Any] | None = None,
    ) -> None:
        """
        Registriert ein neues Content-Event direkt in der zentralen DB.
        
        content_id: z.B. 'evergreen_12', 'reel_automation_basics'
        platform: 'instagram', 'tiktok', 'blog'
        metrics: {"views": 1200, "likes": 130}
        meta: Optional, {"hook": "Die Wahrheit über AI", "cta": "Kommentiere INFOS"}
        """
        try:
            # Bestehende Events aus der DB laden
            analytics_data = self.state.get_state("analytics", {"events": []})
            events = analytics_data.get("events", [])
            
            if not isinstance(events, list):
                events = []

            # Neues Event-Objekt erstellen
            event = {
                "content_id": content_id,
                "platform": platform,
                "metrics": metrics,
                "meta": meta or {},
                "timestamp": datetime.now().isoformat(),
            }
            
            events.append(event)
            analytics_data["events"] = events
            
            # Zustand transaktionssicher speichern
            self.state.set_state("analytics", analytics_data)
            log_doctor(f"Analytics: Event registriert für {content_id} [{platform}] -> {metrics}")
            
        except Exception as e:
            log_doctor(f"Analytics-Fehler: Konnte Event für {content_id} nicht schreiben: {e}")

    def load_events(self) -> List[Dict[str, Any]]:
        """Gibt die vollständige Zeitreihe aller aufgezeichneten Events zurück."""
        analytics_data = self.state.get_state("analytics", {"events": []})
        return analytics_data.get("events", [])

    def get_top_performing_content(self, platform: str, metric_key: str = "views", limit: int = 5) -> List[Dict[str, Any]]:
        """
        PRO-Zusatzfunktion: Filtert autonom den bestperformenden Content heraus,
        damit deine anderen Engines (z.B. Optimizer) lernen, welcher Hook zieht.
        """
        events = self.load_events()
        filtered = [e for e in events if e.get("platform") == platform]
        
        # Sortieren nach dem gewünschten Metrik-Schlüssel (z.B. 'views' oder 'likes')
        try:
            filtered.sort(
                key=lambda e: int(e.get("metrics", {}).get(metric_key, 0)), 
                reverse=True
            )
        except Exception:
            pass
            
        return filtered[:limit]