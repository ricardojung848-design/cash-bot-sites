import os
import sys
import threading
import time
import tkinter as tk
from pathlib import Path

# CustomTkinter für Hardware-beschleunigtes Sci-Fi Rendering laden
try:
    import customtkinter as ctk
except ImportError:
    import os
    os.system('pip install customtkinter')
    import customtkinter as ctk

# Stammverzeichnis absichern (Schaut eine Ebene höher, da Datei im modules-Ordner liegt)
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# =====================================================================
# INTEGRATION DEINER ECHTEN CORE-ENGINES
# =====================================================================
from doctor_core.engine_manager import EngineManager
from doctor_core.state import DoctorState
from doctor_core.system_check import SystemChecker
from doctor_core.log_analysis import LogAnalyzer
from doctor_core.auto_fix_engine import AutoFixEngine
from doctor_core.background import BackgroundMonitor

try:
    from modules.engines.engine_fix_suggestions import FixSuggestionEngine
except ImportError:
    from modules.module_fix_suggestions import FixSuggestionEngine

LOGS_DIR = BASE_DIR / "logs"

class AegisControlCenter(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- CORE LOGIK INITIALISIERUNG ---
        try:
            self.state = DoctorState()
        except Exception:
            self.state = None
        
        self.engines = EngineManager()
        if self.state:
            self.engines.register("state", self.state)

        # Sub-Engines instanziieren
        self.system_checker = SystemChecker()
        self.log_analyzer = LogAnalyzer()
        self.auto_fix_engine = AutoFixEngine(engine_manager=self.engines)
        self.background = BackgroundMonitor(engine_manager=self.engines)

        if FixSuggestionEngine:
            self.fix_suggestion_engine = FixSuggestionEngine(self.engines)
            self.engines.register("fix", self.fix_suggestion_engine)
        else:
            self.fix_suggestion_engine = None

        # --- UI DESIGN SYSTEM SETUP (Aegis-Rot) ---
        self.title("AEGIS // QUANTUM INTELLIGENCE CONTROL CENTER")
        self.geometry("1200x780")  # Syntax-Fehler behoben (:// zu x)
        self.configure(fg_color="#040406") # Weltraum-Tiefschwarz
        ctk.set_appearance_mode("dark")
        
        self.color_neon_red = "#ff2a2a"
        self.color_glass_bg = "#120404"
        self.color_border_glow = "#630b0b"

        # --- INTERFACE-STRUKTUR ---
        self._create_header()
        self._create_bento_grid()
        
        # --- ASYNCHRONE AGENTEN-THREADS ---
        self.is_monitoring = True
        threading.Thread(target=self._async_core_boot, daemon=True).start()
        threading.Thread(target=self._live_log_streamer, daemon=True).start()
        threading.Thread(target=self._init_global_shortcuts, daemon=True).start()

    def _create_header(self):
        """Erstellt die obere Kontroll-Leiste im Sci-Fi Look"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 0))

        title = ctk.CTkLabel(
            header_frame, 
            text="▲ AEGIS // COGNITIVE COMMAND SYSTEM v2050", 
            font=("Consolas", 15, "bold"), 
            text_color=self.color_neon_red
        )
        title.pack(side="left")

        self.status_led = ctk.CTkLabel(
            header_frame, 
            text="● CORE MATRIX: CONNECTING...", 
            font=("Consolas", 11, "bold"), 
            text_color="#ffaa00"
        )
        self.status_led.pack(side="right")

    def _create_bento_grid(self):
        """Baut das funktionale Bento-Box-Grid aus schwebenden Glas-Modulen"""
        grid_container = ctk.CTkFrame(self, fg_color="transparent")
        grid_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        grid_container.grid_columnconfigure((0, 1, 2), weight=1, uniform="equal")
        grid_container.grid_rowconfigure(0, weight=4)
        grid_container.grid_rowconfigure(1, weight=5)

        # Modul 1: Agenten-Status-Zentrale
        mod_agents = ctk.CTkFrame(grid_container, fg_color=self.color_glass_bg, border_color=self.color_border_glow, border_width=1, corner_radius=12)
        mod_agents.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        self._add_module_title(mod_agents, "📡 AGENT REGISTRY & STATE")
        
        self.registry_labels = {}
        engines_list = ["DoctorState DB", "EngineManager", "BackgroundMonitor", "AutoFixEngine"]
        for i, eng in enumerate(engines_list):
            f = ctk.CTkFrame(mod_agents, fg_color="transparent")
            f.pack(fill="x", padx=15, pady=2)
            ctk.CTkLabel(f, text=f"• {eng}", font=("Consolas", 11)).pack(side="left")
            status_lbl = ctk.CTkLabel(f, text="OFFLINE", font=("Consolas", 11, "bold"), text_color="#ff5555")
            status_lbl.pack(side="right")
            self.registry_labels[eng] = status_lbl

        # Modul 2: Das KI-Auge Controls
        mod_eye = ctk.CTkFrame(grid_container, fg_color=self.color_glass_bg, border_color=self.color_border_glow, border_width=1, corner_radius=12)
        mod_eye.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        self._add_module_title(mod_eye, "👁️ OPERATIONS COMMANDS")
        
        ctk.CTkButton(mod_eye, text="⚡ SYSTEM CHECK", fg_color="#200505", border_color=self.color_border_glow, border_width=1, text_color="#ffffff", hover_color="#400a0a", command=self._cmd_system_check).pack(fill="x", padx=15, pady=4)
        ctk.CTkButton(mod_eye, text="📊 LOGS ANALYSIEREN", fg_color="#200505", border_color=self.color_border_glow, border_width=1, text_color="#ffffff", hover_color="#400a0a", command=self._cmd_analyze_logs).pack(fill="x", padx=15, pady=4)

        # Modul 3: Vektor-Speicher / KI-Heilung-Phasen
        mod_vector = ctk.CTkFrame(grid_container, fg_color=self.color_glass_bg, border_color=self.color_border_glow, border_width=1, corner_radius=12)
        mod_vector.grid(row=0, column=2, padx=8, pady=8, sticky="nsew")
        self._add_module_title(mod_vector, "🧠 RECOVERY PIPELINE")
        
        ctk.CTkButton(mod_vector, text="🔥 AUTO-FIX EINSTEUERN (P7)", fg_color="#300505", border_color=self.color_neon_red, border_width=1, text_color=self.color_neon_red, hover_color="#500a0a", font=("Consolas", 11, "bold"), command=self._cmd_trigger_autofix).pack(fill="x", padx=15, pady=8)

        # Modul 4: Live-Denk-Log (Matrix Telemetrie)
        mod_log = ctk.CTkFrame(grid_container, fg_color=self.color_glass_bg, border_color=self.color_border_glow, border_width=1, corner_radius=12)
        mod_log.grid(row=1, column=0, columnspan=3, padx=8, pady=8, sticky="nsew")
        self._add_module_title(mod_log, "⚡ REALTIME COGNITIVE TELEMETRY FLOW")
        
        self.log_box = tk.Text(mod_log, bg="#080101", fg=self.color_neon_red, insertbackground=self.color_neon_red, font=("Consolas", 10), bd=0, highlightthickness=0, padding=10)
        self.log_box.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.log_box.insert("end", "[AEGIS-BOOT] Signalmatrix aufgebaut. Warte auf Core-Stream...\n")

    def _add_module_title(self, frame, text):
        lbl = ctk.CTkLabel(frame, text=text, font=("Consolas", 11, "bold"), text_color="#aaaaaa")
        lbl.pack(anchor="w", padx=15, pady=10)

    # --- ACTIONS & OPERATIONS ---
    def _async_core_boot(self):
        """Bootet die Hintergrund-Dienste und schaltet LEDs auf Grün"""
        try:
            self.background.start()
            time.sleep(0.5)
            self.after(0, lambda: self.status_led.configure(text="● CORE MATRIX: NOMINAL", text_color="#00ffaa"))
            for eng in self.registry_labels:
                self.after(0, lambda e=eng: self.registry_labels[e].configure(text="NOMINAL", text_color="#00ffaa"))
            self._log_ui("[OK] Alle kognitiven Sub-Engines erfolgreich gebunden.")
        except Exception as err:
            self._log_ui(f"[CRITICAL] Fehler beim Core-Boot: {err}")

    def _live_log_streamer(self):
        """Liest live das worker.log aus und pumpt es in den Matrix-Stream"""
        log_path = LOGS_DIR / "worker.log"
        last_size = 0
        while self.is_monitoring:
            if log_path.is_file():
                current_size = log_path.stat().st_size
                if current_size < last_size: # Log wurde rotiert/geleert
                    last_size = 0
                if current_size > last_size:
                    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                        f.seek(last_size)
                        new_lines = f.read()
                        if new_lines:
                            self._log_ui(new_lines.strip())
                    last_size = current_size
            time.sleep(1.0)

    def _log_ui(self, msg: str):
        if msg:
            self.log_box.insert("end", f"[{time.strftime('%H:%M:%S')}] {msg}\n")
            self.log_box.see("end")

    def _cmd_system_check(self):
        self._log_ui("[CMD] Starte Systemstrukturprüfung...")
        if self.system_checker.run():
            self._log_ui("[INFO] SystemChecker: Datenstrukturen konsistent.")

    def _cmd_analyze_logs(self):
        self._log_ui("[CMD] Analysiere Log-Dateien...")
        if self.log_analyzer.run():
            self._log_ui("[INFO] LogAnalyzer: Analyse abgeschlossen.")

    def _cmd_trigger_autofix(self):
        self._log_ui("[HEAL] Berechne Auto-Fix Muster für core/Agent_Worker.py...")
        hint = "RuntimeError: FabrikEngine benötigt einen registrierten State-Manager im EngineManager!"
        traceback_content = (
            "Traceback (most recent call last):\n"
            "  File \"core/Agent_Worker.py\", line 15, in worker_loop\n"
            "    from modules.engines.engine_fabrik import FabrikEngine\n"
            "ModuleNotFoundError: No module named 'modules.engines.engine_fabrik'"
        )
        win = tk.Toplevel(self)
        win.title("Aegis Auto-Fix Injektor")
        win.configure(bg=self.color_glass_bg)
        
        tk.Label(win, text="Zieldatei:", bg=self.color_glass_bg, fg="#ffffff").pack(anchor="w", padx=10, pady=2)
        ent = tk.Entry(win, bg="#000000", fg="#ffffff", bd=1)
        ent.pack(fill="x", padx=10, pady=2)
        ent.insert(0, "core/Agent_Worker.py")
        
        txt = tk.Text(win, bg="#000000", fg="#ffffff", height=12)
        txt.pack(fill="both", expand=True, padx=10, pady=5)
        
        if self.fix_suggestion_engine:
            self.fix_suggestion_engine.analyze_and_autofill(win, traceback_content, hint)
        
        def do_inject():
            target = (BASE_DIR / ent.get().strip()).resolve()
            ok, msg = self.auto_fix_engine.apply_fix_with_backup(target, txt.get("1.0", "end").rstrip("\n"), True)
            self._log_ui(msg)
            if ok: win.destroy()
            
        tk.Button(win, text="INJEKTION AUSFÜHREN", bg="#400505", fg=self.color_neon_red, command=do_inject).pack(pady=5)

    # --- SPOTLIGHT OVERLAY SHORTCUT (Strg + Leertaste) ---
    def _init_global_shortcuts(self):
        try:
            import keyboard
            keyboard.add_hotkey("ctrl+space", lambda: self.after(0, self._show_spotlight))
        except ImportError:
            import os
            os.system('pip install keyboard')

    def _show_spotlight(self):
        spotlight = tk.Toplevel(self)
        spotlight.overrideredirect(True)
        spotlight.attributes("-topmost", True)
        
        w, h = 600, 50
        x = (spotlight.winfo_screenwidth() - w) // 2
        y = (spotlight.winfo_screenheight() - h) // 3
        spotlight.geometry(f"{w}x{h}+{x}+{y}")
        
        glow = tk.Frame(spotlight, bg=self.color_neon_red, bd=1)
        glow.pack(fill="both", expand=True)
        
        entry = tk.Entry(glow, bg="#0a0202", fg="#ffffff", insertbackground=self.color_neon_red, font=("Consolas", 12), bd=0, justify="center")
        entry.pack(fill="both", expand=True, padx=2, pady=2)
        entry.focus_set()
        
        spotlight.bind("<Escape>", lambda e: spotlight.destroy())
        entry.bind("<Return>", lambda e: [self._log_ui(f"[CMD-OVERLAY] {entry.get()}"), spotlight.destroy()])

if __name__ == "__main__":
    app = AegisControlCenter()
    app.mainloop()  # Fehler behoben (.run() zu .mainloop())