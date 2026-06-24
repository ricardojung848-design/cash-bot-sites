import os
import shutil
import datetime
from typing import Optional, Tuple


# Basisverzeichnis des Projekts ermitteln (relativ zu dieser Datei)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Ordner für Backups
BACKUP_ROOT = os.path.join(BASE_DIR, "backups")


def ensure_backup_dir() -> None:
    """
    Stellt sicher, dass der Backup-Ordner existiert.
    """
    os.makedirs(BACKUP_ROOT, exist_ok=True)


def get_backup_path_for_file(target_path: str) -> str:
    """
    Liefert den Pfad zur Backup-Datei für eine bestimmte Zieldatei.
    Es gibt immer nur EIN letztes Backup pro Datei (Option 3).
    Beispiel:
        target_path:  /projekt/telegram_bot.py
        backup_path:  /projekt/backups/telegram_bot.py.bak
    """
    ensure_backup_dir()
    filename = os.path.basename(target_path)
    backup_name = f"{filename}.bak"
    return os.path.join(BACKUP_ROOT, backup_name)


def has_backup(target_path: str) -> bool:
    """
    Prüft, ob es für die angegebene Datei ein Backup gibt.
    """
    backup_path = get_backup_path_for_file(target_path)
    return os.path.isfile(backup_path)


def create_backup(target_path: str) -> Optional[str]:
    """
    Erstellt ein Backup der angegebenen Datei.
    Überschreibt das alte Backup (Option 3: nur letztes Backup).
    Gibt den Pfad zur Backup-Datei zurück oder None, wenn die Datei nicht existiert.
    """
    if not os.path.isfile(target_path):
        return None

    backup_path = get_backup_path_for_file(target_path)
    ensure_backup_dir()
    shutil.copy2(target_path, backup_path)
    return backup_path


def restore_backup(target_path: str) -> bool:
    """
    Stellt die Datei aus dem letzten Backup wieder her.
    Gibt True zurück, wenn erfolgreich, sonst False.
    """
    backup_path = get_backup_path_for_file(target_path)
    if not os.path.isfile(backup_path):
        return False

    shutil.copy2(backup_path, target_path)
    return True


def read_file_safely(path: str, encoding: str = "utf-8") -> Optional[str]:
    """
    Liest den Inhalt einer Datei sicher ein.
    Gibt den Inhalt als String zurück oder None, wenn die Datei nicht existiert.
    """
    if not os.path.isfile(path):
        return None

    with open(path, "r", encoding=encoding) as f:
        return f.read()


def write_file_safely(path: str, content: str, encoding: str = "utf-8") -> None:
    """
    Schreibt den Inhalt sicher in eine Datei.
    """
    # Sicherstellen, dass der Ordner existiert
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding=encoding) as f:
        f.write(content)


def apply_fix_with_backup(
    target_path: str,
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
    target_path = os.path.abspath(target_path)

    if create_backup_before:
        backup_path = create_backup(target_path)
        if backup_path is None:
            return False, f"Backup fehlgeschlagen: Datei existiert nicht: {target_path}"

    try:
        write_file_safely(target_path, new_content)
        return True, f"Fix angewendet auf: {target_path}"
    except Exception as e:
        return False, f"Fehler beim Schreiben der Datei {target_path}: {e}"


def rollback_last_fix(target_path: str) -> Tuple[bool, str]:
    """
    Setzt die Datei auf die letzte Backup-Version zurück.
    Rückgabe:
        (erfolg: bool, nachricht: str)
    """
    target_path = os.path.abspath(target_path)

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
    Liefert einen einfachen Zeitstempel-String, falls du ihn im Doctor/Worker loggen willst.
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
