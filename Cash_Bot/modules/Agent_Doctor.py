import tkinter as tk
from tkinter import ttk
from pathlib import Path

from doctor_core.logging import log_doctor
from doctor_core.engine_manager import EngineManager
from doctor_core.state import DoctorState
from doctor_core.simulation import Phase6Simulation

from doctor_core.voice import VoiceEngine
from doctor_core.system_check import SystemChecker
from doctor_core.log_analysis import LogAnalyzer
from doctor_core.module_builder import ModuleBuilder
from doctor_core.module_extender import ModuleExtender
from doctor_core.worker_optimizer import WorkerOptimizer
from doctor_core.telegram_optimizer import TelegramOptimizer
from doctor_core.auto_docs import AutoDocs
from doctor_core.tests import TestRunner
from doctor_core.phase5_brain import Phase5Brain
from doctor_core.background import BackgroundMonitor

from doctor_core.auto_fix_engine import (
    apply_fix_with_backup,
    rollback_last_fix,
)

# PRO-Version FixSuggestionEngine
from modules.engines.engine_fix_suggestions import FixSuggestionEngine


# Basis-Pfade
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
LOGS_DIR = BASE_DIR / "logs"
MODULES_DIR = BASE_DIR / "modules"
ENGINES_DIR = MODULES_DIR / "engines"

# Dateien
TELEGRAM_TOKEN_FILE = CONFIG_DIR / "token.txt"
TELEGRAM_CHAT_ID_FILE = CONFIG_DIR / "telegram_chat_id.json"
CREDENTIALS_FILE = CONFIG_DIR / "doctor_credentials.json"
DOCTOR_STATE_FILE = CONFIG_DIR / "doctor_state.json"
SYSTEM_MAP_FILE = CONFIG_DIR / "system_map.json"
DOC_FILE = CONFIG_DIR / "doctor_docs.json"
TEST_REPORT_FILE = CONFIG_DIR / "doctor_tests.json"
PREDICTIVE_STATE_FILE = CONFIG_DIR / "predictive_state.json"
PRIORITY_FILE = CONFIG_DIR / "priority_plan.json"
FIX_SUGGESTIONS_FILE = CONFIG_DIR / "fix_suggestions.json"
OPTIMIZER_PLAN_FILE = CONFIG_DIR / "optimizer_plan.json"
LEARNING_FILE = CONFIG_DIR / "learning_state.json"
PLANNER_FILE = CONFIG_DIR / "planner_plan.json"


class AgentDoctorApp:
    def __init__(self):
        # Engines & State
        self.engines = EngineManager()
        self.state = DoctorState()

        # Voice
        self.voice = VoiceEngine(logger=log_doctor)

        # Core-Module
        self.system_checker = SystemChecker(
            logger=log_doctor,
            config_dir=CONFIG_DIR,
            logs_dir=LOGS_DIR,
            modules_dir=MODULES_DIR,
            engines_dir=ENGINES_DIR,
            files_to_check=[
                TELEGRAM_TOKEN_FILE,
                TELEGRAM_CHAT_ID_FILE,
                CREDENTIALS_FILE,
                DOCTOR_STATE_FILE,
                SYSTEM_MAP_FILE,
                DOC_FILE,
                TEST_REPORT_FILE,
                PREDICTIVE_STATE_FILE,
                PRIORITY_FILE,
                FIX_SUGGESTIONS_FILE,
                OPTIMIZER_PLAN_FILE,
                LEARNING_FILE,
                PLANNER_FILE,
            ],
        )

        self.log_analyzer = LogAnalyzer(logger=log_doctor, logs_dir=LOGS_DIR)
        self.module_builder = ModuleBuilder(logger=log_doctor, modules_dir=MODULES_DIR)
        self.module_extender = ModuleExtender(logger=log_doctor, modules_dir=MODULES_DIR)
        self.worker_optimizer = WorkerOptimizer(logger=log_doctor)
        self.telegram_optimizer = TelegramOptimizer(logger=log_doctor)
        self.auto_docs = AutoDocs(logger=log_doctor, modules_dir=MODULES_DIR)
        self.test_runner = TestRunner(logger=log_doctor)
        self.phase5_brain = Phase5Brain(logger=log_doctor)
        self.background = BackgroundMonitor(logger=log_doctor)

        # Phase‑7 PRO Engine
        self.engines.fix = FixSuggestionEngine(
            logger=log_doctor,
            logs_dir=LOGS_DIR,
            state_file=FIX_SUGGESTIONS_FILE,
        )

        # UI
        self.root = tk.Tk()
        self.root.title("Agent_Doctor // System Engineer (PRO)")
        self.root.configure(bg="#111111")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#111111")
        style.configure("TLabel", background="#111111", foreground="#ffffff")
        style.configure("TButton", background="#222222", foreground="#ffffff")

        main = ttk.Frame(self.root, padding=10)
        main.pack(fill="both", expand=True)

        header = ttk.Label(
            main,
            text="Agent_Doctor – PRO‑Architektur (Phase 5 + Phase 6 + Phase 7 Auto‑Fix)",
            font=("Segoe UI", 13, "bold"),
        )
        header.pack(anchor="w", pady=(0, 10))

        self.status_label = ttk.Label(
            main,
            text="Status: Online – Engines geladen.",
            font=("Segoe UI", 10),
        )
        self.status_label.pack(anchor="w", pady=(0, 10))

        # -------------------------
        # UI-BUTTONS / FUNKTIONSLEISTE
        # -------------------------

        # System
        system_frame = ttk.Frame(main)
        system_frame.pack(anchor="w", pady=(0, 10))

        ttk.Label(system_frame, text="System:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=5)
        ttk.Button(system_frame, text="System prüfen", command=self._run_system_check).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(system_frame, text="Logs analysieren", command=self._run_log_analysis).grid(row=1, column=1, padx=5, pady=5)

        # Module
        module_frame = ttk.Frame(main)
        module_frame.pack(anchor="w", pady=(0, 10))

        ttk.Label(module_frame, text="Module:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=5)
        ttk.Button(module_frame, text="Modul bauen", command=self._open_module_builder_window).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(module_frame, text="Modul erweitern", command=self._open_module_extender_window).grid(row=1, column=1, padx=5, pady=5)

        # Optimierung
        opt_frame = ttk.Frame(main)
        opt_frame.pack(anchor="w", pady=(0, 10))

        ttk.Label(opt_frame, text="Optimierung:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=5)
        ttk.Button(opt_frame, text="Worker optimieren", command=self._run_worker_opt).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(opt_frame, text="Telegram optimieren", command=self._run_telegram_opt).grid(row=1, column=1, padx=5, pady=5)

        # Dokumentation
        doc_frame = ttk.Frame(main)
        doc_frame.pack(anchor="w", pady=(0, 10))

        ttk.Label(doc_frame, text="Dokumentation:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=5)
        ttk.Button(doc_frame, text="Auto-Doku", command=self._run_auto_docs).grid(row=1, column=0, padx=5, pady=5)

        # Tests
        test_frame = ttk.Frame(main)
        test_frame.pack(anchor="w", pady=(0, 10))

        ttk.Label(test_frame, text="Tests:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=5)
        ttk.Button(test_frame, text="Tests ausführen", command=self._run_tests).grid(row=1, column=0, padx=5, pady=5)

        # Phase 5
        phase5_frame = ttk.Frame(main)
        phase5_frame.pack(anchor="w", pady=(0, 10))

        ttk.Label(phase5_frame, text="Phase 5:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=5)
        ttk.Button(phase5_frame, text="Phase‑5‑Brain aktualisieren", command=self._run_phase5_brain).grid(row=1, column=0, padx=5, pady=5)

        # Phase 6
        phase6_frame = ttk.Frame(main)
        phase6_frame.pack(anchor="w", pady=(0, 10))

        ttk.Label(phase6_frame, text="Phase‑6‑Funktionen:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=5)
        ttk.Button(phase6_frame, text="Phase‑6‑Simulation starten", command=self.run_phase6_simulation).grid(row=1, column=0, padx=5, pady=5)

        # Phase 7
        phase7_frame = ttk.Frame(main)
        phase7_frame.pack(anchor="w", pady=(0, 10))

        ttk.Label(phase7_frame, text="Phase‑7‑Auto‑Fix:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=5)
        ttk.Button(phase7_frame, text="Auto‑Fix aus Logs (Vorschlag laden)", command=self._run_auto_fix_from_logs).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(phase7_frame, text="Fix anwenden (manuell)", command=self._open_auto_fix_window).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(phase7_frame, text="Letztes Backup wiederherstellen", command=self._open_rollback_window).grid(row=1, column=2, padx=5, pady=5)

        # Voice
        voice_frame = ttk.Frame(main)
        voice_frame.pack(anchor="w", pady=(0, 10))

        ttk.Label(voice_frame, text="Voice:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=5)
        ttk.Button(voice_frame, text="Voice‑Test", command=lambda: self.say("Hallo Ricardo, die Voice‑Engine funktioniert.")).grid(row=1, column=0, padx=5, pady=5)

        # Log-Ausgabe
        self.log_box = tk.Text(main, bg="#000000", fg="#00ff88", insertbackground="#00ff88", height=18, borderwidth=0)
        self.log_box.pack(fill="both", expand=True)

        # Start-Log
        log_doctor("Agent_Doctor PRO gestartet.")
        self._log_ui("Agent_Doctor PRO gestartet.")

        # Begrüßung
        self.voice.startup_greeting()

        # Hintergrundüberwachung starten
        self.background.start()
    # ----------------------------------------------------
    # UI HELFER
    # ----------------------------------------------------
    def _log_ui(self, msg: str):
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")

    def set_status(self, text: str):
        self.status_label.config(text=text)

    def say(self, text: str):
        self.voice.speak(text)

    # ----------------------------------------------------
    # SYSTEM
    # ----------------------------------------------------
    def _run_system_check(self):
        self.set_status("Status: Systemprüfung läuft...")
        ok = self.system_checker.run()
        if ok:
            self.say("Die Systemstruktur wirkt konsistent.")
        else:
            self.say("Ich habe Probleme im System erkannt.")
        self.set_status("Status: Systemprüfung abgeschlossen.")

    def _run_log_analysis(self):
        self.set_status("Status: Loganalyse läuft...")
        ok = self.log_analyzer.run()
        if ok:
            self.say("Ich habe Log‑Dateien gefunden.")
        else:
            self.say("Ich habe keine Log‑Dateien gefunden.")
        self.set_status("Status: Loganalyse abgeschlossen.")

    # ----------------------------------------------------
    # MODULE
    # ----------------------------------------------------
    def _open_module_builder_window(self):
        win = tk.Toplevel(self.root)
        win.title("Modul bauen")
        win.configure(bg="#111111")

        frame = ttk.Frame(win, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Modulname:", font=("Segoe UI", 9)).pack(anchor="w")
        name_entry = tk.Entry(frame, bg="#000000", fg="#ffffff", insertbackground="#ffffff")
        name_entry.pack(fill="x", pady=5)

        def create():
            name = name_entry.get().strip()
            ok = self.module_builder.create_module(name)
            if ok:
                self.say("Ich habe das Modul erstellt.")
            else:
                self.say("Das Modul konnte nicht erstellt werden.")

        ttk.Button(frame, text="Erstellen", command=create).pack(anchor="e", pady=5)

    def _open_module_extender_window(self):
        win = tk.Toplevel(self.root)
        win.title("Modul erweitern")
        win.configure(bg="#111111")

        frame = ttk.Frame(win, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Modulname:", font=("Segoe UI", 9)).pack(anchor="w")
        name_entry = tk.Entry(frame, bg="#000000", fg="#ffffff", insertbackground="#ffffff")
        name_entry.pack(fill="x", pady=5)

        ttk.Label(frame, text="Code anhängen:", font=("Segoe UI", 9)).pack(anchor="w")
        code_box = tk.Text(frame, bg="#000000", fg="#ffffff", insertbackground="#ffffff", height=10)
        code_box.pack(fill="both", pady=5)

        def extend():
            name = name_entry.get().strip()
            code = code_box.get("1.0", "end").strip()
            ok = self.module_extender.append_to_module(name, code)
            if ok:
                self.say("Ich habe das Modul erweitert.")
            else:
                self.say("Das Modul konnte nicht erweitert werden.")

        ttk.Button(frame, text="Anhängen", command=extend).pack(anchor="e", pady=5)
    # ----------------------------------------------------
    # OPTIMIERUNG
    # ----------------------------------------------------
    def _run_worker_opt(self):
        self.set_status("Status: Worker-Optimierung läuft...")
        ok = self.worker_optimizer.optimize()
        if ok:
            self.say("Worker-Optimierung abgeschlossen.")
        self.set_status("Status: Worker-Optimierung abgeschlossen.")

    def _run_telegram_opt(self):
        self.set_status("Status: Telegram-Optimierung läuft...")
        ok = self.telegram_optimizer.optimize()
        if ok:
            self.say("Telegram-Optimierung abgeschlossen.")
        self.set_status("Status: Telegram-Optimierung abgeschlossen.")

    # ----------------------------------------------------
    # DOKUMENTATION
    # ----------------------------------------------------
    def _run_auto_docs(self):
        self.set_status("Status: Auto-Doku läuft...")
        ok = self.auto_docs.generate()
        if ok:
            self.say("Auto-Dokumentation abgeschlossen.")
        self.set_status("Status: Auto-Doku abgeschlossen.")

    # ----------------------------------------------------
    # TESTS
    # ----------------------------------------------------
    def _run_tests(self):
        self.set_status("Status: Tests laufen...")
        ok = self.test_runner.run()
        if ok:
            self.say("Tests abgeschlossen.")
        self.set_status("Status: Tests abgeschlossen.")

    # ----------------------------------------------------
    # PHASE 5
    # ----------------------------------------------------
    def _run_phase5_brain(self):
        self.set_status("Status: Phase‑5‑Brain Update läuft...")
        ok = self.phase5_brain.update()
        if ok:
            self.say("Phase‑5‑Brain aktualisiert.")
        self.set_status("Status: Phase‑5‑Brain abgeschlossen.")

    # ----------------------------------------------------
    # PHASE 6
    # ----------------------------------------------------
    def run_phase6_simulation(self):
        self.set_status("Status: Phase‑6‑Simulation läuft...")
        sim = Phase6Simulation(self.engines, self.state)
        sim.run()
        self.say("Phase‑6‑Simulation abgeschlossen.")
        self.set_status("Status: Phase‑6‑Simulation abgeschlossen.")
    # ----------------------------------------------------
    # PHASE 7 – AUTO‑FIX PRO
    # ----------------------------------------------------
    def _run_auto_fix_from_logs(self):
        self.set_status("Status: Auto‑Fix aus Logs läuft...")

        # Prüfen ob Engine existiert
        if not hasattr(self.engines, "fix") or self.engines.fix is None:
            self.say("Keine FixSuggestionEngine geladen.")
            self.set_status("Status: Auto‑Fix aus Logs abgeschlossen.")
            return

        # Vorschläge laden
        suggestions = self.engines.fix.update()
        if not suggestions:
            self.say("Keine Fix‑Vorschläge in den Logs gefunden.")
            self.set_status("Status: Auto‑Fix aus Logs abgeschlossen.")
            return

        # Wir nehmen den ersten Vorschlag
        s = suggestions[0]
        log_file = s.get("log_file", "")
        keyword = s.get("keyword", "")
        hint = s.get("hint", "")

        source_file = s.get("source_file")
        line = s.get("line")
        function = s.get("function")

        # Pfad automatisch vorbelegen
        prefill_path = ""
        if source_file:
            try:
                src_path = Path(source_file).resolve()
                prefill_path = str(src_path.relative_to(BASE_DIR))
            except Exception:
                prefill_path = ""

        # Template erzeugen
        template = (
            f"# Auto‑Fix‑Vorschlag basierend auf Log:\n"
            f"# Log-Datei: {log_file}\n"
            f"# Keyword: {keyword}\n"
            f"# Hinweis: {hint}\n\n"
        )

        if source_file:
            template += f"# Quell‑Datei: {source_file}\n"
        if line:
            template += f"# Zeile: {line}\n"
        if function:
            template += f"# Funktion: {function}\n"
        template += "\n"

        template += (
            "# Vorschlag:\n"
            "# 1. Öffne die angegebene Datei/Zeile.\n"
            "# 2. Analysiere die Ursache (z. B. falscher Wert, fehlende Variable, falscher Typ).\n"
            "# 3. Passe den Code hier so an, wie er final in der Datei stehen soll.\n\n"
            "# Beispiel: Fehlerhafte Zeile durch robustere Variante ersetzen.\n"
            "# alte_zeile = ...\n"
            "# neue_zeile = ...\n"
        )

        # Fenster öffnen
        self._open_auto_fix_window(prefill_path=prefill_path, prefill_code=template)

        self.say("Ich habe einen Fix‑Vorschlag aus den Logs geladen. Pfad wurde automatisch vorbelegt.")
        self.set_status("Status: Auto‑Fix aus Logs abgeschlossen.")

    # ----------------------------------------------------
    # AUTO‑FIX UI
    # ----------------------------------------------------
    def _open_auto_fix_window(self, prefill_path: str = "", prefill_code: str = ""):
        win = tk.Toplevel(self.root)
        win.title("Auto‑Fix anwenden (mit Backup)")
        win.configure(bg="#111111")

        frame = ttk.Frame(win, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Zieldatei (Pfad relativ zu Projekt):", font=("Segoe UI", 9)).pack(anchor="w")
        path_entry = tk.Entry(frame, bg="#000000", fg="#ffffff", insertbackground="#ffffff")
        path_entry.pack(fill="x", pady=5)

        if prefill_path:
            path_entry.insert(0, prefill_path)

        ttk.Label(frame, text="Neuer Inhalt:", font=("Segoe UI", 9)).pack(anchor="w")
        code_box = tk.Text(frame, bg="#000000", fg="#ffffff", insertbackground="#ffffff", height=12)
        code_box.pack(fill="both", pady=5)

        if prefill_code:
            code_box.insert("1.0", prefill_code)

        def apply_fix():
            rel_path = path_entry.get().strip()
            if not rel_path:
                self.say("Kein Pfad angegeben.")
                return

            target_path = (BASE_DIR / rel_path).resolve()
            new_content = code_box.get("1.0", "end").rstrip("\n")

            ok, msg = apply_fix_with_backup(target_path, new_content, create_backup_before=True)
            log_doctor(msg)
            self._log_ui(msg)
            if ok:
                self.say("Fix angewendet. Backup wurde erstellt.")
            else:
                self.say("Fix konnte nicht angewendet werden.")

        ttk.Button(frame, text="Fix anwenden", command=apply_fix).pack(anchor="e", pady=5)

    # ----------------------------------------------------
    # ROLLBACK
    # ----------------------------------------------------
    def _open_rollback_window(self):
        win = tk.Toplevel(self.root)
        win.title("Letztes Backup wiederherstellen")
        win.configure(bg="#111111")

        frame = ttk.Frame(win, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Zieldatei (Pfad relativ zu Projekt):", font=("Segoe UI", 9)).pack(anchor="w")
        path_entry = tk.Entry(frame, bg="#000000", fg="#ffffff", insertbackground="#ffffff")
        path_entry.pack(fill="x", pady=5)

        def do_rollback():
            rel_path = path_entry.get().strip()
            if not rel_path:
                self.say("Kein Pfad angegeben.")
                return

            target_path = (BASE_DIR / rel_path).resolve()
            ok, msg = rollback_last_fix(target_path)
            log_doctor(msg)
            self._log_ui(msg)
            if ok:
                self.say("Backup wiederhergestellt.")
            else:
                self.say("Kein Backup verfügbar oder Wiederherstellung fehlgeschlagen.")

        ttk.Button(frame, text="Backup wiederherstellen", command=do_rollback).pack(anchor="e", pady=5)

    # ----------------------------------------------------
    # START
    # ----------------------------------------------------
    def run(self):
        self.root.mainloop()


def main():
    app = AgentDoctorApp()
    app.run()


if __name__ == "__main__":
    main()
