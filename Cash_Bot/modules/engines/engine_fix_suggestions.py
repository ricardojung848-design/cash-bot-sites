import time
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # .../Cash_Bot
CONFIG_DIR = BASE_DIR / "config"
FIX_SUGGESTIONS_FILE = CONFIG_DIR / "fix_suggestions.json"
LOGS_DIR = BASE_DIR / "logs"


def _safe_load_json(path: Path, default):
    try:
        if not path.exists():
            return default
        raw = path.read_text(encoding="utf-8")
        if not raw.strip():
            return default
        return json.loads(raw)
    except Exception:
        return default


def _safe_save_json(path: Path, data: dict):
    try:
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        pass


class FixSuggestionEngine:
    """
    Liest einfache Log-Dateien und erzeugt grobe Fix-Vorschläge
    basierend auf Schlüsselwörtern.
    """

    KEYWORDS = {
        "SyntaxError": "Syntax prüfen, insbesondere Anführungszeichen und Klammern.",
        "ConnectionError": "Netzwerkverbindung und API-URL prüfen.",
        "Timeout": "Timeout erhöhen oder Last reduzieren.",
        "KeyError": "Dictionary-Schlüssel prüfen oder Default-Werte setzen.",
        "FileNotFoundError": "Pfad und Dateinamen prüfen, ggf. Datei anlegen.",
    }

    def __init__(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        if not FIX_SUGGESTIONS_FILE.exists():
            _safe_save_json(
                FIX_SUGGESTIONS_FILE,
                {
                    "last_update": None,
                    "suggestions": [],
                },
            )

    def _load_suggestions(self) -> dict:
        return _safe_load_json(
            FIX_SUGGESTIONS_FILE,
            {
                "last_update": None,
                "suggestions": [],
            },
        )

    def _save_suggestions(self, data: dict):
        _safe_save_json(FIX_SUGGESTIONS_FILE, data)

    def _scan_logs(self) -> list:
        suggestions = []
        if not LOGS_DIR.exists():
            return suggestions

        for f in LOGS_DIR.iterdir():
            if not f.is_file():
                continue
            if f.suffix not in [".log", ".txt"]:
                continue
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            for kw, hint in self.KEYWORDS.items():
                if kw in content:
                    suggestions.append(
                        {
                            "file": str(f),
                            "keyword": kw,
                            "hint": hint,
                        }
                    )
        return suggestions

    def update(self) -> list:
        suggestions = self._scan_logs()
        data = {
            "last_update": time.strftime("%Y-%m-%d %H:%M:%S"),
            "suggestions": suggestions,
        }
        self._save_suggestions(data)
        return suggestions
