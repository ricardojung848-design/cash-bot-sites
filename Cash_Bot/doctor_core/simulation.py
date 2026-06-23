from .logging import log_doctor
from .state import DoctorState


class Phase6Simulation:
    def __init__(self, engines, state: DoctorState):
        self.engines = engines
        self.state = state

    def run(self):
        log_doctor("Phase‑6‑Simulation gestartet.")
        data = self.state.load_all()

        priority = data.get("priority", {})
        fixes = data.get("fixes", {})
        optimizer = data.get("optimizer", {})
        planner = data.get("planner", {})

        log_doctor("---- Priorisierte Aufgaben ----")
        for t in priority.get("tasks", []):
            log_doctor(f"Würde priorisieren: {t.get('name')} (Grund: {t.get('reason')})")

        log_doctor("---- Fix‑Vorschläge ----")
        for s in fixes.get("suggestions", []):
            log_doctor(f"Würde fixen: {s.get('file')} (Keyword: {s.get('keyword')}, Hinweis: {s.get('hint')})")

        log_doctor("---- Optimierungs‑Kandidaten ----")
        for m in optimizer.get("modules", []):
            log_doctor(f"Würde optimieren: {m.get('name')} (Komplexität: {m.get('complexity')}, Zeilen: {m.get('lines')})")

        log_doctor("---- Roadmap‑Schritte ----")
        for r in planner.get("roadmap", []):
            log_doctor(f"Roadmap‑Eintrag: {r}")

        log_doctor("Phase‑6‑Simulation abgeschlossen.")
