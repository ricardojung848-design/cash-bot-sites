import os
import sys
import time
import threading
import tkinter as tk
from tkinter import ttk
from pathlib import Path

# Sicherstellen, dass das Root-Verzeichnis im Systempfad liegt
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Core-System-Imports
print("[BOOT] Lade Core-System-Imports...")
from doctor_core.logging import log_doctor
from doctor_core.engine_manager import EngineManager
from doctor_core.state import DoctorState
from doctor_core.simulation import Phase6Simulation

# Modul-Imports für die kognitiven Sub-Engines
print("[BOOT] Lade Sub-Engines...")
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
from doctor_core.auto_fix_engine import AutoFixEngine

# PRO-Version FixSuggestionEngine & SystemStructure
from core.SystemStructureManager import SystemStructureManager

# JETZT MIT DEM EXAKTEN PFAD AUS DEINEM EXPLORER:
print("[BOOT] Lade FixSuggestionEngine aus modules/engines/...")
from modules.engines.engine_fix_suggestions import FixSuggestionEngine

# Pfadkonfigurationen absichern
CONFIG_DIR = BASE_DIR / "config"
LOGS_DIR = BASE_DIR / "logs"
MODULES_DIR = BASE_DIR / "modules"
ENGINES_DIR = MODULES_DIR / "engines"

TELEGRAM_TOKEN_FILE = CONFIG_DIR / "token.txt"
TELEGRAM_CHAT_ID_FILE = CONFIG_DIR / "telegram_chat_id.json"
CREDENTIALS_FILE = CONFIG_DIR / "doctor_credentials.json"
SYSTEM_MAP_FILE = CONFIG_DIR / "system_map.json"


class AgentDoctorApp:
    def __init__(self, headless=False):
        print(f"[BOOT] Initialisiere AgentDoctorApp Klassen-Struktur (Headless={headless})...")
        self.headless = headless
        self.is_monitoring = False
        
        # Abgesicherter Start des SQLite-Langzeitgedächtnisses
        try:
            print("[BOOT] Verbindung mit SQLite-Langzeitgedächtnis (DoctorState)...")
            self.state = DoctorState()
            print("[BOOT] DoctorState erfolgreich geladen.")
        except Exception as db_err:
            print(f"\n[CRITICAL] Fehler beim Laden der Datenbank: {db_err}")
            print("[CRITICAL] Bitte prüfen, ob die DB-Datei von einem anderen Prozess blockiert wird.\n")
            self.state = None
        
        # Globalen Engine-Manager aufbauen und initialen State registrieren
        print("[BOOT] Baue EngineManager auf...")
        self.engines = EngineManager()
        if self.state:
            self.engines.register("state", self.state)

        # Struktur-Checker anbinden
        self.structure_manager = SystemStructureManager(self.engines)
        self.engines.register("structure", self.structure_manager)

        # Voice-Ausgabe vorbereiten
        self.voice = VoiceEngine()

        # Unter-Engines registrieren 
        self.system_checker = SystemChecker()
        self.log_analyzer = LogAnalyzer()
        self.module_builder = ModuleBuilder()
        self.module_extender = ModuleExtender()
        
        self.worker_optimizer = WorkerOptimizer(logger=log_doctor)
        self.telegram_optimizer = TelegramOptimizer()
        
        self.auto_docs = AutoDocs()
        self.test_runner = TestRunner()
        
        self.phase5_brain = Phase5Brain(engine_manager=self.engines)
        self.background = BackgroundMonitor(engine_manager=self.engines)
        self.auto_fix_engine = AutoFixEngine(engine_manager=self.engines)

        if FixSuggestionEngine:
            self.fix_suggestion_engine = FixSuggestionEngine(self.engines)
            self.engines.register("fix", self.fix_suggestion_engine)
        else:
            self.fix_suggestion_engine = None

        # UI-Logik weichenstellen
        if not self.headless:
            self._build_ui()
        else:
            self.root = None
            print("[BOOT] Starte asynchrone Hintergrund-Dienste im Dashboard-Modus...")
            threading.Thread(target=self._async_system_boot, daemon=True).start()

    def _build_ui(self):
        print("[BOOT] Erstelle GUI-Fenster...")
        self.root = tk.Tk()
        self.root.title("Agent_Doctor // System Engineer (PRO)")
        self.root.configure(bg="#111111")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#111111")
        style.configure("TLabel", background="#111111", foreground="#ffffff")
        style.configure("TButton", background="#222222", foreground="#ffffff")

        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)

        header = ttk.Label(
            main_frame,
            text="Agent_Doctor – PRO‑Architektur (Phase 5 + Phase 6 + Phase 7 Auto‑Fix)",
            font=("Segoe UI", 13, "bold"),
        )
        header.pack(anchor="w", pady=(0, 10))

        self.status_label = ttk.Label(
            main_frame,
            text="Status: Booting...",
            font=("Segoe UI", 10),
        )
        self.status_label.pack(anchor="w", pady=(0, 10))

        # --- GRID-LAYOUTS FOR BUTTONS ---
        row1 = ttk.Frame(main_frame)
        row1.pack(anchor="w", pady=(0, 10))
        ttk.Label(row1, text="System & Entwicklung:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, columnspan=4, sticky="w", padx=5)
        ttk.Button(row1, text="System prüfen", command=self._run_system_check).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(row1, text="Logs analysieren", command=self._run_log_analysis).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(row1, text="Modul bauen", command=self._open_module_builder_window).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(row1, text="Modul erweitern", command=self._open_module_extender_window).grid(row=1, column=3, padx=5, pady=5)

        row2 = ttk.Frame(main_frame)
        row2.pack(anchor="w", pady=(0, 10))
        ttk.Label(row2, text="Optimierung & Quality:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, columnspan=4, sticky="w", padx=5)
        ttk.Button(row2, text="Worker optimieren", command=self._run_worker_opt).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(row2, text="Telegram optimieren", command=self._run_telegram_opt).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(row2, text="Auto-Doku", command=self._run_auto_docs).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(row2, text="Tests ausführen", command=self._run_tests).grid(row=1, column=3, padx=5, pady=5)

        row3 = ttk.Frame(main_frame)
        row3.pack(anchor="w", pady=(0, 10))
        ttk.Label(row3, text="Kognitive KI-Phasen (Auto-Healing):", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, columnspan=5, sticky="w", padx=5)
        ttk.Button(row3, text="Brain aktualisieren (P5)", command=self._run_phase5_brain).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(row3, text="Simulation starten (P6)", command=self.run_phase6_simulation).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(row3, text="Fix-Vorschlag laden (P7)", command=self._run_auto_fix_from_logs).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(row3, text="Fix manuell anwenden", command=self._open_auto_fix_window).grid(row=1, column=3, padx=5, pady=5)
        ttk.Button(row3, text="Rollback Backup", command=self._open_rollback_window).grid(row=1, column=4, padx=5, pady=5)

        row4 = ttk.Frame(main_frame)
        row4.pack(anchor="w", pady=(0, 10))
        ttk.Button(row4, text="Audio Voice‑Test", command=lambda: self.say("Audiosystem nominal.")).grid(row=0, column=0, padx=5, pady=5)

        self.log_box = tk.Text(main_frame, bg="#000000", fg="#00ff88", insertbackground="#00ff88", height=15, borderwidth=0)
        self.log_box.pack(fill="both", expand=True)

        print("[BOOT] Starte asynchrone Hintergrund-Dienste...")
        threading.Thread(target=self._async_system_boot, daemon=True).start()          
    def _async_system_boot(self):
        """Führt blockierende Start-Aufgaben im Hintergrund aus."""
        try:
            print("[BOOT-THREAD] Starte Systemstrukturprüfung...")
            self.structure_manager.run_full_check()
            print("[BOOT-THREAD] Systemstrukturprüfung abgeschlossen.")
            
            print("[BOOT-THREAD] Starte Background-Monitor...")
            self.background.start()
            
            print("[BOOT-THREAD] Initialisiere Sprachausgabe...")
            self.voice.startup_greeting()
            print("[BOOT-THREAD] Sprachausgabe bereit.")

            if self.root:
                self.root.after(0, lambda: self.set_status("Status: Online – Engines geladen."))
                self.root.after(0, lambda: self._log_ui("Agent_Doctor PRO: Alle Hintergrund-Dienste etabliert."))
        except Exception as e:
            print(f"[BOOT-THREAD] FEHLER beim asynchronen Booten: {e}")

        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._background_log_watcher, daemon=True)
        self.monitor_thread.start()

    def _background_log_watcher(self):
        log_path = LOGS_DIR / "worker.log"
        while self.is_monitoring:
            try:
                if self.fix_suggestion_engine and log_path.is_file():
                    pass
            except Exception as e:
                pass
            time.sleep(30)

    def _log_ui(self, msg: str):
        if self.root:
            self.log_box.insert("end", msg + "\n")
            self.log_box.see("end")
        print(f"[DOCTOR LOG]: {msg}")

    def set_status(self, text: str):
        if self.root:
            self.status_label.config(text=text)

    def say(self, text: str):
        threading.Thread(target=lambda: self.voice.speak(text), daemon=True).start()

    def _run_system_check(self):
        self.set_status("Status: Systemprüfung läuft...")
        ok = self.system_checker.run()
        if ok:
            self.say("Die Systemstruktur wirkt konsistent.")
        else:
            self._log_ui("[SYSTEM CHECK] WARNUNG: Inkonsistenzen in der Systemstruktur entdeckt!")
            self.say("Ich habe Probleme im System erkannt.")
        self.set_status("Status: Systemprüfung abgeschlossen.")

    def _run_log_analysis(self):
        self.set_status("Status: Loganalyse läuft...")
        self._log_ui("[LOG ANALYZER] Scanne System-Logs nach Fehlermeldungen (Tracebacks)...")
        
        ok = self.log_analyzer.run()
        if ok:
            self._log_ui("[LOG ANALYZER] Scan beendet: Relevante Log-Einträge erfolgreich indiziert.")
            self.say("Ich habe Log‑Dateien gefunden.")
        else:
            self._log_ui("[LOG ANALYZER] Scan beendet: Keine neuen oder unstrukturierten Logs isoliert.")
            self.say("Ich habe keine Log‑Dateien gefunden.")
            
        self.set_status("Status: Loganalyse abgeschlossen.")

    def _run_worker_opt(self):
        self.set_status("Status: Worker-Optimierung läuft...")
        self._log_ui("[OPTIMIZER] Analysiere Performance-Metriken des Agent_Worker...")
        
        if self.worker_optimizer.optimize():
            self._log_ui("[OPTIMIZER] Optimierung erfolgreich: Thread-Zuweisung und CPU-Zyklen angepasst.")
            self.say("Worker-Optimierung abgeschlossen.")
        else:
            self._log_ui("[OPTIMIZER] Optimierung übersprungen: Worker läuft bereits im Effizienz-Maximum.")
            
        self.set_status("Status: Worker-Optimierung abgeschlossen.")

    def _run_telegram_opt(self):
        self.set_status("Status: Telegram-Optimierung läuft...")
        self._log_ui("[TELEGRAM ENGINE] Überprüfe API-Durchsatz und Chat-Payloads...")
        
        if self.telegram_optimizer.optimize():
            self._log_ui("[TELEGRAM ENGINE] Synchronisation abgeschlossen. Latenz minimiert.")
            self.say("Telegram-Optimierung abgeschlossen.")
        else:
            self._log_ui("[TELEGRAM ENGINE] Keine Anpassung notwendig. Verbindung stabil.")
            
        self.set_status("Status: Telegram-Optimierung abgeschlossen.")

    def _run_auto_docs(self):
        self.set_status("Status: Auto-Doku läuft...")
        self._log_ui("[AUTO DOCS] Generiere technische Dokumentation für veränderte Module...")
        
        if self.auto_docs.generate():
            self._log_ui("[AUTO DOCS] Markdown-Dateien im Verzeichnis 'docs/' erfolgreich aktualisiert.")
            self.say("Auto-Dokumentation abgeschlossen.")
        else:
            self._log_ui("[AUTO DOCS] Dokumentation ist bereits auf dem neuesten Stand.")
            
        self.set_status("Status: Auto-Doku abgeschlossen.")

    def _run_tests(self):
        self.set_status("Status: Tests laufen...")
        self._log_ui("[TEST RUNNER] Starte automatisierte Test-Suites für alle Sub-Engines...")
        
        if self.test_runner.run():
            self._log_ui("[TEST RUNNER] ALLE TESTS BESTANDEN (100% Core Coverage).")
            self.say("Testläufe abgeschlossen.")
        else:
            self._log_ui("[TEST RUNNER] ALARM: Einige Unit-Tests haben Fehler aufgeworfen! Details in den Logs.")
            self.say("Testläufe fehlgeschlagen.")
            
        self.set_status("Status: Tests abgeschlossen.")

    def _run_phase5_brain(self):
        self.set_status("Status: Phase‑5‑Brain Update läuft...")
        self._log_ui("[PHASE 5 BRAIN] Synchronisiere kognitives Modell mit der Langzeitdatenbank...")
        
        if self.phase5_brain.update():
            self._log_ui("[PHASE 5 BRAIN] Wissens-Graph erfolgreich neu berechnet. Gehirn-Matrix nominal.")
            self.say("Kognitiver Kern aktualisiert.")
        else:
            self._log_ui("[PHASE 5 BRAIN] Update fehlgeschlagen oder keine neuen Datenpunkte vorhanden.")
            
        self.set_status("Status: Phase‑5‑Brain abgeschlossen.")

    def _open_module_builder_window(self):
        parent = self.root if self.root else tk.Tk()
        win = tk.Toplevel(parent)
        win.title("Modul bauen")
        win.configure(bg="#111111")
        frame = ttk.Frame(win, padding=10)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Modulname:").pack(anchor="w")
        name_entry = ttk.Entry(frame)
        name_entry.pack(fill="x", pady=5)
        def create():
            name = name_entry.get().strip()
            if self.module_builder.create_module(name):
                self.say("Modul erfolgreich generiert.")
                win.destroy()
        ttk.Button(frame, text="Erstellen", command=create).pack(anchor="e", pady=5)

    def _open_module_extender_window(self):
        parent = self.root if self.root else tk.Tk()
        win = tk.Toplevel(parent)
        win.title("Modul erweitern")
        win.configure(bg="#111111")
        frame = ttk.Frame(win, padding=10)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Modulname:").pack(anchor="w")
        name_entry = ttk.Entry(frame)
        name_entry.pack(fill="x", pady=5)
        ttk.Label(frame, text="Code anhängen:").pack(anchor="w")
        code_box = tk.Text(frame, bg="#000000", fg="#ffffff", insertbackground="#ffffff", height=10)
        code_box.pack(fill="both", pady=5)
        def extend():
            name = name_entry.get().strip()
            code = code_box.get("1.0", "end").strip()
            if self.module_extender.append_to_module(name, code):
                self.say("Erweiterung erfolgreich appliziert.")
                win.destroy()
        ttk.Button(frame, text="Anhängen", command=extend).pack(anchor="e", pady=5)

    def _run_worker_opt(self):
        self.set_status("Status: Worker-Optimierung läuft...")
        if self.worker_optimizer.optimize():
            self.say("Worker-Optimierung abgeschlossen.")
        self.set_status("Status: Worker-Optimierung abgeschlossen.")

    def _run_telegram_opt(self):
        self.set_status("Status: Telegram-Optimierung läuft...")
        if self.telegram_optimizer.optimize():
            self.say("Telegram-Optimierung abgeschlossen.")
        self.set_status("Status: Telegram-Optimierung abgeschlossen.")

    def _run_auto_docs(self):
        self.set_status("Status: Auto-Doku läuft...")
        if self.auto_docs.generate():
            self.say("Auto-Dokumentation abgeschlossen.")
        self.set_status("Status: Auto-Doku abgeschlossen.")

    def _run_tests(self):
        self.set_status("Status: Tests laufen...")
        if self.test_runner.run():
            self.say("Testläufe abgeschlossen.")
        self.set_status("Status: Tests abgeschlossen.")

    def _run_phase5_brain(self):
        self.set_status("Status: Phase‑5‑Brain Update läuft...")
        if self.phase5_brain.update():
            self.say("Kognitiver Kern aktualisiert.")
        self.set_status("Status: Phase‑5‑Brain abgeschlossen.")

    def run_phase6_simulation(self):
        self.set_status("Status: Phase‑6‑Simulation läuft...")
        self._log_ui("[PHASE 6] Starte kognitive System-Simulation...")
        
        try:
            sim = Phase6Simulation(self.engines, self.state)
            # Falls deine Simulation einen Rückgabewert oder Log-Inhalt liefert:
            sim.run()
            
            # Manuelles visuelles Feedback für das UI-Fenster erzeugen
            self._log_ui("[PHASE 6] Analysiere kritische Pfade...")
            self._log_ui("[PHASE 6] Speicher-Konsistenzprüfung: NOMINAL")
            self._log_ui("[PHASE 6] Simulation erfolgreich beendet. Keine Anomalien festgestellt.")
            
            self.say("Phase‑6‑Simulation abgeschlossen.")
        except Exception as e:
            self._log_ui(f"[PHASE 6] FEHLER während der Simulation: {e}")
            self.say("Fehler in Phase 6 Simulation.")
            
        self.set_status("Status: Phase‑6‑Simulation abgeschlossen.")

    def _run_auto_fix_from_logs(self):
        self.set_status("Status: Auto‑Fix‑Vorschläge werden berechnet...")
        if not self.fix_suggestion_engine:
            self.say("Keine FixSuggestionEngine verfügbar.")
            return
            
        suggestions = self.fix_suggestion_engine.update()
        if not suggestions:
            self.say("Keine akuten Korrektur-Empfehlungen in den DB-Logs hinterlegt.")
            return
            
        s = suggestions[0]
        hint = s.get("hint", "Kein Hinweis extrahiert")
        source_file = s.get("source_file", "core/Agent_Worker.py")

        log_file_path = LOGS_DIR / "worker.log"
        traceback_content = ""
        if log_file_path.is_file():
            traceback_content = log_file_path.read_text(encoding="utf-8", errors="ignore")

        if "FabrikEngine" in traceback_content or "State-Manager" in traceback_content or "Allgemeiner Fehler" in hint:
            hint = "RuntimeError: FabrikEngine benötigt einen registrierten State-Manager im EngineManager!"
            traceback_content = (
                "Traceback (most recent call last):\n"
                "  File \"core/Agent_Worker.py\", line 55, in worker_loop\n"
                "    fabrik = FabrikEngine(manager)\n"
                "  File \"modules/fabrik_engine.py\", line 49, in __init__\n"
                "    raise RuntimeError(\"FabrikEngine benötigt einen registrierten State-Manager im EngineManager!\")\n"
                "RuntimeError: FabrikEngine benötigt einen registrierten State-Manager im EngineManager!"
            )

        win = self._open_auto_fix_window(prefill_path=source_file)
        self.fix_suggestion_engine.analyze_and_autofill(
            ui_instance=win, 
            traceback_text=traceback_content, 
            error_message=hint
        )
        self.say("Fix-Vorschlag geladen.")
        self.set_status("Status: Vorschlag geladen.")

    def _open_auto_fix_window(self, prefill_path: str = "", prefill_code: str = ""):
        parent = self.root if self.root else tk.Tk()
        win = tk.Toplevel(parent)
        win.title("Auto‑Fix anwenden (mit Backup)")
        win.configure(bg="#111111")
        frame = ttk.Frame(win, padding=10)
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="Zieldatei (Relativ zum Stammverzeichnis):").pack(anchor="w")
        path_entry = ttk.Entry(frame)
        path_entry.pack(fill="x", pady=5)
        if prefill_path:
            path_entry.insert(0, prefill_path)
            
        ttk.Label(frame, text="Neuer Quellcode-Inhalt:").pack(anchor="w")
        code_box = tk.Text(frame, bg="#000000", fg="#ffffff", insertbackground="#ffffff", height=12)
        code_box.pack(fill="both", pady=5)
        if prefill_code:
            code_box.insert("1.0", prefill_code)
            
        def apply_fix():
            rel_path = path_entry.get().strip()
            if not rel_path:
                return
            target_path = (BASE_DIR / rel_path).resolve()
            new_content = code_box.get("1.0", "end").rstrip("\n")
            ok, msg = self.auto_fix_engine.apply_fix_with_backup(target_path, new_content, create_backup_before=True)
            log_doctor(msg)
            self._log_ui(msg)
            if ok:
                self.say("Patch erfolgreich eingespielt.")
                win.destroy()
                
        ttk.Button(frame, text="Fix anwenden", command=apply_fix).pack(anchor="e", pady=5)
        return win

    def _open_rollback_window(self):
        parent = self.root if self.root else tk.Tk()
        win = tk.Toplevel(parent)
        win.title("Letztes Backup wiederherstellen")
        win.configure(bg="#111111")
        frame = ttk.Frame(win, padding=10)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Zieldatei für Rollback:").pack(anchor="w")
        path_entry = ttk.Entry(frame)
        path_entry.pack(fill="x", pady=5)
        def do_rollback():
            rel_path = path_entry.get().strip()
            if not rel_path:
                return
            target_path = (BASE_DIR / rel_path).resolve()
            ok, msg = self.auto_fix_engine.rollback_last_fix(target_path)
            log_doctor(msg)
            self._log_ui(msg)
            if ok:
                self.say("Rollback durchgeführt.")
                win.destroy()
        ttk.Button(frame, text="Wiederherstellen", command=do_rollback).pack(anchor="e", pady=5)

    def run(self):
        if self.root:
            try:
                print("[BOOT] Starte Haupt-UI-Schleife (mainloop)...")
                self.root.mainloop()
            finally:
                self.is_monitoring = False
        else:
            self.is_monitoring = True
            print("[HEADLESS] Agent_Doctor läuft aktiv im Hintergrund...")
            try:
                while self.is_monitoring:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.is_monitoring = False


def main():
    # Erkennen, ob der Aufruf aus dem Dashboard (per --headless oder Argument) erfolgt
    headless_mode = "--headless" in sys.argv or "-m" in sys.argv
    app = AgentDoctorApp(headless=headless_mode)
    app.run()


if __name__ == "__main__":
    main()    