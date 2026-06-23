from pathlib import Path
import importlib.util
from .logging import log_doctor

BASE_DIR = Path(__file__).resolve().parent.parent
MODULES_DIR = BASE_DIR / "modules"
ENGINES_DIR = MODULES_DIR / "engines"


class EngineManager:
    def __init__(self):
        self.predictive = None
        self.priority = None
        self.fix = None
        self.optimizer = None
        self.learning = None
        self.planner = None
        self._load_all()

    def _load_module(self, name: str):
        path = ENGINES_DIR / f"{name}.py"
        if not path.exists():
            log_doctor(f"Engine fehlt: {path}")
            return None
        spec = importlib.util.spec_from_file_location(name, str(path))
        if not spec or not spec.loader:
            log_doctor(f"Spec für Engine {name} fehlgeschlagen.")
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _load_all(self):
        m_pred = self._load_module("engine_predictive")
        if m_pred and hasattr(m_pred, "PredictiveEngine"):
            self.predictive = m_pred.PredictiveEngine()
            log_doctor("PredictiveEngine geladen.")

        m_prio = self._load_module("engine_priority")
        if m_prio and hasattr(m_prio, "PriorityEngine"):
            self.priority = m_prio.PriorityEngine()
            log_doctor("PriorityEngine geladen.")

        m_fix = self._load_module("engine_fix_suggestions")
        if m_fix and hasattr(m_fix, "FixSuggestionEngine"):
            self.fix = m_fix.FixSuggestionEngine()
            log_doctor("FixSuggestionEngine geladen.")

        m_opt = self._load_module("engine_optimizer")
        if m_opt and hasattr(m_opt, "OptimizerEngine"):
            self.optimizer = m_opt.OptimizerEngine()
            log_doctor("OptimizerEngine geladen.")

        m_learn = self._load_module("engine_learning")
        if m_learn and hasattr(m_learn, "LearningEngine"):
            self.learning = m_learn.LearningEngine()
            log_doctor("LearningEngine geladen.")

        m_plan = self._load_module("engine_planner")
        if m_plan and hasattr(m_plan, "PlannerEngine"):
            self.planner = m_plan.PlannerEngine()
            log_doctor("PlannerEngine geladen.")
