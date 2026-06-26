import os
import sys
import json
import tkinter as tk
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

LAYOUT_FILE = BASE_DIR / "config" / "layout.json"
REGISTRY_FILE = BASE_DIR / "config" / "registry.json"

class AegisOSDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. Core Engines initialisieren
        self.doctor_state = DoctorState()
        self.engines = EngineManager()
        self.engines.register("state", self.doctor_state)
        
        self.pm = AgentProcessManager(self.engines)
        self.storage = AegisStorage()
        self.dialog_engine = AegisDialogEngine(self.engines)

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
        
        # Standard-Anordnung falls neu: Zuweisung [Row, Column]
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

    def _build_main_layout(self):
        """Erstellt die iPhone-Splitscreen-Struktur"""
        # HEADER
        header = ctk.CTkFrame(self, fg_color="transparent", height=40)
        header.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(header, text="📱 Aegis OS v2.0", font=("Consolas", 16, "bold")).pack(side="left")
        self.lbl_global_status = ctk.CTkLabel(header, text="SYSTEM NOMINAL", text_color="#00ffaa", font=("Consolas", 12, "bold"))
        self.lbl_global_status.pack(side="right")

        # NOTSCHALTER (Kill Switch)
        btn_kill = ctk.CTkButton(header, text="🛑 ALL KILL", fg_color="#401010", hover_color="#601010", width=80, command=self._global_kill)
        btn_kill.pack(side="right", padx=20)

        # MAIN CONTAINER
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Links: iPhone Grid-Fläche
        self.left_screen = ctk.CTkScrollableFrame(main_container, width=400, fg_color="#121216", border_width=1, border_color="#22222a")
        self.left_screen.pack(side="left", fill="both", expand=False, padx=5)
        
        # Rechts: Großes Display für fokussierte App
        self.right_screen = ctk.CTkFrame(main_container, fg_color="#181820", border_width=1, border_color="#22222a")
        self.right_screen.pack(side="right", fill="both", expand=True, padx=5)

    def _render_app_grid(self):
        """Baut das Grid basierend auf den Layout-Koordinaten auf"""
        # Bestehende Widgets im linken Screen löschen
        for widget in self.left_screen.winfo_children():
            widget.destroy()

        # Grid konfigurieren
        self.left_screen.grid_columnconfigure((0, 1), weight=1, minsize=180)

        self.tiles = {}
        for app_name, pos in self.app_positions.items():
            row, col = pos[0], pos[1]
            
            # App-Kachel (Container)
            tile = ctk.CTkFrame(self.left_screen, fg_color="#22222e", border_width=1, border_color="#333344", height=120)
            tile.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            tile.grid_propagate(False)

            # Linksklick -> App rechts öffnen
            tile.bind("<Button-1>", lambda event, name=app_name: self._open_app_view(name))
            
            # Rechtsklick -> Kachel für Verschieben auswählen
            tile.bind("<Button-3>", lambda event, name=app_name: self._select_for_move(name))

            # Status LED (An/Aus)
            led = ctk.CTkLabel(tile, text="●", text_color="#ff5555", font=("Consolas", 14))
            led.place(x=15, y=10)

            # App Name
            lbl_name = ctk.CTkLabel(tile, text=app_name, font=("Consolas", 13, "bold"))
            lbl_name.place(x=35, y=8)
            
            # Event-Weiterleitung für Klick auf Label/LED
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
            # Tausche Positionen zwischen zuvor gewählter und dieser geklickten Kachel
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

        # Titel der App oben rechts anzeigen
        title_frame = ctk.CTkFrame(self.right_screen, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(title_frame, text=f"📂 APP // {app_name.upper()}", font=("Consolas", 16, "bold")).pack(side="left")

        # Fallunterscheidung: Welche App wurde geklickt?
        if app_name == "AI Voice Chat":
            self._build_voice_app_view()
        elif app_name == "Task Manager":
            self._build_task_app_view()
        else:
            # Dynamische Agenten-Steuerung (Start/Stopp-Fläche)
            self._build_agent_app_view(app_name)

    def _build_voice_app_view(self):
        """Die Chat-Oberfläche für deine KI-Unterhaltungen"""
        container = ctk.CTkFrame(self.right_screen, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=5)

        self.chat_history = tk.Text(container, bg="#0d0d11", fg="#00ffaa", font=("Consolas", 11), bd=0, highlightthickness=0)
        self.chat_history.pack(fill="both", expand=True, pady=(0, 10))
        self.chat_history.insert("end", "Aegis OS Dialogue System bereit. Sprechen oder schreiben Sie einen Befehl...\n\n")

        input_frame = ctk.CTkFrame(container, fg_color="transparent")
        input_frame.pack(fill="x")

        entry_cmd = ctk.CTkEntry(input_frame, placeholder_text="Z.B.: 'starte Worker' oder 'erstelle Aufgabe Kaffee kochen'...", font=("Consolas", 12))
        entry_cmd.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        def send_voice_cmd():
            text = entry_cmd.get().strip()
            if text:
                self.chat_history.insert("end", f"👤 DU: {text}\n")
                
                # 🛠️ LOGIK-BRÜCKE: Erkennt den Startbefehl im Chat
                if text.lower().startswith("starte "):
                    # Extrahiert den Namen (z.B. "worker")
                    target_agent = text[7:].strip().lower()
                    
                    # Sucht den passenden Eintrag in deiner Registry
                    found_app_name = None
                    for app_name in self.apps.keys():
                        if target_agent in app_name.lower():
                            found_app_name = app_name
                            break
                    
                    if found_app_name:
                        script_path = self.apps[found_app_name]["path"]
                        # Startet den Prozess über den ProcessManager!
                        res = self.pm.start_agent(found_app_name, script_path)
                        if res == "SUCCESS":
                            self.chat_history.insert("end", f"🤖 AEGIS: [{found_app_name}] wurde erfolgreich gestartet!\n\n")
                        else:
                            self.chat_history.insert("end", f"🤖 AEGIS: Startfehler -> {res}\n\n")
                    else:
                        self.chat_history.insert("end", f"🤖 AEGIS: Agent '{target_agent}' wurde in der registry.json nicht gefunden.\n\n")
                else:
                    # Normaler Dialog falls kein Startbefehl
                    reply = self.dialog_engine.process_command(text)
                    self.chat_history.insert("end", f"🤖 AEGIS: {reply}\n\n")
                
                self.chat_history.see("end")
                entry_cmd.delete(0, "end")

        btn_send = ctk.CTkButton(input_frame, text="Senden 🚀", width=80, command=send_voice_cmd)
        btn_send.pack(side="right")
        entry_cmd.bind("<Return>", lambda e: send_voice_cmd())

    def _build_task_app_view(self):
        """Zeigt deine Erledigungen aus der SQLite-Datenbank"""
        container = ctk.CTkFrame(self.right_screen, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=5)

        txt_tasks = tk.Text(container, bg="#0d0d11", fg="#ffffff", font=("Consolas", 12), bd=0, highlightthickness=0)
        txt_tasks.pack(fill="both", expand=True, pady=10)

        tasks = self.storage.get_all_tasks()
        if not tasks:
            txt_tasks.insert("end", "Keine offenen Aufgaben registriert.")
        else:
            for t in tasks:
                status_icon = "[OFFEN]" if t[2] == "OPEN" else "[ERLEDIGT]"
                txt_tasks.insert("end", f"{status_icon} ID #{t[0]}: {t[1]}\n")

    def _build_agent_app_view(self, app_name):
        """Steuer-Zentrale für dedizierte Hintergrund-Agenten"""
        app_info = self.apps[app_name]
        
        lbl_info = ctk.CTkLabel(self.right_screen, text=f"Skriptpfad: {app_info['path']}", font=("Consolas", 12))
        lbl_info.pack(anchor="w", padx=20, pady=5)

        btn_start = ctk.CTkButton(self.right_screen, text="STARTEN ▶", fg_color="#103510", hover_color="#154515", 
                                   command=lambda: self.pm.start_agent(app_name, app_info["path"]))
        btn_start.pack(fill="x", padx=20, pady=10)

        btn_stop = ctk.CTkButton(self.right_screen, text="STOPPEN 🛑", fg_color="#401515", hover_color="#551515", 
                                  command=lambda: self.pm.stop_agent(app_name))
        btn_stop.pack(fill="x", padx=20, pady=10)

    def _global_kill(self):
        self.pm.stop_all()
        self.lbl_global_status.configure(text="ALLE AGENTEN GESTOPPT", text_color="#ff3333")

    def _update_loop(self):
        """Fragt sekündlich den Prozessmanager ab und schaltet die LEDs"""
        statuses = self.pm.get_statuses()
        
        for app_name in self.apps.keys():
            if app_name in self.tiles:
                status = statuses.get(app_name, "OFFLINE")
                if status == "RUNNING":
                    self.tiles[app_name]["led"].configure(text_color="#00ffaa")  # Grün
                elif status == "CRASHED":
                    self.tiles[app_name]["led"].configure(text_color="#ffaa00")  # Orange (Doctor aktiv)
                else:
                    self.tiles[app_name]["led"].configure(text_color="#ff4444")  # Rot

        self.after(1000, self._update_loop)

if __name__ == "__main__":
    app = AegisOSDashboard()
    app.mainloop()