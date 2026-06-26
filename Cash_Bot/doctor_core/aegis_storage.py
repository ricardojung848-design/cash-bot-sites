import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "core" / "aegis_storage.db"

class AegisStorage:
    def __init__(self):
        DB_PATH.parent.makedirs(exist_ok=True)
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(str(DB_PATH))

    def _init_db(self):
        """Erstellt die Tabellen für Aufgaben, Kalender und E-Mails"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabelle für To-Do / Erledigungen
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    status TEXT DEFAULT 'OPEN',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabelle für Kalender-Termine
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS calendar (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    event_date TEXT NOT NULL,
                    event_time TEXT NOT NULL
                )
            """)
            conn.commit()

    def add_task(self, title):
        with self._get_connection() as conn:
            conn.cursor().execute("INSERT INTO tasks (title) VALUES (?)", (title,))
            conn.commit()

    def get_all_tasks(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, status FROM tasks ORDER BY id DESC")
            return cursor.fetchall()

    def add_event(self, title, date, time_str):
        with self._get_connection() as conn:
            conn.cursor().execute("INSERT INTO calendar (title, event_date, event_time) VALUES (?, ?, ?)", (title, date, time_str))
            conn.commit()