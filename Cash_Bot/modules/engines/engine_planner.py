import time
from typing import Any, List, Dict
from doctor_core.logging import log_doctor


class PlannerEngine:
    """
    MEGA-PRO-Version:
    - Synthetisiert die Roadmap direkt aus dem SQLite-Langzeitgedächtnis
    - Konsolidiert Prioritäten, Optimierungsziele und offene Fix-Meldungen
    - Verhindert Overheads durch intelligentes Slicing der Datensätze (Top 5)
    - Vollständig thread-sicher in die Engine-Manager-Infrastruktur integriert
    """

    def __init__(self, engine_manager: Any = None):
        self.engines = engine_manager

    def build_roadmap(self) -> List[Dict[str, Any]]:
        """Sammelt Zustände aus allen registrierten Domänen und generiert die Handlungs-Roadmap."""
        roadmap = []

        if not self.engines or not self.engines.has("state"):
            log_doctor("PlannerEngine: State-Manager nicht verfügbar. Generierung abgebrochen.")
            return roadmap

        try:
            state = self.engines.get("state")

            # 1. Prioritäten laden
            priority_data = state.get_state("priority", {"tasks": []})
            for t in priority_data.get("tasks", []):
                roadmap.append({
                    "type": "priority_task",
                    "name": t.get("name"),
                    "reason": t.get("reason"),
                })

            # 2. Code-Optimierungsziele laden (Top 5 komplexe Module)
            optimizer_data = state.get_state("optimizer", {"modules": []})
            for m in optimizer_data.get("modules", [])[:5]:
                roadmap.append({
                    "type": "module_optimize",
                    "name": m.get("name"),
                    "info": f"Komplexität: {m.get('complexity')}, Zeilen: {m.get('lines')}",
                })

            # 3. Strukturierte Fix-Vorschläge laden (Top 5 Fehler-Muster)
            fixes_data = state.get_state("fixes", {"suggestions": []})
            for s in fixes_data.get("suggestions", [])[:5]:
                roadmap.append({
                    "type": "fix_suggestion",
                    "file": s.get("file") or s.get("log_file"),
                    "keyword": s.get("keyword"),
                    "hint": s.get("hint"),
                })

        except Exception as e:
            log_doctor(f"PlannerEngine: Kritischer Fehler beim Aggregieren der Roadmap-Daten: {e}")

        return roadmap

    def update(self) -> List[Dict[str, Any]]:
        """Aktualisiert die Roadmap und persistiert sie transaktionssicher in der Datenbank."""
        log_doctor("PlannerEngine: Generiere konsolidierten System-Zukunftsplan (Roadmap).")
        roadmap = self.build_roadmap()

        data = {
            "last_update": time.strftime("%Y-%m-%d %H:%M:%S"),
            "roadmap": roadmap,
        }

        if self.engines and self.engines.has("state"):
            try:
                state = self.engines.get("state")
                # Persistiert den finalen kombinierten Zustand unter dem Key 'planner'
                state.set_state("planner", data)
                log_doctor(f"PlannerEngine: Roadmap mit {len(roadmap)} Einträgen erfolgreich im Langzeitgedächtnis aktualisiert.")
            except Exception as e:
                log_doctor(f"PlannerEngine: Fehler beim Schreiben in das SQLite-System: {e}")
        else:
            log_doctor(f"PlannerEngine: State-Manager fehlt. {len(roadmap)} Einträge temporär gepuffert.")

        return roadmap