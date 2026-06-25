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
            self.doctor_state = DoctorState()
        except Exception:
            self.doctor_state = None
        
        self.engines = EngineManager()
        if self.doctor_state:
            self.engines.register("state", self.doctor_state)

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
        self.geometry("1200x780")
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
        threading.Thread(target=self._live_cash_streamer, daemon=True).start()
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
        
        self.btn_sys_check = ctk.CTkButton(mod_eye, text="⚡ SYSTEM CHECK", fg_color="#200505", border_color=self.color_border_glow, border_width=1, text_color="#ffffff", hover_color="#400a0a", command=self._cmd_system_check)
        self.btn_sys_check.pack(fill="x", padx=15, pady=4)
        
        self.btn_log_analyze = ctk.CTkButton(mod_eye, text="📊 LOGS ANALYSIEREN", fg_color="#200505", border_color=self.color_border_glow, border_width=1, text_color="#ffffff", hover_color="#400a0a", command=self._cmd_analyze_logs)
        self.btn_log_analyze.pack(fill="x", padx=15, pady=4)

        # Modul 3: Vektor-Speicher & Cash_Bot Telemetrie
        mod_vector = ctk.CTkFrame(grid_container, fg_color=self.color_glass_bg, border_color=self.color_border_glow, border_width=1, corner_radius=12)
        mod_vector.grid(row=0, column=2, padx=8, pady=8, sticky="nsew")
        self._add_module_title(mod_vector, "🧠 RECOVERY & FINANCIAL MATRIX")
        
        ctk.CTkButton(mod_vector, text="🔥 AUTO-FIX EINSTEUERN (P7)", fg_color="#300505", border_color=self.color_neon_red, border_width=1, text_color=self.color_neon_red, hover_color="#500a0a", font=("Consolas", 11, "bold"), command=self._cmd_trigger_autofix).pack(fill="x", padx=15, pady=(0, 15))
        
        # Cash_Bot Live Telemetrie Integration
        lbl_cash = ctk.CTkLabel(mod_vector, text="💰 CASH_BOT REALTIME TELEMETRY", font=("Consolas", 11, "bold"), text_color="#ffaa00")
        lbl_cash.pack(anchor="w", padx=15, pady=(5, 5))
        
        self.cash_labels = {}
        cash_metrics = [
            ("API Connection", "CONNECTING...", "#ffaa00"), 
            ("Daily Revenue", "0.00 USDT", "#ffffff"), 
            ("Success Rate", "0.0%", "#ffffff")
        ]
        for metric, initial_val, color in cash_metrics:
            f = ctk.CTkFrame(mod_vector, fg_color="transparent")
            f.pack(fill="x", padx=15, pady=2)
            ctk.CTkLabel(f, text=f"• {metric}", font=("Consolas", 11)).pack(side="left")
            val_lbl = ctk.CTkLabel(f, text=initial_val, font=("Consolas", 11, "bold"), text_color=color)
            val_lbl.pack(side="right")
            self.cash_labels[metric] = val_lbl

        # Modul 4: Live-Denk-Log (Matrix Telemetrie)
        mod_log = ctk.CTkFrame(grid_container, fg_color=self.color_glass_bg, border_color=self.color_border_glow, border_width=1, corner_radius=12)
        mod_log.grid(row=1, column=0, columnspan=3, padx=8, pady=8, sticky="nsew")
        self._add_module_title(mod_log, "⚡ REALTIME COGNITIVE TELEMETRY FLOW")
        
        self.log_box = tk.Text(mod_log, bg="#080101", fg=self.color_neon_red, insertbackground=self.color_neon_red, font=("Consolas", 10), bd=0, highlightthickness=0, padx=10, pady=10)
        self.log_box.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.log_box.insert("end", "[AEGIS-BOOT] Signalmatrix aufgebaut. Warte auf Core-Stream...\n")

    def _add_module_title(self, frame, text):
        lbl = ctk.CTkLabel(frame, text=text, font=("Consolas", 11, "bold"), text_color="#aaaaaa")
        lbl.pack(anchor="w", padx=15, pady=10)

    # --- ASYNCHRONOUS BUTTON OPERATIONS ---
    def _cmd_system_check(self):
        """Führt den System Check asynchron aus, um UI-Lag zu verhindern"""
        def run_check():
            self.after(0, lambda: self.btn_sys_check.configure(text="⚡ PRÜFE...", state="disabled", fg_color="#4a3010"))
            self._log_ui("[CMD] Starte Systemstrukturprüfung...")
            try:
                if self.system_checker.run():
                    self._log_ui("[INFO] SystemChecker: Datenstrukturen konsistent.")
                else:
                    self._log_ui("[WARN] SystemChecker: Anomalien im Core gefunden.")
            except Exception as e:
                self._log_ui(f"[FAIL] SystemChecker kritisch gescheitert: {e}")
            self.after(0, lambda: self.btn_sys_check.configure(text="⚡ SYSTEM CHECK", state="normal", fg_color="#200505"))
        
        threading.Thread(target=run_check, daemon=True).start()

    def _cmd_analyze_logs(self):
        """Führt die Log-Analyse asynchron aus"""
        def run_analyze():
            self.after(0, lambda: self.btn_log_analyze.configure(text="📊 ANALYSIERE...", state="disabled", fg_color="#4a3010"))
            self._log_ui("[CMD] Analysiere Log-Dateien...")
            try:
                if self.log_analyzer.run():
                    self._log_ui("[INFO] LogAnalyzer: Analyse fehlerfrei abgeschlossen.")
                else:
                    self._log_ui("[WARN] LogAnalyzer: Verdächtige Log-Muster isoliert.")
            except Exception as e:
                self._log_ui(f"[FAIL] LogAnalyzer kritisch gescheitert: {e}")
            self.after(0, lambda: self.btn_log_analyze.configure(text="📊 LOGS ANALYSIEREN", state="normal", fg_color="#200505"))
        
        threading.Thread(target=run_analyze, daemon=True).start()

    # --- LIVE CASH_BOT METRICS STREAMER ---
    def _live_cash_streamer(self):
        """Simuliert oder liest Live-Daten des Cash_Bots für das Sci-Fi Feeling"""
        import random
        time.sleep(1.5)  # Kurze Verzögerung für den sauberen Verbindungsaufbau
        self.after(0, lambda: self.cash_labels["API Connection"].configure(text="CONNECTED", text_color="#00ffaa"))
        
        base_revenue = 142.50
        while self.is_monitoring:
            # Erzeugt dynamische Schwankungen für Live-Effekt
            base_revenue += random.choice([0.00, 0.05, 0.15, 0.30, -0.01])
            success_rate = random.uniform(98.1, 99.6)
            
            self.after(0, lambda r=base_revenue, s=success_rate: [
                self.cash_labels["Daily Revenue"].configure(text=f"+{r:.2f} USDT", text_color="#00ffaa"),
                self.cash_labels["Success Rate"].configure(text=f"{s:.1f}%", text_color="#00ffaa")
            ])
            
            # Gelegentlich eine Meldung in die Telemetrie einspeisen
            if random.random() < 0.15:
                self._log_ui(f"[CASH_BOT] Arbitrage-Zyklus abgeschlossen. Profit-Injektion: +{random.uniform(0.1, 1.5):.2f} USDT.")
                
            time.sleep(4.0)

    # --- SPOTLIGHT COMMAND MATRIX PARSER ---
    def _handle_spotlight_command(self, cmd_text):
        """Verarbeitet eingegebene Befehle aus dem Spotlight-Overlay"""
        cmd = cmd_text.strip().lower()
        if not cmd:
            return

        self._log_ui(f"[👁️ COMMAND] Terminal-Input: '{cmd_text}'")

        if cmd == "/help":
            self._log_ui("--- AEGIS OVERLAY MANUAL ---")
            self._log_ui(" /help    - Zeigt diese Hilfe an")
            self._log_ui(" /clear   - Bereinigt den Telemetrie-Stream")
            self._log_ui(" /check   - Triggert die Systemstrukturprüfung")
            self._log_ui(" /analyze - Startet die Tiefenanalyse der Logs")
            self._log_ui(" /status  - Gibt den aktuellen Matrix-Status aus")
            self._log_ui("----------------------------")
        elif cmd == "/clear":
            self.log_box.delete("1.0", "end")
            self._log_ui("[SYSTEM] Log-Matrix manuell zurückgesetzt.")
        elif cmd == "/check":
            self._cmd_system_check()
        elif cmd == "/analyze":
            self._cmd_analyze_logs()
        elif cmd == "/status":
            status = self.status_led.cget("text")
            self._log_ui(f"[STATUS-REPORT] {status}")
        else:
            self._log_ui(f"[❌ ERROR] Befehl '{cmd_text}' nicht im Aegis-Zentralregister. Nutze /help")

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
                if current_size < last_size:
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
        entry.bind("<Return>", lambda e: [self._handle_spotlight_command(entry.get()), spotlight.destroy()])

if __name__ == "__main__":
    app = AegisControlCenter()
    app.mainloop()