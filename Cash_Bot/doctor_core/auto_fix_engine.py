from pathlib import Path
from datetime import datetime
from typing import Tuple

from doctor_core.logging import log_doctor


def _make_backup_path(target_path: Path) -> Path:
    """
    Erzeugt einen Backup-Pfad neben der Zieldatei.
    Beispiel: worker.py -> worker.py.bak_2026-06-24_15-30-12
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return target_path.with_suffix(target_path.suffix + f".bak_{timestamp}")


def apply_fix_with_backup(
    target_path: Path,
    new_content: str,
    create_backup_before: bool = True,
) -> Tuple[bool, str]:
    """
    PRO-Version:
    - optionales Backup der bestehenden Datei
    - schreibt neuen Inhalt
    - gibt (ok, message) zurück
    """

    try:
        target_path = Path(target_path)

        if not target_path.exists():
            # Falls Datei nicht existiert, Verzeichnis anlegen
            target_path.parent.mkdir(parents=True, exist_ok=True)
            original_exists = False
        else:
            original_exists = True

        backup_path = None

        if create_backup_before and original_exists:
            backup_path = _make_backup_path(target_path)
            backup_path.write_text(target_path.read_text(encoding="utf-8"), encoding="utf-8")
            log_doctor(f"AutoFix: Backup erstellt: {backup_path}")

        # Neuen Inhalt schreiben
        target_path.write_text(new_content, encoding="utf-8")
        msg = f"AutoFix: Neuer Inhalt in {target_path} geschrieben."
        if backup_path:
            msg += f" Backup: {backup_path}"
        return True, msg

    except Exception as e:
        msg = f"AutoFix: Fehler beim Anwenden des Fixes auf {target_path}: {e}"
        log_doctor(msg)
        return False, msg


def _find_latest_backup(target_path: Path) -> Path | None:
    """
    Sucht das neueste Backup für die Zieldatei.
    """
    target_path = Path(target_path)
    pattern = target_path.with_suffix(target_path.suffix + ".bak_")
    parent = target_path.parent

    if not parent.exists():
        return None

    candidates = [p for p in parent.iterdir() if p.name.startswith(pattern.name)]
    if not candidates:
        return None

    # Nach Datum im Namen sortieren (lexikographisch reicht hier)
    candidates.sort(reverse=True)
    return candidates[0]


def rollback_last_fix(target_path: Path) -> Tuple[bool, str]:
    """
    PRO-Version:
    - sucht das letzte Backup
    - stellt es wieder her
    - gibt (ok, message) zurück
    """
    try:
        target_path = Path(target_path)
        backup_path = _find_latest_backup(target_path)

        if backup_path is None or not backup_path.exists():
            msg = f"Rollback: Kein Backup für {target_path} gefunden."
            log_doctor(msg)
            return False, msg

        # Backup-Inhalt zurückschreiben
        content = backup_path.read_text(encoding="utf-8")
        target_path.write_text(content, encoding="utf-8")

        msg = f"Rollback: Backup {backup_path} nach {target_path} wiederhergestellt."
        log_doctor(msg)
        return True, msg

    except Exception as e:
        msg = f"Rollback: Fehler beim Wiederherstellen von {target_path}: {e}"
        log_doctor(msg)
        return False, msg
