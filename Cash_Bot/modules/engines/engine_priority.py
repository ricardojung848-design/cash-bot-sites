import time
from typing import Any, List, Dict
from doctor_core.logging import log_doctor


class PriorityEngine:
    """
    MEGA-PRO-Version:
    - Priorisiert System-Operationen autonom anhand des aktuellen Risiko-Zustands
    - Liest Echtzeit-Metriken direkt aus dem zentralen SQLite-Langzeitgedächtnis
    - Sortiert Aufgaben aufsteigend nach ihrer Prioritätsstufe (1 = Kritisch)
    - Vollständig thread-sicher über die Engine-Manager-Infrastruktur orchestriert
    """

    def __init__(self, engine_manager: Any = None):
        self.engines = engine_manager

    def build_priority_list(self) -> List[Dict[str, Any]]:
        """Analysiert den prädiktiven Risiko-Score und leitet dringende Aufgaben ab."""
        tasks = []

        if not self.engines or not self.engines.has("state"):
            log_doctor("PriorityEngine: State-Manager nicht erreichbar. Generiere Standard-Task.")
            return [{"name": "Standard-Routine", "reason": "System läuft isoliert.", "priority": 4}]

        try:
            state = self.engines.get("state")
            
            # 1. Prädiktiven Risiko-Score direkt aus dem DB-State laden
            predictive_data = state.get_state("predictive", {"last_score": 0.0})
            risk = float(predictive_data.get("last_score", 0.0))

            # 2. Offene Fehler zur Quantifizierung heranziehen
            unfixed_errors = state.get_unfixed_errors()
            error_count = len(unfixed_errors)

            # --- Dynamische Priorisierungslogik ---
            
            # Prio 1: Hohes Risiko oder offene Code-Fehler verlangen sofortiges Self-Healing
            if risk >= 4.0 or error_count > 0:
                tasks.append({
                    "name": "Systemprüfung & Self-Healing",
                    "reason": f"Erhöhtes Risiko ({risk:.1f}/10.0) oder offene Patches ({error_count}) erkannt.",
                    "priority": 1,
                })

            # Prio 2: Auslastung der Roadmap analysieren
            planner_data = state.get_state("planner", {"roadmap": []})
            roadmap_len = len(planner_data.get("roadmap", []))
            if roadmap_len > 15:
                tasks.append({
                    "name": "Loganalyse & Optimierung",
                    "reason": f"Hohe kognitive Dichte auf der Roadmap ({roadmap_len} Einträge).",
                    "priority": 2,
                })

            # Prio 3: Routineüberwachung bei mäßiger Aktivität
            if roadmap_len > 5:
                tasks.append({
                    "name": "Review der System-Protokolle",
                    "reason": "Regelmäßige Analyse der laufenden Worker-Aktivitäten.",
                    "priority": 3,
                })

            # Fallback: Wenn alles absolut stabil und leer ist
            if not tasks:
                tasks.append({
                    "name": "Regelmäßige Wartung",
                    "reason": "Keine akuten Probleme. System befindet sich im optimalen Idle-Status.",
                    "priority": 4,
                })

            # Nach Priorität aufsteigend sortieren (1 kommt zuerst)
            tasks.sort(key=lambda t: t["priority"])

        except Exception as e:
            log_doctor(f"PriorityEngine: Fehler beim Berechnen der Prioritäten-Liste: {e}")
            # Ausfallsicherer Standard-Task
            tasks = [{"name": "Sicherheits-Routine", "reason": "Berechnungsfehler im Core.", "priority": 1}]

        return tasks

    def update(self) -> List[Dict[str, Any]]:
        """Führt den Priorisierungslauf aus und schreibt das Ergebnis in die Datenbank."""
        log_doctor("PriorityEngine: Starte autonome Aufgaben-Priorisierung.")
        tasks = self.build_priority_list()

        data = {
            "last_update": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tasks": tasks,
        }

        if self.engines and self.engines.has("state"):
            try:
                state = self.engines.get("state")
                state.set_state("priority", data)
                log_doctor(f"PriorityEngine: {len(tasks)} Aufgaben priorisiert und im Langzeitgedächtnis abgelegt.")
            except Exception as e:
                log_doctor(f"PriorityEngine: Fehler beim Schreiben in den SQLite-State: {e}")
        else:
            log_doctor(f"PriorityEngine: State-Manager fehlt. Prioritätenliste temporär im RAM.")

        return tasks