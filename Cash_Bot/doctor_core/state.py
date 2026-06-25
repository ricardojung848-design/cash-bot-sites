from pathlib import Path
import sqlite3
import json
import time
import threading

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
DB_FILE = CONFIG_DIR / "doctor_memory.sqlite"

class DoctorState:
    def __init__(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_db()

    def _get_connection(self):
        """Erstellt eine thread-sichere Verbindung zur SQLite-Datenbank."""
        conn = sqlite3.connect(DB_FILE, timeout=30.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initialisiert die relationale Enterprise-Datenstruktur."""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # 1. Tabelle für Modul-Zustände und Kontexte
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS system_states (
                        key TEXT PRIMARY KEY,
                        data TEXT,
                        last_update TEXT
                    )
                """)
                
                # 2. Langzeit-Fehlerhistorie (Wichtig für die Auto-Fix-Engine)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS error_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        module_name TEXT,
                        error_message TEXT,
                        traceback TEXT,
                        timestamp TEXT,
                        fixed INTEGER DEFAULT 0,
                        fix_applied TEXT
                    )
                """)
                
                # 3. Optimierungs-Historie
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS optimization_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        module_name TEXT,
                        metric_improved TEXT,
                        old_value REAL,
                        new_value REAL,
                        timestamp TEXT
                    )
                """)
                
                # 4. Social Media Performance & Analytics
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS social_stats (
                        platform TEXT,
                        metric_key TEXT,
                        metric_value REAL,
                        timestamp TEXT,
                        PRIMARY KEY (platform, metric_key, timestamp)
                    )
                """)
                
                conn.commit()
            
            # Migriere alte JSON-Dateien, falls vorhanden, um Abwärtskompatibilität zu sichern
            self._migrate_old_jsons()

    def _migrate_old_jsons(self):
        """Migriert Daten aus alten JSON-Dateien automatisch in die DB, falls sie existieren."""
        old_files = {
            "predictive_state": CONFIG_DIR / "predictive_state.json",
            "priority_plan": CONFIG_DIR / "priority_plan.json",
            "fix_suggestions": CONFIG_DIR / "fix_suggestions.json",
            "optimizer_plan": CONFIG_DIR / "optimizer_plan.json",
            "learning_state": CONFIG_DIR / "learning_state.json",
            "planner_plan": CONFIG_DIR / "planner_plan.json"
        }
        
        for key, path in old_files.items():
            if path.exists():
                try:
                    raw = path.read_text(encoding="utf-8")
                    if raw.strip():
                        data = json.loads(raw)
                        self.set_state(key, data)
                        # Datei umbenennen, um Mehrfach-Migration zu verhindern
                        path.rename(path.with_suffix(".json.bak"))
                except Exception:
                    pass

    # --- CORE CORE-API FÜR ZUSTÄNDE (Ersatz für altes JSON-System) ---

    def set_state(self, key: str, data: dict):
        """Speichert oder aktualisiert einen Zustand absolut atomar und thread-sicher."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        json_data = json.dumps(data, indent=2, ensure_ascii=False)
        
        with self._lock:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO system_states (key, data, last_update)
                    VALUES (?, ?, ?)
                    ON CONFLICT(key) DO UPDATE SET
                        data = excluded.data,
                        last_update = excluded.last_update
                """, (key, json_data, timestamp))
                conn.commit()

    def get_state(self, key: str, default: dict = None) -> dict:
        """Sucht einen Zustand nach Key."""
        if default is None:
            default = {}
        with self._lock:
            with self._get_connection() as conn:
                row = conn.execute("SELECT data FROM system_states WHERE key = ?", (key,)).fetchone()
                if row:
                    return json.loads(row["data"])
                return default

    # --- ABWÄRTSKOMPATIBILITÄT & HILFS-METHODEN ---

    def load_all(self) -> dict:
        """Gibt das vom alten System erwartete Format zurück, liest aber aus der sicheren DB."""
        return {
            "priority": self.get_state("priority_plan", {"last_update": None, "tasks": []}),
            "fixes": self.get_state("fix_suggestions", {"last_update": None, "suggestions": []}),
            "optimizer": self.get_state("optimizer_plan", {"last_update": None, "modules": []}),
            "planner": self.get_state("planner_plan", {"last_update": None, "roadmap": []}),
        }

    def update_planner(self, roadmap: list):
        """Aktualisiert den Planner-State über die neue DB-Logik."""
        data = {
            "last_update": time.strftime("%Y-%m-%d %H:%M:%S"),
            "roadmap": roadmap,
        }
        self.set_state("planner_plan", data)

    # --- NEUE PRO ENGINES MEMORY INTEGRATION ---

    def log_error(self, module_name: str, error_message: str, traceback: str = ""):
        """Erfasst Systemfehler im Langzeitgedächtnis für die Auto-Fix-Engine."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with self._lock:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO error_history (module_name, error_message, traceback, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (module_name, error_message, traceback, timestamp))
                conn.commit()

    def get_unfixed_errors(self) -> list:
        """Holt alle ungelösten Fehler für die Auto-Fix-Engine."""
        with self._lock:
            with self._get_connection() as conn:
                rows = conn.execute("SELECT * FROM error_history WHERE fixed = 0").fetchall()
                return [dict(row) for row in rows]

    def mark_error_fixed(self, error_id: int, fix_applied: str):
        """Markiert einen Fehler als behoben."""
        with self._lock:
            with self._get_connection() as conn:
                conn.execute("""
                    UPDATE error_history 
                    SET fixed = 1, fix_applied = ? 
                    WHERE id = ?
                """, (fix_applied, error_id))
                conn.commit()