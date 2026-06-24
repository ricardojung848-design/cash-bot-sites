from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from doctor_core.logging import log_doctor


@dataclass
class EngineManager:
    """
    PRO-Version:
    - zentraler Container für alle Engines
    - dynamische Registrierung
    - Zugriff per Attribut (self.engines.fix, self.engines.worker, ...)
    - Fallback-Logging, wenn Engine fehlt
    """

    _engines: Dict[str, Any] = field(default_factory=dict)

    def register(self, name: str, engine: Any) -> None:
        """
        Engine unter einem Namen registrieren.
        Beispiel:
            engines.register("fix", FixSuggestionEngine(...))
        """
        if not name:
            raise ValueError("Engine-Name darf nicht leer sein.")
        self._engines[name] = engine
        setattr(self, name, engine)
        log_doctor(f"EngineManager: Engine '{name}' registriert: {engine.__class__.__name__}")

    def get(self, name: str) -> Optional[Any]:
        """
        Engine per Namen abrufen.
        """
        return self._engines.get(name)

    def has(self, name: str) -> bool:
        """
        Prüfen, ob eine Engine registriert ist.
        """
        return name in self._engines

    def ensure(self, name: str) -> Any:
        """
        Engine holen oder Fehler loggen, wenn sie fehlt.
        """
        engine = self.get(name)
        if engine is None:
            log_doctor(f"EngineManager: Engine '{name}' ist nicht registriert.")
        return engine

    def list_engines(self) -> Dict[str, str]:
        """
        Übersicht aller registrierten Engines (Name -> Klassennamen).
        """
        return {name: engine.__class__.__name__ for name, engine in self._engines.items()}
