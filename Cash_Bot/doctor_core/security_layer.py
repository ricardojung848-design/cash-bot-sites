import ast
from pathlib import Path
from doctor_core.logging import log_doctor

# Basis-Pfad des Projekts absichern
BASE_DIR = Path(__file__).resolve().parent.parent


class SecurityLayer:
    """
    Phase 10 Security-Layer:
    Bietet ein Permission-System für kritische Operationen und eine 
    AST-basierte Sandbox-Überprüfung für dynamisch generierten Code.
    """

    def __init__(self):
        # Standard-Berechtigungen (True = Erlaubt, False = Gesperrt/Safe-Mode)
        self._permissions = {
            "file_write_core": False,      # Core-Dateien überschreiben
            "file_delete": False,          # Dateien löschen
            "execute_unsafe_code": False,  # Ungeprüften Code ausführen
            "network_egress": True,        # Internetverbindung für API/Recherche
        }

    def set_permission(self, permission_key: str, allowed: bool) -> None:
        """Erlaubt es der GUI oder dem Admin, Berechtigungen im laufenden Betrieb zu ändern."""
        if permission_key in self._permissions:
            self._permissions[permission_key] = allowed
            status = "FREIGEGEBEN" if allowed else "GESPERRT (Safe-Mode)"
            log_doctor(f"Security-Layer: Berechtigung '{permission_key}' wurde auf {status} gesetzt.")

    def request_permission(self, permission_key: str) -> bool:
        """Prüft, ob eine Operation aktuell erlaubt ist."""
        return self._permissions.get(permission_key, False)

    def verify_code_safety(self, file_path: Path) -> bool:
        """
        Analysiert den Quellcode einer Datei vor der Ausführung/dem Import mittels AST (Abstract Syntax Tree).
        Sucht nach potenziell bösartigen oder gefährlichen Systembefehlen.
        """
        try:
            if not file_path.exists():
                log_doctor(f"Security-Layer 🛑: Datei {file_path.name} existiert nicht für Sicherheits-Check.")
                return False

            code = file_path.read_text(encoding="utf-8")
            tree = ast.parse(code)

            # Liste verbotener Ausdrücke und Module
            forbidden_modules = {"subprocess", "shutil", "ctypes", "socket"}
            forbidden_functions = {"eval", "exec", "system", "popen", "rmdir", "remove", "unlink"}

            for node in ast.walk(tree):
                # 1. Imports prüfen
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in forbidden_modules:
                            log_doctor(f"Security-Layer 🚨: Import von riskantem Modul '{alias.name}' in {file_path.name} blockiert.")
                            return False
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module in forbidden_modules:
                        log_doctor(f"Security-Layer 🚨: From-Import aus riskantem Modul '{node.module}' in {file_path.name} blockiert.")
                        return False

                # 2. Funktionsaufrufe prüfen
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in forbidden_functions:
                            log_doctor(f"Security-Layer 🚨: Aufruf von gefährlicher Funktion '{node.func.id}' in {file_path.name} abgefangen.")
                            return False
                    
                    elif isinstance(node.func, ast.Attribute):
                        if node.func.attr in forbidden_functions:
                            log_doctor(f"Security-Layer 🚨: Attribut-Aufruf von gefährlicher Funktion '{node.func.attr}' in {file_path.name} abgefangen.")
                            return False

            log_doctor(f"Security-Layer ✅: {file_path.name} erfolgreich scanniert. Keine kritischen Anomalien gefunden (Sandbox-Pass).")
            return True

        except SyntaxError as se:
            log_doctor(f"Security-Layer ❌: Syntaxfehler bei der Analyse von {file_path.name}: {se}. Code blockiert.")
            return False
        except Exception as e:
            log_doctor(f"Security-Layer ❌: Unerwarteter Fehler bei Sandbox-Prüfung von {file_path.name}: {e}")
            return False