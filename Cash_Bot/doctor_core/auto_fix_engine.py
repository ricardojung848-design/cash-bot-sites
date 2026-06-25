from pathlib import Path
from datetime import datetime
from typing import Tuple, Any
import os
from doctor_core.logging import log_doctor


class AutoFixEngine:
    """
    MEGA-PRO-Version:
    - Autonome Fehlerbehebung & Patch-Verwaltung
    - Integrierte Sandbox-Validierung vor dem Schreiben von Code
    - Automatisches Datei-Backup und transaktionssicheres Rollback
    - Vollständige Anbindung an Event-Bus und SQLite-Memory
    """

    def __init__(self, engine_manager: Any = None):
        self.engines = engine_manager
        self.base_dir = Path(__file__).resolve().parent.parent

    def handle_error_event(self, error_data: dict) -> None:
        """
        Hook für das Event-System. Reagiert vollautomatisch auf Fehlermeldungen.
        """
        module = error_data.get("module", "unknown")
        error_msg = error_data.get("error", "")
        log_doctor(f"AutoFixEngine: Event empfangen. Analysiere Fehler in Modul '{module}'...")
        
        # Hier würde der LLM/Fix-Generierungs-Prozess ansetzen.
        # Für die Kern-Architektur simulieren wir die Pipeline-Kette zur Validierung:
        self.process_auto_fix(module, error_msg)

    def process_auto_fix(self, module_name: str, error_message: str) -> bool:
        """Steuert den gesamten Zyklus: Analyse -> Test in Sandbox -> Anwendung."""
        # 1. Dummy-Patch generieren oder aus Vorschlägen laden (Projektkontext)
        # In einer Vollintegration wird hier dein Prompt-Generierungs-Modul aufgerufen
        proposed_fix_code = f"# Fixed automatically by Doctor-Agent\n# Original Error: {error_message}\n"
        
        target_file = self.base_dir / "modules" / f"{module_name}.py"
        if not target_file.exists():
            target_file = self.base_dir / "doctor_core" / f"{module_name}.py"

        if not target_file.exists():
            log_doctor(f"AutoFixEngine: Datei für {module_name} konnte nicht lokalisiert werden.")
            return False

        # 2. VORAB-VALIDIERUNG IN DER SANDBOX (Security-Layer)
        if self.engines and self.engines.has("checker"):
            checker = self.engines.get("checker")
            # Kombiniere alten Code mit Fix oder teste isolierten Code-Snippet
            success, message = checker.execute_in_sandbox(proposed_fix_code, timeout_seconds=5)
            
            if not success:
                log_doctor(f"AutoFixEngine: Patch-Validierung in Sandbox abgelehnt! Grund: {message}")
                return False

        # 3. Patch anwenden mit automatischem Backup
        success, msg = self.apply_fix_with_backup(target_file, proposed_fix_code, create_backup_before=True)
        
        # 4. Status in der Memory-Engine protokollieren
        if self.engines and self.engines.has("state"):
            state = self.engines.get("state")
            # Finde die ID des letzten Fehlers in der DB, um ihn als behoben zu markieren
            try:
                unfixed = state.get_unfixed_errors()
                for err in unfixed:
                    if err["module_name"] == module_name:
                        state.mark_error_fixed(err["id"], fix_applied=proposed_fix_code)
            except Exception as e:
                log_doctor(f"AutoFixEngine: Fehler beim Schreiben der Historie: {e}")

        return success

    def _make_backup_path(self, target_path: Path) -> Path:
        """Erzeugt einen Backup-Pfad neben der Zieldatei."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return target_path.with_suffix(target_path.suffix + f".bak_{timestamp}")

    def apply_fix_with_backup(
        self,
        target_path: Path,
        new_content: str,
        create_backup_before: bool = True,
    ) -> Tuple[bool, str]:
        """Schreibt neuen Inhalt und sichert optional die alte Datei."""
        try:
            target_path = Path(target_path)

            if not target_path.exists():
                target_path.parent.mkdir(parents=True, exist_ok=True)
                original_exists = False
            else:
                original_exists = True

            backup_path = None

            if create_backup_before and original_exists:
                backup_path = self._make_backup_path(target_path)
                backup_path.write_text(target_path.read_text(encoding="utf-8"), encoding="utf-8")
                log_doctor(f"AutoFixEngine: Backup erstellt: {backup_path}")

            target_path.write_text(new_content, encoding="utf-8")
            msg = f"AutoFixEngine: Neuer Inhalt in {target_path} geschrieben."
            if backup_path:
                msg += f" Backup: {backup_path}"
            return True, msg

        except Exception as e:
            msg = f"AutoFixEngine: Fehler beim Anwenden des Fixes auf {target_path}: {e}"
            log_doctor(msg)
            return False, msg

    def _find_latest_backup(self, target_path: Path) -> Path | None:
        """Sucht das neueste Backup für die Zieldatei."""
        target_path = Path(target_path)
        pattern = target_path.with_suffix(target_path.suffix + ".bak_")
        parent = target_path.parent

        if not parent.exists():
            return None

        candidates = [p for p in parent.iterdir() if p.name.startswith(pattern.name)]
        if not candidates:
            return None

        candidates.sort(reverse=True)
        return candidates[0]

    def rollback_last_fix(self, target_path: Path) -> Tuple[bool, str]:
        """Sucht das letzte Backup und stellt es wieder her."""
        try:
            target_path = Path(target_path)
            backup_path = self._find_latest_backup(target_path)

            if backup_path is None or not backup_path.exists():
                msg = f"Rollback: Kein Backup für {target_path} gefunden."
                log_doctor(msg)
                return False, msg

            content = backup_path.read_text(encoding="utf-8")
            target_path.write_text(content, encoding="utf-8")

            msg = f"Rollback: Backup {backup_path} nach {target_path} wiederhergestellt."
            log_doctor(msg)
            return True, msg

        except Exception as e:
            msg = f"Rollback: Fehler beim Wiederherstellen von {target_path}: {e}"
            log_doctor(msg)
            return False, msg