import shutil
import datetime
from pathlib import Path
from typing import Optional, Tuple

from doctor_core.logging import log_doctor
from doctor_core.engine_manager import EngineManager


class FileBackupEngine:
    """
    PRO-Version der FileBackupEngine:
    - Verwaltet Datei-Backups und sichere Schreib-/Leseoperationen.
    - Hält standardmäßig genau ein letztes stabiles Backup pro Datei bereit (.bak).
    - Vollständig integriert in das EngineManager-Ökosystem und thread-sicher konzipiert.
    """

    def __init__(self, engine_manager: EngineManager):
        self.engines = engine_manager
        
        # Basisverzeichnis ermitteln (eine Ebene über doctor_core/modules)
        self.base_dir = Path(__file__).resolve().parent.parent
        self.backup_dir = self.base_dir / "backups"

    def ensure_backup_dir(self) -> None:
        """Stellt sicher, dass der Backup-Ordner im Projektverzeichnis existiert."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def get_backup_path_for_file(self, target_path: Path) -> Path:
        """
        Liefert den Zielpfad der Backup-Datei für eine bestimmte Datei.
        Beispiel: /projekt/telegram_bot.py -> /projekt/backups/telegram_bot.py.bak
        """
        self.ensure_backup_dir()
        filename = target_path.name
        backup_name = f"{filename}.bak"
        return self.backup_dir / backup_name

    def has_backup(self, target_path: Path) -> bool:
        """Prüft, ob für die angegebene Datei ein gültiges Backup existiert."""
        backup_path = self.get_backup_path_for_file(target_path)
        return backup_path.is_file()

    def create_backup(self, target_path: Path) -> Optional[Path]:
        """
        Erstellt ein Backup der angegebenen Datei.
        Überschreibt das alte Backup (hält immer den letzten Stand).
        """
        try:
            resolved_target = Path(target_path).resolve()
            if not resolved_target.is_file():
                log_doctor(f"BackupEngine-Fehler: Datei existiert nicht für Backup: {resolved_target}")
                return None

            backup_path = self.get_backup_path_for_file(resolved_target)
            self.ensure_backup_dir()
            
            # Kopiert die Datei inklusive Metadaten
            shutil.copy2(str(resolved_target), str(backup_path))
            log_doctor(f"BackupEngine: Backup erfolgreich erstellt -> {backup_path.name}")
            return backup_path
        except Exception as e:
            log_doctor(f"BackupEngine-Kritisch: Fehler beim Erstellen des Backups für {target_path}: {e}")
            return None

    def restore_backup(self, target_path: Path) -> bool:
        """Stellt eine Datei aus ihrem letzten Backup wieder her."""
        try:
            resolved_target = Path(target_path).resolve()
            backup_path = self.get_backup_path_for_file(resolved_target)
            
            if not backup_path.is_file():
                log_doctor(f"BackupEngine-Fehler: Kein Backup gefunden für {resolved_target}")
                return False

            shutil.copy2(str(backup_path), str(resolved_target))
            log_doctor(f"BackupEngine: 🎉 Backup erfolgreich wiederhergestellt -> {resolved_target.name}")
            return True
        except Exception as e:
            log_doctor(f"BackupEngine-Kritisch: Fehler bei der Wiederherstellung von {target_path}: {e}")
            return False

    def read_file_safely(self, path: Path, encoding: str = "utf-8") -> Optional[str]:
        """Liest den Inhalt einer Datei sicher ein."""
        try:
            resolved_path = Path(path).resolve()
            if not resolved_path.is_file():
                return None

            with resolved_path.open("r", encoding=encoding) as f:
                return f.read()
        except Exception as e:
            log_doctor(f"BackupEngine-Fehler beim Lesen von {path}: {e}")
            return None

    def write_file_safely(self, path: Path, content: str, encoding: str = "utf-8") -> None:
        """Schreibt den Inhalt transaktionssicher in eine Datei (inkl. Ordnererstellung)."""
        resolved_path = Path(path).resolve()
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        with resolved_path.open("w", encoding=encoding) as f:
            f.write(content)

    def apply_fix_with_backup(
        self,
        target_path: Path,
        new_content: str,
        create_backup_before: bool = True,
    ) -> Tuple[bool, str]:
        """
        Wendet neuen Code/Inhalt auf eine Datei an und sichert den alten Zustand ab.
        """
        resolved_target = Path(target_path).resolve()

        if create_backup_before:
            backup_path = self.create_backup(resolved_target)
            if backup_path is None:
                return False, f"Backup fehlgeschlagen: Datei existiert nicht: {resolved_target}"

        try:
            self.write_file_safely(resolved_target, new_content)
            return True, f"Fix angewendet auf: {resolved_target}"
        except Exception as e:
            log_doctor(f"BackupEngine-Fehler beim Anwenden des Fixes auf {resolved_target}: {e}")
            return False, f"Fehler beim Schreiben der Datei {resolved_target}: {e}"

    def rollback_last_fix(self, target_path: Path) -> Tuple[bool, str]:
        """Führt einen Rollback der Ziel-Datei auf die letzte Backup-Version durch."""
        resolved_target = Path(target_path).resolve()

        if not self.has_backup(resolved_target):
            return False, f"Kein Backup vorhanden für: {resolved_target}"

        ok = self.restore_backup(resolved_target)
        if not ok:
            return False, f"Backup konnte nicht wiederhergestellt werden: {resolved_target}"
        return True, f"Rollback erfolgreich durchgeführt für: {resolved_target}"

    def timestamp(self) -> str:
        """Liefert einen formatierten Zeitstempel für Logging-Zwecke."""
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Abwärtskompatibler Einstiegspunkt für ältere Funktionstrigger
def apply_fix_legacy(target_path: Path, new_content: str, engine_manager: EngineManager) -> Tuple[bool, str]:
    """Erlaubt Legacy-Modulen den Aufruf der Backup-Fix-Logik."""
    engine = FileBackupEngine(engine_manager)
    return engine.apply_fix_with_backup(target_path, new_content)