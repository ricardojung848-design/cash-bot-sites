from pathlib import Path
import shutil
import datetime
from typing import Optional, Tuple


# Basisverzeichnis: eine Ebene über doctor_core
BASE_DIR = Path(__file__).resolve().parent.parent
BACKUP_DIR = BASE_DIR / "backups"


def ensure_backup_dir() -> None:
    """
    Stellt sicher, dass der Backup-Ordner existiert.
    """
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def get_backup_path_for_file(target_path: Path) -> Path:
    """
    Liefert den Pfad zur Backup-Datei für eine bestimmte Zieldatei.
    Es gibt immer nur EIN letztes Backup pro Datei (Option 3).
    Beispiel:
        target:  /projekt/telegram_bot.py
        backup:  /projekt/backups/telegram_bot.py.bak
    """
    ensure_backup_dir()
    filename = target_path.name
    backup_name = f"{filename}.bak"
    return BACKUP_DIR / backup_name


def has_backup(target_path: Path) -> bool:
    """
    Prüft, ob es für die angegebene Datei ein Backup gibt.
    """
    backup_path = get_backup_path_for_file(target_path)
    return backup_path.is_file()


def create_backup(target_path: Path) -> Optional[Path]:
    """
    Erstellt ein Backup der angegebenen Datei.
    Überschreibt das alte Backup (Option 3: nur letztes Backup).
    Gibt den Pfad zur Backup-Datei zurück oder None, wenn die Datei nicht existiert.
    """
    target_path = target_path.resolve()
    if not target_path.is_file():
        return None

    backup_path = get_backup_path_for_file(target_path)
    ensure_backup_dir()
    shutil.copy2(str(target_path), str(backup_path))
    return backup_path


def restore_backup(target_path: Path) -> bool:
    """
    Stellt die Datei aus dem letzten Backup wieder her.
    Gibt True zurück, wenn erfolgreich, sonst False.
    """
    target_path = target_path.resolve()
    backup_path = get_backup_path_for_file(target_path)
    if not backup_path.is_file():
        return False

    shutil.copy2(str(backup_path), str(target_path))
    return True


def read_file_safely(path: Path, encoding: str = "utf-8") -> Optional[str]:
    """
    Liest den Inhalt einer Datei sicher ein.
    Gibt den Inhalt als String zurück oder None, wenn die Datei nicht existiert.
    """
    path = path.resolve()
    if not path.is_file():
        return None

    with path.open("r", encoding=encoding) as f:
        return f.read()


def write_file_safely(path: Path, content: str, encoding: str = "utf-8") -> None:
    """
    Schreibt den Inhalt sicher in eine Datei.
    """
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding=encoding) as f:
        f.write(content)


def apply_fix_with_backup(
    target_path: Path,
    new_content: str,
    create_backup_before: bool = True,
) -> Tuple[bool, str]:
    """
    Wendet einen Fix auf eine Datei an:
    - optional: erstellt vorher ein Backup (Option 3: nur ein letztes Backup)
    - schreibt den neuen Inhalt in die Datei

    Rückgabe:
        (erfolg: bool, nachricht: str)
    """
    target_path = target_path.resolve()

    if create_backup_before:
        backup_path = create_backup(target_path)
        if backup_path is None:
            return False, f"Backup fehlgeschlagen: Datei existiert nicht: {target_path}"

    try:
        write_file_safely(target_path, new_content)
        return True, f"Fix angewendet auf: {target_path}"
    except Exception as e:
        return False, f"Fehler beim Schreiben der Datei {target_path}: {e}"


def rollback_last_fix(target_path: Path) -> Tuple[bool, str]:
    """
    Setzt die Datei auf die letzte Backup-Version zurück.
    Rückgabe:
        (erfolg: bool, nachricht: str)
    """
    target_path = target_path.resolve()

    if not has_backup(target_path):
        return False, f"Kein Backup vorhanden für: {target_path}"

    try:
        ok = restore_backup(target_path)
        if not ok:
            return False, f"Backup konnte nicht wiederhergestellt werden: {target_path}"
        return True, f"Backup wiederhergestellt für: {target_path}"
    except Exception as e:
        return False, f"Fehler beim Wiederherstellen des Backups für {target_path}: {e}"


def timestamp() -> str:
    """
    Einfacher Zeitstempel-String, falls du ihn loggen willst.
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
