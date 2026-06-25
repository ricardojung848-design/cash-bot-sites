from pathlib import Path
import time
from typing import Any, Dict, List
from doctor_core.logging import log_doctor


class Phase5Brain:
    """
    MEGA-PRO-Version:
    - Das zentrale Gehirn und die Entscheidungsmatrix des Agenten
    - Synthetisiert Daten aus der Memory-Engine (SQLite) und den Analyzern
    - Erstellt autonome Handlungspläne und optimiert die System-Roadmap
    - Orchestriert die Zusammenarbeit zwischen AutoFix, Optimizer und MediaEngine
    """

    def __init__(self, engine_manager: Any = None):
        self.engines = engine_manager
        self.base_dir = Path(__file__).resolve().parent.parent

    def update(self) -> bool:
        """
        Zentraler Update-Zyklus des Gehirns. 
        Wird periodisch vom BackgroundMonitor aufgerufen.
        """
        log_doctor("Phase5Brain: Starte kognitiven Analyse- und Update-Zyklus.")

        if not self.engines or not self.engines.has("state"):
            log_doctor("Phase5Brain: Fehler - State-Manager (Memory-Engine) nicht erreichbar.")
            return False

        try:
            state = self.engines.get("state")
            
            # 1. Gesamten Systemzustand aus dem SQLite-Langzeitgedächtnis laden
            system_data = state.load_all()
            
            # 2. Fehlerlage bewerten
            unfixed_errors = state.get_unfixed_errors()
            if unfixed_errors:
                log_doctor(f"Phase5Brain: Kritischer Zustand! {len(unfixed_errors)} ungelöste Fehler erkannt.")
                # Weise die AutoFixEngine an, höchste Priorität auf diese Fehler zu setzen
                if self.engines.has("fix"):
                    self.engines.trigger("new_error", {
                        "module": unfixed_errors[0]["module_name"],
                        "error": unfixed_errors[0]["error_message"]
                    })

            # 3. Kognitiven Zukunftsplan (Roadmap) autonom aktualisieren
            self._recalculate_roadmap(state, system_data, len(unfixed_errors))

            log_doctor("Phase5Brain: Kognitiver Update-Zyklus erfolgreich abgeschlossen.")
            return True

        except Exception as e:
            log_doctor(f"CRITICAL Error im Phase5Brain Update-Lauf: {e}")
            return False

    def _recalculate_roadmap(self, state: Any, current_data: Dict[str, Any], error_count: int) -> None:
        """Berechnet basierend auf System-Metriken die nächsten Schritte auf der Roadmap."""
        planner = current_data.get("planner", {"roadmap": []})
        roadmap: List[str] = planner.get("roadmap", [])

        # Säubern von alten automatischen Systemmeldungen, um die DB nicht zu überladen
        roadmap = [item for item in roadmap if not item.startswith("[Autonom]")]

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        # Strategische Entscheidung des Gehirns treffen
        if error_count > 0:
            decision = f"[Autonom] {timestamp} - FOKUS: Systemstabilität wiederherstellen ({error_count} offene Patches)."
        elif self.engines.has("optimizer"):
            decision = f"[Autonom] {timestamp} - FOKUS: Performance-Tuning der Telegram- & Media-Schnittstellen."
        else:
            decision = f"[Autonom] {timestamp} - FOKUS: Idle-Modus. Warte auf Benutzerbefehle oder Log-Ereignisse."

        roadmap.append(decision)
        
        # Aktualisierten Plan zurück ins Langzeitgedächtnis schreiben
        new_planner_state = {"roadmap": roadmap}
        state.set_state("planner", new_planner_state)
        
        log_doctor(f"Phase5Brain: Strategische Entscheidung eingeloggt: {decision}")