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


def log_doctor(msg: str):
    ts = time.strftime("%H:%M:%S")
    print(f"[Doctor {ts}] {msg}")


BASE_DIR = Path(__file__).resolve().parent.parent  # .../Cash_Bot
CONFIG_DIR = BASE_DIR / "config"
LOGS_DIR = BASE_DIR / "logs"
MODULES_DIR = BASE_DIR / "modules"

CREDENTIALS_FILE = CONFIG_DIR / "doctor_credentials.json"
TELEGRAM_TOKEN_FILE = CONFIG_DIR / "token.txt"
TELEGRAM_CHAT_ID_FILE = CONFIG_DIR / "telegram_chat_id.json"
DOCTOR_STATE_FILE = CONFIG_DIR / "doctor_state.json"


class LogicAdvisor:
    def evaluate_action(self, action: str, context: dict) -> bool:
        # Platzhalter für spätere Logikregeln
        return True


class QualityAdvisor:
    def validate_action(self, action: str, context: dict) -> bool:
        # Platzhalter für spätere Qualitätsregeln
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
        self._ensure_state_file()

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
            text="Agent_Doctor – Monitoring, Self-Healing, Token- & Modul-Engineering",
            font=("Segoe UI", 13, "bold"),
        )
        header.pack(anchor="w", pady=(0, 10))

        self.status_label = ttk.Label(
            main,
            text="Status: Initialisierung...",
            font=("Segoe UI", 10),
        )
        self.status_label.pack(anchor="w", pady=(0, 10))

        btn_frame_top = ttk.Frame(main)
        btn_frame_top.pack(anchor="w", pady=(0, 10))

        self.btn_check_system = ttk.Button(
            btn_frame_top, text="System prüfen", command=self.check_system
        )
        self.btn_check_system.grid(row=0, column=0, padx=5, pady=5)

        self.btn_analyze_logs = ttk.Button(
            btn_frame_top, text="Logs analysieren", command=self.analyze_logs
        )
        self.btn_analyze_logs.grid(row=0, column=1, padx=5, pady=5)

        self.btn_basic_self_heal = ttk.Button(
            btn_frame_top, text="Basis-Self-Healing", command=self.basic_self_heal
        )
        self.btn_basic_self_heal.grid(row=0, column=2, padx=5, pady=5)

        self.btn_token_manager = ttk.Button(
            btn_frame_top, text="Token-Manager", command=self.open_token_manager
        )
        self.btn_token_manager.grid(row=0, column=3, padx=5, pady=5)

        btn_frame_bottom = ttk.Frame(main)
        btn_frame_bottom.pack(anchor="w", pady=(0, 10))

        self.btn_module_builder = ttk.Button(
            btn_frame_bottom, text="Modul bauen", command=self.open_module_builder
        )
        self.btn_module_builder.grid(row=0, column=0, padx=5, pady=5)

        self.btn_module_extender = ttk.Button(
            btn_frame_bottom, text="Modul erweitern", command=self.open_module_extender
        )
        self.btn_module_extender.grid(row=0, column=1, padx=5, pady=5)

        self.btn_optimize_worker = ttk.Button(
            btn_frame_bottom, text="Worker optimieren", command=self.optimize_worker
        )
        self.btn_optimize_worker.grid(row=0, column=2, padx=5, pady=5)

        self.btn_optimize_telegram = ttk.Button(
            btn_frame_bottom, text="Telegram optimieren", command=self.optimize_telegram
        )
        self.btn_optimize_telegram.grid(row=0, column=3, padx=5, pady=5)

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

        self.log("Agent_Doctor gestartet (Phase 3 + Hooks für Phase 4).")
        self.set_status(
            "Status: Online – Monitoring, Self-Healing, Token-Manager, Modul-Engineering, Optimierung & Lern-Hooks bereit."
        )
        self.say(
            "Agent Doctor ist online, Ricardo. Ich überwache dein System, repariere Basisprobleme, verwalte Token, baue Module und bereite erweiterte KI-Funktionen vor."
        )

    # Voice
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

    # Logging & Status
    def log(self, msg: str):
        ts = time.strftime("%H:%M:%S")
        line = f"[{ts}] {msg}\n"
        self.log_box.insert("end", line)
        self.log_box.see("end")
        log_doctor(msg)
        self._append_state_log(msg)

    def set_status(self, text: str):
        self.status_label.config(text=text)
        self._update_state_status(text)

    # Struktur-Self-Healing
    def _ensure_base_structure(self):
        for path in [CONFIG_DIR, LOGS_DIR, MODULES_DIR]:
            if not path.exists():
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    log_doctor(f"Ordner angelegt: {path}")
                except Exception as e:
                    log_doctor(f"Fehler beim Anlegen von {path}: {e}")

    def _ensure_basic_files(self):
        if not TELEGRAM_TOKEN_FILE.exists():
            try:
                TELEGRAM_TOKEN_FILE.write_text("", encoding="utf-8")
                log_doctor(f"Leere Token-Datei angelegt: {TELEGRAM_TOKEN_FILE}")
            except Exception as e:
                log_doctor(f"Fehler beim Anlegen von {TELEGRAM_TOKEN_FILE}: {e}")

        if not TELEGRAM_CHAT_ID_FILE.exists():
            try:
                TELEGRAM_CHAT_ID_FILE.write_text("{}", encoding="utf-8")
                log_doctor("telegram_chat_id.json angelegt.")
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
                log_doctor("doctor_credentials.json angelegt.")
            except Exception as e:
                log_doctor(f"Fehler beim Anlegen von doctor_credentials.json: {e}")
        else:
            self._safe_json_repair(CREDENTIALS_FILE)

    def _ensure_state_file(self):
        if not DOCTOR_STATE_FILE.exists():
            try:
                DOCTOR_STATE_FILE.write_text(
                    json.dumps(
                        {
                            "status": "initial",
                            "last_logs": [],
                            "last_commands": [],
                        },
                        indent=2,
                    ),
                    encoding="utf-8",
                )
                log_doctor("doctor_state.json angelegt.")
            except Exception as e:
                log_doctor(f"Fehler beim Anlegen von doctor_state.json: {e}")
        else:
            self._safe_json_repair(DOCTOR_STATE_FILE)

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

    # State-Hooks (Vorbereitung für Learning / Predictive)
    def _load_state(self) -> dict:
        if not DOCTOR_STATE_FILE.exists():
            return {}
        try:
            raw = DOCTOR_STATE_FILE.read_text(encoding="utf-8")
            return json.loads(raw)
        except Exception:
            return {}

    def _save_state(self, state: dict):
        try:
            DOCTOR_STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
        except Exception as e:
            log_doctor(f"Fehler beim Speichern von doctor_state.json: {e}")

    def _append_state_log(self, msg: str):
        state = self._load_state()
        logs = state.get("last_logs", [])
        logs.append(msg)
        if len(logs) > 50:
            logs = logs[-50:]
        state["last_logs"] = logs
        self._save_state(state)

    def _update_state_status(self, status: str):
        state = self._load_state()
        state["status"] = status
        self._save_state(state)

    def _append_state_command(self, cmd: str):
        state = self._load_state()
        cmds = state.get("last_commands", [])
        cmds.append(cmd)
        if len(cmds) > 50:
            cmds = cmds[-50:]
        state["last_commands"] = cmds
        self._save_state(state)

    # Hintergrundüberwachung
    def _background_loop(self):
        self.log("Hintergrundüberwachung gestartet.")
        while True:
            self._ensure_base_structure()
            self._ensure_basic_files()
            self._ensure_credentials_file()
            self._ensure_state_file()
            time.sleep(10)

    # Systemprüfung
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

        issues = []

        for path in [CONFIG_DIR, LOGS_DIR, MODULES_DIR]:
            if not path.exists():
                issues.append(f"Fehlender Ordner: {path}")

        for path in [TELEGRAM_TOKEN_FILE, TELEGRAM_CHAT_ID_FILE, CREDENTIALS_FILE, DOCTOR_STATE_FILE]:
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

    # Loganalyse
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

        log_files = []
        if LOGS_DIR.exists():
            for f in LOGS_DIR.iterdir():
                if f.is_file() and f.suffix in [".log", ".txt"]:
                    log_files.append(f)

        if not log_files:
            self.log("Keine Log-Dateien gefunden (Basis).")
            self.say("Ich habe keine Log-Dateien gefunden. Die Loganalyse ist begrenzt.")
        else:
            self.log(f"{len(log_files)} Log-Datei(en) gefunden.")
            self.say("Ich habe Log-Dateien gefunden. In späteren Phasen werde ich sie detailliert auswerten.")

        self.set_status("Status: Loganalyse abgeschlossen.")

    # Basis-Self-Healing
    def basic_self_heal(self):
        action = "basic_self_heal"
        context = {}
        if not self._approve_action(action, context):
            self.log("Aktion 'Basis-Self-Healing' wurde von Beratern abgelehnt.")
            self.say("Die Berater lehnen diese Self-Healing-Aktion ab. Ich führe sie nicht aus.")
            return

        self.log("Starte Basis-Self-Healing.")
        self.set_status("Status: Basis-Self-Healing aktiv.")
        self.say("Ich führe eine einfache Selbstheilungsroutine aus.")

        self._ensure_base_structure()
        self._ensure_basic_files()
        self._ensure_credentials_file()
        self._ensure_state_file()

        self.log("Basis-Self-Healing abgeschlossen.")
        self.set_status("Status: Basis-Self-Healing abgeschlossen.")
        self.say("Die Basis-Self-Healing-Routine ist abgeschlossen.")

    # Token-Manager
    def open_token_manager(self):
        self.log("Token-Manager geöffnet.")
        self.say("Ich öffne den Token-Manager für deine Zugangsdaten.")

        tm = tk.Toplevel(self.root)
        tm.title("Agent_Doctor – Token-Manager")
        tm.configure(bg="#111111")

        frame = ttk.Frame(tm, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="Verwaltung von Token / API-Keys (Basis-Version)",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        creds = self._load_credentials()

        ttk.Label(frame, text="Telegram-Token:", font=("Segoe UI", 9)).pack(anchor="w")
        telegram_entry = tk.Entry(
            frame,
            bg="#000000",
            fg="#ffffff",
            insertbackground="#ffffff",
            borderwidth=1,
        )
        telegram_entry.pack(fill="x", pady=(0, 5))
        telegram_entry.insert(0, creds.get("telegram_token", ""))

        ttk.Label(frame, text="OpenAI-Key:", font=("Segoe UI", 9)).pack(anchor="w")
        openai_entry = tk.Entry(
            frame,
            bg="#000000",
            fg="#ffffff",
            insertbackground="#ffffff",
            borderwidth=1,
        )
        openai_entry.pack(fill="x", pady=(0, 5))
        openai_entry.insert(0, creds.get("openai_key", ""))

        ttk.Label(frame, text="Instagram-Token:", font=("Segoe UI", 9)).pack(anchor="w")
        insta_entry = tk.Entry(
            frame,
            bg="#000000",
            fg="#ffffff",
            insertbackground="#ffffff",
            borderwidth=1,
        )
        insta_entry.pack(fill="x", pady=(0, 5))
        insta_entry.insert(0, creds.get("instagram_token", ""))

        def save_creds():
            new_creds = {
                "telegram_token": telegram_entry.get().strip(),
                "openai_key": openai_entry.get().strip(),
                "instagram_token": insta_entry.get().strip(),
            }
            try:
                CREDENTIALS_FILE.write_text(
                    json.dumps(new_creds, indent=2), encoding="utf-8"
                )
                self.log("Token/Keys im Token-Manager gespeichert.")
                self.say("Ich habe die Token und Keys im Token-Manager gespeichert.")
            except Exception as e:
                self.log(f"Fehler beim Speichern der Token: {e}")
                self.say("Beim Speichern der Token ist ein Fehler aufgetreten.")

        save_btn = ttk.Button(frame, text="Speichern", command=save_creds)
        save_btn.pack(anchor="e", pady=(10, 0))

    def _load_credentials(self) -> dict:
        if not CREDENTIALS_FILE.exists():
            return {}
        try:
            raw = CREDENTIALS_FILE.read_text(encoding="utf-8")
            return json.loads(raw)
        except Exception:
            return {}

    # Modul-Builder
    def open_module_builder(self):
        self.log("Modul-Builder geöffnet.")
        self.say("Ich öffne den Modul-Builder, um neue Module zu erzeugen.")

        mb = tk.Toplevel(self.root)
        mb.title("Agent_Doctor – Modul-Builder")
        mb.configure(bg="#111111")

        frame = ttk.Frame(mb, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="Neues Modul erstellen",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        ttk.Label(frame, text="Modulname (ohne .py):", font=("Segoe UI", 9)).pack(anchor="w")
        name_entry = tk.Entry(
            frame,
            bg="#000000",
            fg="#ffffff",
            insertbackground="#ffffff",
            borderwidth=1,
        )
        name_entry.pack(fill="x", pady=(0, 5))

        def create_module():
            name = name_entry.get().strip()
            if not name:
                self.log("Modul-Builder: Kein Name angegeben.")
                self.say("Für den Modul-Builder benötige ich einen Modulnamen.")
                return

            filename = MODULES_DIR / f"{name}.py"
            if filename.exists():
                self.log(f"Modul-Builder: Datei existiert bereits: {filename}")
                self.say("Dieses Modul existiert bereits. Ich überschreibe es nicht.")
                return

            class_name = "".join(part.capitalize() for part in name.split("_"))
            template_code = (
                "import time\n\n"
                f"class {class_name}:\n"
                "    def __init__(self):\n"
                "        pass\n\n"
                "    def run(self):\n"
                "        # TODO: Implementiere die Logik dieses Moduls\n"
                "        time.sleep(0.1)\n"
            )

            try:
                filename.write_text(template_code, encoding="utf-8")
                self.log(f"Neues Modul erstellt: {filename}")
                self.say("Ich habe das neue Modul erstellt. Du kannst es jetzt im System integrieren.")
            except Exception as e:
                self.log(f"Fehler beim Erstellen des Moduls: {e}")
                self.say("Beim Erstellen des Moduls ist ein Fehler aufgetreten.")

        create_btn = ttk.Button(frame, text="Modul erstellen", command=create_module)
        create_btn.pack(anchor="e", pady=(10, 0))

    # Modul-Erweiterer
    def open_module_extender(self):
        self.log("Modul-Erweiterer geöffnet.")
        self.say("Ich öffne den Modul-Erweiterer, um bestehende Module zu ergänzen.")

        me = tk.Toplevel(self.root)
        me.title("Agent_Doctor – Modul-Erweiterer")
        me.configure(bg="#111111")

        frame = ttk.Frame(me, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="Bestehendes Modul erweitern",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        modules = []
        if MODULES_DIR.exists():
            for f in MODULES_DIR.iterdir():
                if f.is_file() and f.suffix == ".py":
                    modules.append(f.name)

        if not modules:
            ttk.Label(
                frame,
                text="Keine Module gefunden im modules/-Ordner.",
                font=("Segoe UI", 9),
            ).pack(anchor="w")
            self.say("Ich habe keine Module im modules-Ordner gefunden.")
            return

        ttk.Label(frame, text="Modul auswählen:", font=("Segoe UI", 9)).pack(anchor="w")
        selected = tk.StringVar(value=modules[0])
        module_combo = ttk.Combobox(frame, textvariable=selected, values=modules, state="readonly")
        module_combo.pack(fill="x", pady=(0, 5))

        ttk.Label(frame, text="Kommentar / Erweiterungs-Hinweis:", font=("Segoe UI", 9)).pack(anchor="w")
        note_entry = tk.Entry(
            frame,
            bg="#000000",
            fg="#ffffff",
            insertbackground="#ffffff",
            borderwidth=1,
        )
        note_entry.pack(fill="x", pady=(0, 5))

        def extend_module():
            mod_name = selected.get()
            note = note_entry.get().strip()
            if not mod_name:
                self.log("Modul-Erweiterer: Kein Modul ausgewählt.")
                self.say("Für den Modul-Erweiterer benötige ich ein ausgewähltes Modul.")
                return

            target_file = MODULES_DIR / mod_name
            if not target_file.exists():
                self.log(f"Modul-Erweiterer: Datei existiert nicht: {target_file}")
                self.say("Das ausgewählte Modul existiert nicht mehr.")
                return

            addition = "\n\n# Doctor-Erweiterung:\n"
            if note:
                addition += f"# {note}\n"
            else:
                addition += "# Erweiterungspunkt für zusätzliche Funktionen.\n"

            try:
                with target_file.open("a", encoding="utf-8") as fh:
                    fh.write(addition)
                self.log(f"Modul erweitert: {target_file}")
                self.say("Ich habe das Modul erweitert. Du kannst hier zusätzliche Logik ergänzen.")
            except Exception as e:
                self.log(f"Fehler beim Erweitern des Moduls: {e}")
                self.say("Beim Erweitern des Moduls ist ein Fehler aufgetreten.")

        extend_btn = ttk.Button(frame, text="Modul erweitern", command=extend_module)
        extend_btn.pack(anchor="e", pady=(10, 0))

    # Optimizer (Basis-Platzhalter)
    def optimize_worker(self):
        action = "optimize_worker"
        context = {}
        if not self._approve_action(action, context):
            self.log("Aktion 'Worker optimieren' wurde von Beratern abgelehnt.")
            self.say("Die Berater lehnen diese Optimierung ab. Ich führe sie nicht aus.")
            return

        self.log("Starte Basis-Optimierung für Worker.")
        self.set_status("Status: Worker-Optimierung läuft...")
        self.say("Ich führe eine einfache Optimierungsroutine für den Worker aus.")

        time.sleep(1)

        self.log("Basis-Optimierung für Worker abgeschlossen.")
        self.set_status("Status: Worker-Optimierung abgeschlossen.")
        self.say("Die Basis-Optimierung für den Worker ist abgeschlossen.")

    def optimize_telegram(self):
        action = "optimize_telegram"
        context = {}
        if not self._approve_action(action, context):
            self.log("Aktion 'Telegram optimieren' wurde von Beratern abgelehnt.")
            self.say("Die Berater lehnen diese Optimierung ab. Ich führe sie nicht aus.")
            return

        self.log("Starte Basis-Optimierung für Telegram-Bot.")
        self.set_status("Status: Telegram-Optimierung läuft...")
        self.say("Ich führe eine einfache Optimierungsroutine für den Telegram-Bot aus.")

        time.sleep(1)

        self.log("Basis-Optimierung für Telegram-Bot abgeschlossen.")
        self.set_status("Status: Telegram-Optimierung abgeschlossen.")
        self.say("Die Basis-Optimierung für den Telegram-Bot ist abgeschlossen.")

    # Benutzereingaben
    def handle_user_command(self):
        text = self.input_entry.get().strip()
        if not text:
            return

        self.log(f"Benutzereingabe: {text}")
        self.input_entry.delete(0, "end")
        self._append_state_command(text)

        self.say(
            "Ich habe deine Eingabe registriert. In späteren Phasen werde ich sie direkt in technische Aktionen übersetzen."
        )

    # Berater-Freigabe
    def _approve_action(self, action: str, context: dict) -> bool:
        logic_ok = self.logic.evaluate_action(action, context)
        quality_ok = self.quality.validate_action(action, context)
        if not logic_ok or not quality_ok:
            return False
        return True

    # Mainloop
    def run(self):
        self.root.mainloop()


def main():
    app = AgentDoctorApp()
    app.run()


if __name__ == "__main__":
    main()
