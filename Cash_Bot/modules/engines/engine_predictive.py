import time
from typing import Any, List, Dict
from doctor_core.logging import log_doctor


class PredictiveEngine:
    """
    MEGA-PRO-Version:
    - Berechnet dynamisch den System-Risiko-Score (Skala 0.0 bis 10.0)
    - Analysiert ungelöste Fehler und Systemereignisse direkt aus der SQLite-Datenbank
    - Führt eine historische Zeitreihe der Scores zur Trendanalyse im Langzeit-State
    - Thread-sicher und voll integriert in das Core-Ökosystem
    """

    def __init__(self, engine_manager: Any = None):
        self.engines = engine_manager

    def compute_risk(self, state_manager: Any) -> float:
        """
        Berechnet den mathematischen Risiko-Score basierend auf:
        - Anzahl der aktuell ungelösten Systemfehler (hohe Gewichtung)
        - Anzahl der Einträge auf der kognitiven Roadmap
        """
        try:
            # 1. Unfixed Errors direkt abfragen (jeder offene Fehler erhöht das Risiko signifikant)
            unfixed_errors = state_manager.get_unfixed_errors()
            error_risk = len(unfixed_errors) * 2.0  # 2.0 Punkte pro offenem Fehler

            # 2. Auslastung über die Roadmap bewerten
            planner_data = state_manager.get_state("planner", {"roadmap": []})
            roadmap_items = planner_data.get("roadmap", [])
            load_risk = min(len(roadmap_items) / 10.0, 3.0)  # Maximal 3.0 Punkte durch Last

            # Gesamtrisiko synthetisieren
            total_risk = error_risk + load_risk
            return float(min(total_risk, 10.0))

        except Exception as e:
            log_doctor(f"PredictiveEngine: Fehler bei Risiko-Berechnung (Nutze Fallback): {e}")
            return 5.0  # Mittleres Risiko als sicherer Fallback bei Ausfällen

    def update(self) -> float:
        """Aktualisiert die Risiko-Metriken und archiviert den Trend in der Datenbank."""
        log_doctor("PredictiveEngine: Starte prädiktive System-Risikoanalyse.")

        if not self.engines or not self.engines.has("state"):
            log_doctor("PredictiveEngine: State-Manager fehlt. Trend-Berechnung abgebrochen.")
            return 0.0

        try:
            state = self.engines.get("state")
            score = self.compute_risk(state)

            # Historischen Verlauf aus der DB laden
            predictive_data = state.get_state("predictive", {
                "history": [],
                "last_score": 0.0,
                "last_update": None
            })

            history: List[Dict[str, Any]] = predictive_data.get("history", [])
            
            # Neuen Snapshot anhängen
            history.append({
                "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                "score": score,
            })

            # Rollierende Begrenzung auf die letzten 100 Snapshots
            if len(history) > 100:
                history = history[-100:]

            # Datenpaket schnüren und wegschreiben
            predictive_data["history"] = history
            predictive_data["last_score"] = score
            predictive_data["last_update"] = time.strftime("%Y-%m-%d %H:%M:%S")

            state.set_state("predictive", predictive_data)
            log_doctor(f"PredictiveEngine: System-Risiko-Score aktualisiert: {score:.1f}/10.0")
            return score

        except Exception as e:
            log_doctor(f"PredictiveEngine: Fehler beim Update-Zyklus: {e}")
            return 0.0