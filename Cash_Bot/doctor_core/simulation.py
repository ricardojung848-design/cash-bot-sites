from doctor_core.logging import log_doctor
from doctor_core.state import DoctorState
from typing import Any


class Phase6Simulation:
    """
    MEGA-PRO-Version:
    - Simuliert und validiert den aktuellen Systemzustand
    - Nutzt die abwärtskompatible Schnittstelle des neuen SQLite-State-Managers
    - Zieht zusätzlich echte Live-Fehler und Optimierungshistorien für maximale Transparenz
    """

    def __init__(self, engine_manager: Any, state: DoctorState):
        self.engines = engine_manager
        self.state = state

    def run(self) -> None:
        log_doctor("Phase-6-Simulation gestartet.")
        
        # Lädt die standardisierten Core-Pläne (Priority, Fixes, Optimizer, Planner)
        data = self.state.load_all()

        priority = data.get("priority", {})
        fixes = data.get("fixes", {})
        optimizer = data.get("optimizer", {})
        planner = data.get("planner", {})

        # 1. Priorisierte Aufgaben ausgeben
        log_doctor("---- Priorisierte Aufgaben ----")
        tasks = priority.get("tasks", [])
        if not tasks:
            log_doctor("Keine statischen Aufgaben im Prioritätenplan hinterlegt.")
        for t in tasks:
            log_doctor(f"Würde priorisieren: {t.get('name')} (Grund: {t.get('reason')})")

        # 2. Fix-Vorschläge ausgeben
        log_doctor("---- Fix-Vorschläge ----")
        suggestions = fixes.get("suggestions", [])
        if not suggestions:
            log_doctor("Keine manuellen Fix-Vorschläge definiert.")
        for s in suggestions:
            log_doctor(f"Würde fixen: {s.get('file')} (Keyword: {s.get('keyword')}, Hinweis: {s.get('hint')})")

        # 3. ECHTE UNBEHOBENE LIVE-FEHLER (Das Upgrade aus der SQLite-DB!)
        log_doctor("---- Echte ungelöste Systemfehler (SQLite Live-Data) ----")
        try:
            unfixed_errors = self.state.get_unfixed_errors()
            if not unfixed_errors:
                log_doctor("Absolut sauber! Keine ungelösten Systemfehler in der Datenbank.")
            for err in unfixed_errors:
                log_doctor(f"⚠️ LIVE-ERROR in [{err['module_name']}]: {err['error_message']} (Zeit: {err['timestamp']})")
        except Exception as e:
            log_doctor(f"Simulation Fehler beim Abruf der Live-Fehler: {e}")

        # 4. Optimierungs-Kandidaten ausgeben
        log_doctor("---- Optimierungs-Kandidaten ----")
        modules = optimizer.get("modules", [])
        if not modules:
            log_doctor("Keine manuellen Module zur Optimierung markiert.")
        for m in modules:
            log_doctor(f"Würde optimieren: {m.get('name')} (Komplexität: {m.get('complexity')}, Zeilen: {m.get('lines')})")

        # 5. Roadmap-Schritte ausgeben
        log_doctor("---- Roadmap-Schritte ----")
        roadmap = planner.get("roadmap", [])
        if not roadmap:
            log_doctor("Die Roadmap ist aktuell leer.")
        for r in roadmap:
            log_doctor(f"Roadmap-Eintrag: {r}")

        log_doctor("Phase-6-Simulation abgeschlossen.")