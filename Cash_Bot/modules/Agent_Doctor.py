import os
import json
import time
import threading
from pathlib import Path

import tkinter as tk
from tkinter import ttk

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None


# --- einfache interne Log-Funktion ---
def log_doctor(msg: str):
    ts = time.strftime("%H:%M:%S")
    print(f"[Doctor {ts}] {msg}")


# --- Projektpfade (CashBot-Struktur) ---
BASE_DIR = Path(__file__).resolve().parent.parent  # .../Cash_Bot
CONFIG_DIR = BASE_DIR / "config"
LOGS_DIR = BASE_DIR / "logs"
MODULES_DIR = BASE_DIR / "modules"

CREDENTIALS_FILE = CONFIG_DIR / "doctor_credentials.json"
TELEGRAM_TOKEN_FILE = CONFIG_DIR / "token.txt"
TELEGRAM_CHAT_ID_FILE = CONFIG_DIR / "telegram_chat_id.json"


class LogicAdvisor:
    def evaluate_action(self, action: str, context: dict) -> bool:
        # Platzhalter für Logikprüfung – später ausbauen
        return True


class QualityAdvisor:
    def validate_action(self, action: str, context: dict) -> bool:
        # Platzhalter für Qualitätsprüfung – später ausbauen
        return True


class AgentDoctorApp:
    def __init__(self):
        self.logic = LogicAdvisor()
        self.quality = QualityAdvisor()

        self.engine = None
        if pyttsx3 is not None:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty("rate", 185)
            except Exception:
                self.engine = None

        self._ensure_base_structure()
        self._ensure_basic_files()
        self._ensure_credentials_file()

        self.root = tk.Tk()
        self.root.title("Agent_Doctor // System Engineer")
        self.root.configure(bg="#111111")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#111111")
        style.configure("TLabel", background="#111111", foreground="#ffffff")
        style.configure("TButton", background="#222222", foreground="#ffffff")
        style.map("TButton", background=[("active", "#333333")])

        main = ttk.Frame(self.root, padding=10)
        main.pack(fill="both", expand=True)

        header = ttk.Label(
            main,
            text="Agent_Doctor – Systemüberwachung, Self-Healing & Token-Manager",
            font=("Segoe UI", 13, "bold"),
        )
        header.pack(anchor="w", pady=(0, 10))

        self.status_label = ttk.Label(
            main,
            text="Status: Initialisierung...",
            font=("Segoe UI", 10),
        )
        self.status_label.pack(anchor="w", pady=(0, 10))

        btn_frame = ttk.Frame(main)
        btn_frame.pack(anchor="w", pady=(0, 10))

        self.btn_check_system = ttk.Button(
            btn_frame, text="System prüfen", command=self.check_system
        )
        self.btn_check_system.grid(row=0, column=0, padx=5, pady=5)

        self.btn_analyze_logs = ttk.Button(
            btn_frame, text="Logs analysieren", command=self.analyze_logs
        )
        self.btn_analyze_logs.grid(row=0, column=1, padx=5, pady=5)

        self.btn_basic_self_heal = ttk.Button(
            btn_frame, text="Basis-Self-Healing", command=self.basic_self_heal
        )
        self.btn_basic_self_heal.grid(row=0, column=2, padx=5, pady=5)

        self.btn_token_manager = ttk.Button(
            btn_frame, text="Token-Manager", command=self.open_token_manager
        )
        self.btn_token_manager.grid(row=0, column=3, padx=5, pady=5)

        self.log_box = tk.Text(
            main,
            bg="#000000",
            fg="#00ff88",
            insertbackground="#00ff88",
            height=16,
            borderwidth=0,
        )
        self.log_box.pack(fill="both", expand=True)

        self.input_label = ttk.Label(
            main,
            text="Kommando / Notiz an Doctor:",
            font=("Segoe UI", 9),
        )
        self.input_label.pack(anchor="w", pady=(10, 2))

        self.input_entry = tk.Entry(
            main,
            bg="#000000",
            fg="#ffffff",
            insertbackground="#ffffff",
            borderwidth=1,
        )
        self.input_entry.pack(fill="x", pady=(0, 5))

        self.btn_send = ttk.Button(
            main, text="An Doctor senden", command=self.handle_user_command
        )
        self.btn_send.pack(anchor="e", pady=(0, 5))

        threading.Thread(target=self._background_loop, daemon=True).start()

        self.log("Agent_Doctor gestartet (Phase 2: Self-Healing + Token-Manager aktiv).")
        self.set_status("Status: Online – Monitoring, Self-Healing und Token-Manager bereit.")
        self.say(
            "Agent Doctor ist online, Ricardo. Ich überwache dein System, führe Basis-Self-Healing aus und verwalte deine Token."
        )

    # --- Voice ---
    def say(self, text: str):
        if self.engine is None:
            log_doctor(f"(Voice disabled) {text}")
            return

        def _speak():
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception:
                pass

        threading.Thread(target=_speak, daemon=True).start()

    # --- Logging & Status ---
    def log(self, msg: str):
        ts = time.strftime("%H:%M:%S")
        line = f"[{ts}] {msg}\n"
        self.log_box.insert("end", line)
        self.log_box.see("end")
        log_doctor(msg)

    def set_status(self, text: str):
        self.status_label.config(text=text)

    # --- Struktur-Self-Healing (Phase 2) ---
    def _ensure_base_structure(self):
        for path in [CONFIG_DIR, LOGS_DIR, MODULES_DIR]:
            if not path.exists():
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    log_doctor(f"Ordner angelegt: {path}")
                except Exception as e:
                    log_doctor(f"Fehler beim Anlegen von {path}: {e}")

    def _ensure_basic_files(self):
        # Telegram-Token-Datei (falls du sie nutzt)
        if not TELEGRAM_TOKEN_FILE.exists():
            try:
                TELEGRAM_TOKEN_FILE.write_text("", encoding="utf-8")
                log_doctor(f"Leere Token-Datei angelegt: {TELEGRAM_TOKEN_FILE}")
            except Exception as e:
                log_doctor(f"Fehler beim Anlegen von {TELEGRAM_TOKEN_FILE}: {e}")

        # Telegram-Chat-ID JSON
        if not TELEGRAM_CHAT_ID_FILE.exists():
            try:
                TELEGRAM_CHAT_ID_FILE.write_text("{}", encoding="utf-8")
                log_doctor(f"telegram_chat_id.json angelegt.")
            except Exception as e:
                log_doctor(f"Fehler beim Anlegen von telegram_chat_id.json: {e}")
        else:
            self._safe_json_repair(TELEGRAM_CHAT_ID_FILE)

    def _ensure_credentials_file(self):
        if not CREDENTIALS_FILE.exists():
            try:
                CREDENTIALS_FILE.write_text(
                    json.dumps(
                        {
                            "telegram_token": "",
                            "openai_key": "",
                            "instagram_token": "",
                        },
                        indent=2,
                    ),
                    encoding="utf-8",
                )
                log_doctor(f"doctor_credentials.json angelegt.")
            except Exception as e:
                log_doctor(f"Fehler beim Anlegen von doctor_credentials.json: {e}")
        else:
            self._safe_json_repair(CREDENTIALS_FILE)

    def _safe_json_repair(self, path: Path):
        try:
            raw = path.read_text(encoding="utf-8")
            json.loads(raw)
        except Exception:
            try:
                path.write_text("{}", encoding="utf-8")
                log_doctor(f"JSON repariert (zurückgesetzt): {path}")
            except Exception as e:
                log_doctor(f"Fehler beim Reparieren von {path}: {e}")

    # --- Hintergrundüberwachung ---
    def _background_loop(self):
        self.log("Hintergrundüberwachung gestartet.")
        while True:
            # Basis-Checks: Struktur & JSON-Dateien
            self._ensure_base_structure()
            self._ensure_basic_files()
            self._ensure_credentials_file()
            time.sleep(10)

    # --- Systemprüfung ---
    def check_system(self):
        action = "check_system"
        context = {}
        if not self._approve_action(action, context):
            self.log("Aktion 'System prüfen' wurde von Beratern abgelehnt.")
            self.say("Die Berater lehnen diese Systemprüfung ab. Ich führe sie nicht aus.")
            return

        self.log("Starte Systemprüfung (Basis).")
        self.set_status("Status: Systemprüfung läuft...")
        self.say("Ich führe eine grundlegende Systemprüfung durch.")

        # einfache Checks: Ordner & wichtige Dateien
        issues = []

        for path in [CONFIG_DIR, LOGS_DIR, MODULES_DIR]:
            if not path.exists():
                issues.append(f"Fehlender Ordner: {path}")

        for path in [TELEGRAM_TOKEN_FILE, TELEGRAM_CHAT_ID_FILE, CREDENTIALS_FILE]:
            if not path.exists():
                issues.append(f"Fehlende Datei: {path}")

        if issues:
            for i in issues:
                self.log(f"Systemproblem erkannt: {i}")
            self.say("Ich habe strukturelle Probleme im System erkannt. Details im Log.")
        else:
            self.log("Systemstruktur wirkt konsistent (Basisprüfung).")
            self.say("Die grundlegende Systemstruktur wirkt konsistent.")

        self.set_status("Status: Systemprüfung abgeschlossen.")

    # --- Loganalyse ---
    def analyze_logs(self):
        action = "analyze_logs"
        context = {}
        if not self._approve_action(action, context):
            self.log("Aktion 'Logs analysieren' wurde von Beratern abgelehnt.")
            self.say("Die Berater lehnen diese Loganalyse ab. Ich führe sie nicht aus.")
            return

        self.log("Starte Loganalyse (Basis).")
        self.set_status("Status: Loganalyse läuft...")
        self.say("Ich analysiere die vorhandenen Logs auf offensichtliche Probleme.")

        # einfache Basis-Analyse: gibt es überhaupt Log-Dateien?
        log_files = []
        if LOGS_DIR.exists():
            for f in LOGS_DIR.iterdir():
                if f.is_file() and f.suffix in [".log", ".txt"]:
                    log_files.append(f)

        if not log_files:
            self.log("Keine Log-Dateien gefunden