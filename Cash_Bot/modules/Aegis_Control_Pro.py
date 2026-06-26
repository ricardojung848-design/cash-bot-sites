import os
import sys

# Windows global zwingen, Python im UTF-8 Modus auszuführen
os.environ["PYTHONUTF8"] = "1"

import json
import threading
import tkinter as tk
import tkinter.ttk as ttk
from pathlib import Path

try:
    import customtkinter as ctk
except ImportError:
    os.system('pip install customtkinter')
    import customtkinter as ctk

# Stammverzeichnis absichern
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from doctor_core.engine_manager import EngineManager
from doctor_core.state import DoctorState
from doctor_core.process_manager import AgentProcessManager
from doctor_core.aegis_storage import AegisStorage
from doctor_core.dialog_engine import AegisDialogEngine
from modules.Agent_Scout import AgentScout

LAYOUT_FILE = BASE_DIR / "config" / "layout.json"
REGISTRY_FILE = BASE_DIR / "config" / "registry.json"

class AegisOSDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. Core Engines & Zustands-Flags initialisieren
        self.doctor_state = DoctorState()
        self.engines = EngineManager()
        self.engines.register("state", self.doctor_state)
        
        self.pm = AgentProcessManager(self.engines)
        self.storage = AegisStorage()
        self.dialog_engine = AegisDialogEngine(self.engines)
        self.scout_worker = AgentScout(self.engines, ui_instance=self)

        # Internes Tracking für asynchrone Worker (Verhindert LED-Aussetzer bei Ansichtswechseln)
        self.scout_active_flag = False

        # 2. Fenster-Konfiguration
        self.title("Aegis OS // COGNITIVE COMMAND SYSTEM")
        self.geometry("1300x800")
        self.configure(fg_color="#08080c")
        ctk.set_appearance_mode("dark")

        # 3. Apps registrieren & Layout laden
        self.apps = self._load_apps_registry()
        self.app_positions = self._load_layout()

        # Drag & Drop Hilfsvariablen
        self.selected_app_key = None

        # 4. UI Layout aufbauen (Split Screen)
        self._build_main_layout()
        self._render_app_grid()
        
        # Standardansicht rechts laden
        self._open_app_view("AI Voice Chat")
        
        # Status-Schleife für Live-LEDs starten
        self._update_loop()

    def _load_apps_registry(self):
        """Lädt die Liste aller installierten Apps/Agenten basierend auf deiner Struktur"""
        default_registry = {
            "Agent Worker": {"path": "core/Agent_Worker.py", "type": "agent"},
            "Agent Doctor": {"path": "modules/Agent_Doctor.py", "type": "agent"},
            "Agent Scout": {"path": "modules/Agent_Scout.py", "type": "agent"},
            "Agent Wallet": {"path": "modules/Agent_Wallet.py", "type": "agent"},
            "AI Voice Chat": {"path": "doctor_core/dialog_engine.py", "type": "system"},
            "Task Manager": {"path": "doctor_core/aegis_storage.py", "type": "system"}
        }

        if not REGISTRY_FILE.exists():
            os.makedirs(REGISTRY_FILE.parent, exist_ok=True)
            with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
                json.dump(default_registry, f, indent=4)
            return default_registry

        with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
            registry = json.load(f)

        updated = False
        for app_name, app_data in default_registry.items():
            if app_name not in registry:
                registry[app_name] = app_data
                updated = True

        if updated:
            with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
                json.dump(registry, f, indent=4)

        return registry

    def _load_layout(self):
        """Lädt oder generiert die Grid-Anordnung der Kacheln"""
        if LAYOUT_FILE.exists():
            with open(LAYOUT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        
        positions = {}
        for i, app_name in enumerate(self.apps.keys()):
            row = i // 2
            col = i % 2
            positions[app_name] = [row, col]
        return positions

    def _save_layout(self):
        """Speichert die Kachel-Positionen permanent"""
        os.makedirs(LAYOUT_FILE.parent, exist_ok=True)
        with open(LAYOUT_FILE, "w", encoding="utf-8") as f:
            json.dump(self.app_positions, f, indent=4)

    def _start_scout_jagd(self):
        """Aktiviert die Scout-Steuerung und übergibt das GUI-Update als sicheren Callback"""
        self.scout_active_flag = True
        if "Agent Scout" in self.tiles:
            self.tiles["Agent Scout"]["led"].configure(text_color="#00ffaa")
        
        # Leere die Tabelle vor dem neuen Lauf
        if hasattr(self, "treffer_tabelle"):
            for item in self.treffer_tabelle.get_children():
                self.treffer_tabelle.delete(item)
        
        # Wir übergeben eine Lambda-Funktion, die das Update absolut Thread-sicher über .after() einreiht
        def jagd_finished_callback(treffer_liste):
            self.after(0, lambda: self.update_treffer_tabelle(treffer_liste))
            self.scout_active_flag = False
        
        # Thread starten und den Callback mitgeben
        threading.Thread(
            target=self.scout_worker.scout_jagd_starten, 
            kwargs={"callback": jagd_finished_callback}, 
            daemon=True
        ).start()
    def _build_main_layout(self):
        """Erstellt die iPhone-Splitscreen-Struktur"""
        header = ctk.CTkFrame(self, fg_color="transparent", height=40)
        header.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(header, text="📱 Aegis OS v2.0", font=("Consolas", 16, "bold")).pack(side="left")
        self.lbl_global_status = ctk.CTkLabel(header, text="SYSTEM NOMINAL", text_color="#00ffaa", font=("Consolas", 12, "bold"))
        self.lbl_global_status.pack(side="right")

        btn_kill = ctk.CTkButton(header, text="🛑 ALL KILL", fg_color="#401010", hover_color="#601010", width=80, command=self._global_kill)
        btn_kill.pack(side="right", padx=20)

        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        self.left_screen = ctk.CTkScrollableFrame(main_container, width=400, fg_color="#121216", border_width=1, border_color="#22222a")
        self.left_screen.pack(side="left", fill="both", expand=False, padx=5)
        
        self.right_screen = ctk.CTkFrame(main_container, fg_color="#181820", border_width=1, border_color="#22222a")
        self.right_screen.pack(side="right", fill="both", expand=True, padx=5)

    def _render_app_grid(self):
        """Baut das Grid basierend auf den Layout-Koordinaten auf"""
        for widget in self.left_screen.winfo_children():
            widget.destroy()

        self.left_screen.grid_columnconfigure((0, 1), weight=1, minsize=180)

        self.tiles = {}
        for app_name, pos in self.app_positions.items():
            row, col = pos[0], pos[1]
            
            tile = ctk.CTkFrame(self.left_screen, fg_color="#22222e", border_width=1, border_color="#333344", height=120)
            tile.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            tile.grid_propagate(False)

            tile.bind("<Button-1>", lambda event, name=app_name: self._open_app_view(name))
            tile.bind("<Button-3>", lambda event, name=app_name: self._select_for_move(name))

            led = ctk.CTkLabel(tile, text="●", text_color="#ff5555", font=("Consolas", 14))
            led.place(x=15, y=10)

            lbl_name = ctk.CTkLabel(tile, text=app_name, font=("Consolas", 13, "bold"))
            lbl_name.place(x=35, y=8)
            
            lbl_name.bind("<Button-1>", lambda event, name=app_name: self._open_app_view(name))
            led.bind("<Button-1>", lambda event, name=app_name: self._open_app_view(name))

            self.tiles[app_name] = {"frame": tile, "led": led}

    def _select_for_move(self, app_name):
        """Auswahl einer Kachel für das Verschieben (Drag-Simulation)"""
        if self.selected_app_key is None:
            self.selected_app_key = app_name
            self.tiles[app_name]["frame"].configure(border_color="#ffaa00", border_width=2)
            self.lbl_global_status.configure(text=f"Verschiebe Modus: Klicke jetzt Rechts auf die Zielposition!", text_color="#ffaa00")
        else:
            target_pos = self.app_positions[app_name].copy()
            source_pos = self.app_positions[self.selected_app_key].copy()
            
            self.app_positions[self.selected_app_key] = target_pos
            self.app_positions[app_name] = source_pos
            
            self._save_layout()
            self.selected_app_key = None
            self.lbl_global_status.configure(text="SYSTEM NOMINAL", text_color="#00ffaa")
            self._render_app_grid()

    def _open_app_view(self, app_name):
        """Rendert die App-Inhalte dynamisch auf der rechten Großfläche"""
        for widget in self.right_screen.winfo_children():
            widget.destroy()

        title_frame = ctk.CTkFrame(self.right_screen, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(title_frame, text=f"📂 APP // {app_name.upper()}", font=("Consolas", 16, "bold")).pack(side="left")

        if app_name == "AI Voice Chat":
            self._build_voice_app_view()
        elif app_name == "Task Manager":
            self._build_task_app_view()
        else:
            self._build_agent_app_view(app_name)

    def _build_voice_app_view(self):
        """Die Chat-Oberfläche für deine KI-Unterhaltungen mit farblicher Trennung"""
        container = ctk.CTkFrame(self.right_screen, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=5)

        # Chat-Historie als Text-Widget
        self.chat_history = tk.Text(container, bg="#0d0d11", fg="#ffffff", font=("Consolas", 11), bd=0, highlightthickness=0)
        self.chat_history.pack(fill="both", expand=True, pady=(0, 10))
        
        # Farb-Tags für die Historie definieren
        self.chat_history.tag_config("user_tag", foreground="#88aaee", font=("Consolas", 11, "bold"))
        self.chat_history.tag_config("aegis_tag", foreground="#00ffaa", font=("Consolas", 11, "bold"))
        self.chat_history.tag_config("system_tag", foreground="#7777aa", font=("Consolas", 10, "italic"))

        self.chat_history.insert("end", "Aegis OS Dialogue System bereit. Sprechen oder schreiben Sie einen Befehl...\n\n", "system_tag")

        input_frame = ctk.CTkFrame(container, fg_color="transparent")
        input_frame.pack(fill="x")

        entry_cmd = ctk.CTkEntry(input_frame, placeholder_text="Z.B.: 'starte Worker'...", font=("Consolas", 12))
        entry_cmd.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        def send_voice_cmd():
            text = entry_cmd.get().strip()
            if text:
                # Benutzereingabe farbig einfügen
                self.chat_history.insert("end", "👤 DU: ", "user_tag")
                self.chat_history.insert("end", f"{text}\n")
                
                if text.lower().startswith("starte "):
                    target_agent = text[7:].strip().lower()
                    found_app_name = None
                    for app_name in self.apps.keys():
                        if target_agent in app_name.lower():
                            found_app_name = app_name
                            break
                    
                    if found_app_name:
                        script_path = self.apps[found_app_name]["path"]
                        res = self.pm.start_agent(found_app_name, script_path)
                        if res == "SUCCESS":
                            self.chat_history.insert("end", f"🤖 AEGIS: [{found_app_name}] wurde erfolgreich gestartet!\n\n", "aegis_tag")
                        else:
                            self.chat_history.insert("end", f"🤖 AEGIS: Startfehler -> {res}\n\n", "system_tag")
                    else:
                        self.chat_history.insert("end", f"🤖 AEGIS: Agent '{target_agent}' wurde nicht gefunden.\n\n", "system_tag")
                else:
                    reply = self.dialog_engine.process_command(text)
                    # Aegis-Antwort farbig einfügen
                    self.chat_history.insert("end", "🤖 AEGIS: ", "aegis_tag")
                    self.chat_history.insert("end", f"{reply}\n\n")
                
                self.chat_history.see("end")
                entry_cmd.delete(0, "end")

        btn_send = ctk.CTkButton(input_frame, text="Senden 🚀", width=80, command=send_voice_cmd)
        btn_send.pack(side="right")
        entry_cmd.bind("<Return>", lambda e: send_voice_cmd())

    def _build_task_app_view(self):
        """Erstellt eine interaktive, voll funktionsfähige Task-Verwaltung im Aegis-Look"""
        container = ctk.CTkFrame(self.right_screen, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=5)

        # 1. Tabelle für die Aufgaben initialisieren
        self.task_tabelle = ttk.Treeview(container, columns=("id", "aufgabe", "status"), show="headings", height=12)
        self.task_tabelle.heading("id", text="ID")
        self.task_tabelle.heading("aufgabe", text="Aufgabe / Anweisung")
        self.task_tabelle.heading("status", text="Status")
        
        self.task_tabelle.column("id", anchor="center", width=50)
        self.task_tabelle.column("aufgabe", anchor="w", width=450)
        self.task_tabelle.column("status", anchor="center", width=120)

        # Style anwenden (Nutzt das bestehende Scout-Design)
        style = ttk.Style()
        style.configure("Scout.TaskTreeview", background="#181820", foreground="#ffffff", fieldbackground="#181820", bordercolor="#2d2d3d", borderwidth=1, rowheight=28)
        style.configure("Scout.TaskTreeview.Heading", background="#22222e", foreground="#00ffcc", relief="flat", font=("Consolas", 11, "bold"))
        style.map("Scout.TaskTreeview", background=[("selected", "#154515")], foreground=[("selected", "#ffffff")])
        self.task_tabelle.configure(style="Scout.TaskTreeview")
        self.task_tabelle.pack(fill="both", expand=True, pady=(0, 10))

        # Zeilen-Styling für Status und Aegis-Dark-Look
        self.task_tabelle.tag_configure("open", background="#181820", foreground="#ffffff")
        self.task_tabelle.tag_configure("done", background="#101216", foreground="#9fd4b1")

        # --- KONTROLLZENTRUM UNTEN ---
        action_frame = ctk.CTkFrame(container, fg_color="transparent")
        action_frame.pack(fill="x", pady=5)

        # Feld für neue Aufgaben
        self.entry_new_task = ctk.CTkEntry(action_frame, placeholder_text="Neue Aufgabe eingeben...", font=("Consolas", 12))
        self.entry_new_task.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_new_task.bind("<Return>", lambda e: self._add_task_event())

        # Button: Hinzufügen
        btn_add = ctk.CTkButton(action_frame, text="Hinzufügen ➕", width=100, fg_color="#152535", hover_color="#203545", command=self._add_task_event)
        btn_add.pack(side="left", padx=5)

        # Button: Als erledigt markieren
        btn_done = ctk.CTkButton(action_frame, text="Erledigt ✔️", width=100, fg_color="#103510", hover_color="#154515", command=self._mark_task_done_event)
        btn_done.pack(side="right", padx=5)

        # Daten beim Öffnen direkt laden
        self._refresh_task_tabelle()

    def _refresh_task_tabelle(self):
        """Liest die Aufgaben frisch aus der SQLite-Datenbank und rendert sie neu"""
        if not hasattr(self, "task_tabelle") or not self.task_tabelle.winfo_exists():
            return
            
        for item in self.task_tabelle.get_children():
            self.task_tabelle.delete(item)

        tasks = self.storage.get_all_tasks()
        if tasks:
            for t in tasks:
                # t[0] = ID, t[1] = Beschreibung, t[2] = Status
                status_text = "🟢 OPEN" if t[2] == "OPEN" else "⚪ DONE"
                tag = "open" if t[2] == "OPEN" else "done"
                self.task_tabelle.insert("", "end", values=(t[0], t[1], status_text), tags=(tag,))

    def _add_task_event(self):
        """Fügt eine neue Aufgabe über die Storage-Engine hinzu"""
        task_text = self.entry_new_task.get().strip()
        if task_text:
            # Nutzt deine AegisStorage Engine
            if hasattr(self.storage, "add_task"):
                self.storage.add_task(task_text)
            elif hasattr(self.storage, "create_task"):
                self.storage.create_task(task_text)
                
            self.entry_new_task.delete(0, "end")
            self._refresh_task_tabelle()

    def _mark_task_done_event(self):
        """Markiert das in der Tabelle ausgewählte Element als ERLEDIGT"""
        selected = self.task_tabelle.selection()
        if not selected:
            return
            
        item_data = self.task_tabelle.item(selected[0], "values")
        task_id = item_data[0]

        # Versuche die Update-Methode deiner Storage-Engine zu triggern
        if hasattr(self.storage, "complete_task"):
            self.storage.complete_task(task_id)
        elif hasattr(self.storage, "update_task_status"):
            self.storage.update_task_status(task_id, "DONE")
            
        self._refresh_task_tabelle()

    def _log_ui(self, message: str):
        """Schreibt Logs absolut Thread-sicher über die .after() Methode der UI Engine"""
        def thread_safe_insert():
            if hasattr(self, "scout_log_box") and self.scout_log_box.winfo_exists():
                self.scout_log_box.insert("end", message + "\n")
                self.scout_log_box.see("end")
        self.after(0, thread_safe_insert)

    def _build_agent_app_view(self, app_name):
        """Steuer-Zentrale für dedizierte Hintergrund-Agenten mit Live-Logbox und Treffer-Anzeige"""
        app_info = self.apps[app_name]
        
        lbl_info = ctk.CTkLabel(self.right_screen, text=f"Skriptpfad: {app_info['path']}", font=("Consolas", 12))
        lbl_info.pack(anchor="w", padx=20, pady=5)

        if app_name == "Agent Scout":
            btn_start = ctk.CTkButton(self.right_screen, text="SCOUT JAGD STARTEN ▶", fg_color="#103510", hover_color="#154515",
                                      command=self._start_scout_jagd)
            btn_start.pack(fill="x", padx=20, pady=10)

            # --- ERWEITERUNG: Treffer-Tabelle direkt ins Dashboard einbetten ---
            self._erzeuge_scout_treffer_ui(self.right_screen)

            ctk.CTkLabel(self.right_screen, text="LIVE DEPLOYMENT LOGS:", font=("Consolas", 11, "bold"), text_color="#7777aa").pack(anchor="w", padx=20, pady=(10, 2))
            
            self.scout_log_box = tk.Text(self.right_screen, bg="#0d0d11", fg="#00ffaa", font=("Consolas", 11), bd=0, highlightthickness=0)
            self.scout_log_box.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            self.scout_log_box.insert("end", "[SYSTEM] Scout-Konsole initialisiert. Warte auf Jagd-Befehl...\n")
            
        else:
            btn_start = ctk.CTkButton(self.right_screen, text="STARTEN ▶", fg_color="#103510", hover_color="#154515", 
                                       command=lambda: self.pm.start_agent(app_name, app_info["path"]))
            btn_start.pack(fill="x", padx=20, pady=10)

            btn_stop = ctk.CTkButton(self.right_screen, text="STOPPEN 🛑", fg_color="#401515", hover_color="#551515", 
                                      command=lambda: self.pm.stop_agent(app_name))
            btn_stop.pack(fill="x", padx=20, pady=10)

    def _erzeuge_scout_treffer_ui(self, parent_layout):
        """Erstellt eine saubere Tabelle im Dashboard für die gefundenen DETO-Ausschreibungen."""
        
        # Überschrift für die Treffer
        self.treffer_label = tk.Label(parent_layout, text="🎯 GEFUNDENE AUSSCHREIBUNGEN (DETO-PROFIL):", fg="#00ffcc", bg="#181820", font=("Consolas", 12, "bold"))
        self.treffer_label.pack(anchor="w", padx=10, pady=(10, 4))
        
        # Tabelle initialisieren
        self.treffer_tabelle = ttk.Treeview(parent_layout, columns=("titel", "ort", "zeitstempel"), show="headings", height=8)
        self.treffer_tabelle.heading("titel", text="Titel")
        self.treffer_tabelle.heading("ort", text="Ort")
        self.treffer_tabelle.heading("zeitstempel", text="Zeitstempel")
        self.treffer_tabelle.column("titel", anchor="w", width=380)
        self.treffer_tabelle.column("ort", anchor="w", width=140)
        self.treffer_tabelle.column("zeitstempel", anchor="w", width=130)
        
        # Darkstyle per Treeview
        style = ttk.Style()
        style.configure("Scout.Treeview", background="#1a1a24", foreground="#ffffff", fieldbackground="#1a1a24", bordercolor="#2d2d3d", borderwidth=1)
        style.configure("Scout.Treeview.Heading", background="#2d2d3d", foreground="#00ffcc", relief="flat")
        self.treffer_tabelle.configure(style="Scout.Treeview")
        
        self.treffer_tabelle.pack(fill="x", padx=10, pady=(0, 16))

    def update_treffer_tabelle(self, treffer_liste):
        """Wird aufgerufen, sobald der Scout-Lauf beendet ist, um die GUI live zu füttern."""
        for item in self.treffer_tabelle.get_children():
            self.treffer_tabelle.delete(item)

        for treffer in treffer_liste:
            self.treffer_tabelle.insert("", "end", values=(
                treffer.get("titel", "Unbekannt"),
                treffer.get("ort", "Aachen"),
                treffer.get("zeitstempel", "")
            ))

    def _global_kill(self):
        self.pm.stop_all()
        self.scout_active_flag = False
        self.lbl_global_status.configure(text="ALLE AGENTEN GESTOPPT", text_color="#ff3333")

    def _update_loop(self):
        """Fragt den ProcessManager ab und prüft manuelle Threads/Fenster"""
        statuses = self.pm.get_statuses()
        normalized_statuses = {str(k).strip().lower(): v for k, v in statuses.items()}
        
        for app_name in self.apps.keys():
            if app_name in self.tiles:
                app_key_lower = app_name.strip().lower()
                status = "OFFLINE"
                
                for stat_key, stat_val in normalized_statuses.items():
                    if stat_key in app_key_lower or app_key_lower in stat_key:
                        status = stat_val
                        break
                
                # 🛠️ MANUELLE KORREKTUR: Ermittelt den Scout-Status über das krisensichere interne Tracking-Flag
                if app_name == "Agent Scout" and self.scout_active_flag:
                    status = "RUNNING"
                
                # LED-Farbe basierend auf dem gefundenen Status setzen
                if status == "RUNNING":
                    self.tiles[app_name]["led"].configure(text_color="#00ffaa")  # Hellgrün
                elif status == "CRASHED":
                    self.tiles[app_name]["led"].configure(text_color="#ffaa00")  # Orange
                else:
                    self.tiles[app_name]["led"].configure(text_color="#ff4444")  # Rot
                    
        self.after(1000, self._update_loop)

if __name__ == "__main__":
    app = AegisOSDashboard()
    app.mainloop()    