from pathlib import Path
from typing import Any
from doctor_core.logging import log_doctor


class ModuleExtender:
    """
    MEGA-PRO-Version:
    - Erweitert bestehende Module dynamisch zur Laufzeit
    - Sichert die Ziel-Datei ab, indem Code vorab in der Sandbox validiert wird
    - Nutzt das Backup- und Rollback-System der AutoFixEngine bei Schreibfehlern
    - Vollständig integriert in die Engine-Manager-Architektur
    """

    def __init__(self, engine_manager: Any = None):
        self.engines = engine_manager
        self.base_dir = Path(__file__).resolve().parent.parent
        self.modules_dir = self.base_dir / "modules"

    def append_to_module(self, name: str, code: str) -> bool:
        """
        Hängt Code sicher an ein bestehendes Modul im 'modules'-Ordner an.
        Validiert die Integrität vorab über die Sandbox.
        """
        log_doctor(f"ModuleExtender: Anfrage zur Erweiterung von Modul '{name}' erhalten.")
        
        target_file = self.modules_dir / f"{name}.py"
        if not target_file.exists():
            log_doctor(f"ModuleExtender: Ziel-Modul existiert nicht: {target_file}")
            return False

        # 1. VORAB-VALIDIERUNG IN DER SANDBOX (Syntax- und Crash-Check)
        if self.engines and self.engines.has("checker"):
            try:
                current_content = target_file.read_text(encoding="utf-8")
                simulated_combined_code = f"{current_content}\n\n{code}\n"
                
                checker = self.engines.get("checker")
                success, sandbox_msg = checker.execute_in_sandbox(simulated_combined_code, timeout_seconds=5)
                
                if not success:
                    log_doctor(f"ModuleExtender: Erweiterung abgelehnt! Sandbox-Fehler: {sandbox_msg}")
                    return False
            except Exception as e:
                log_doctor(f"ModuleExtender: Sandbox-Vorauswertung fehlgeschlagen: {e}")
                return False

        # 2. CODE SICHER SCHREIBEN (Mit Backup-Infrastruktur)
        try:
            # Falls die AutoFixEngine registriert ist, nutzen wir deren Backup-Funktion
            if self.engines and self.engines.has("fix"):
                fix_engine = self.engines.get("fix")
                current_content = target_file.read_text(encoding="utf-8")
                new_combined_content = f"{current_content}\n\n{code}\n"
                
                success, msg = fix_engine.apply_fix_with_backup(target_file, new_combined_content, create_backup_before=True)
                if success:
                    log_doctor(f"ModuleExtender: Modul '{name}' erfolgreich und sicher erweitert.")
                    return True
                else:
                    return False
            else:
                # Standalone-Fallback, falls die Fix-Engine noch nicht im Manager eingepflegt ist
                with open(target_file, "a", encoding="utf-8") as f:
                    f.write(f"\n\n{code}\n")
                log_doctor(f"ModuleExtender: Modul '{name}' erweitert (Achtung: Ohne Backup-Schutz angewendet).")
                return True

        except Exception as e:
            log_doctor(f"ModuleExtender: Fehler beim Schreiben der Modul-Erweiterung für '{name}': {e}")
            return False