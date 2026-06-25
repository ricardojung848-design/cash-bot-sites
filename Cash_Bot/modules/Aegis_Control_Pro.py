import sys
import threading
import time
import tkinter as tk
from pathlib import Path

# Versuche CustomTkinter für das Sci-Fi Rendering zu laden
try:
    import customtkinter as ctk
except ImportError:
    import os
    os.system('pip install customtkinter')
    import customtkinter as ctk

# Bindung an dein bestehendes System
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Hier werden deine stabilen Triebwerke importiert
# from doctor_core.engine_manager import EngineManager

class AegisControlCenter(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Fenster-Setup (Kommandozentrale)
        self.title("AEGIS // QUANTUM INTELLIGENCE CORE")
        self.geometry("1200x750")
        self.configure(fg_color="#050507") # Tiefschwarzer Space-Hintergrund

        # CustomTkinter Dark-Red Theme erzwingen
        ctk.set_appearance_mode("dark")
        
        # Globale Design-Farben (Cyber-Neon-Rot & Lava)
        self.color_neon_red = "#ff2a2a"
        self.color_glass_bg = "#150505"
        self.color_border_glow = "#8a0f0f"

        # UI aufbauen
        self._create_header()
        self._create_bento_grid()
        
        # Hotkey für das Spotlight-Overlay registrieren (Asynchron)
        threading.Thread(target=self._init_global_shortcuts, daemon=True).start()

    def _create_header(self):
        """Erstellt die obere Kontroll-Leiste im Sci-Fi Look"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 0))

        title = ctk.CTkLabel(
            header_frame, 
            text="▲ AEGIS // COGNITIVE COMMAND SYSTEM v2050", 
            font=("Orbitron", 16, "bold"), 
            text_color=self.color_neon_red
        )
        title.pack(side="left")

        self.status_led = ctk.CTkLabel(
            header_frame, 
            text="● CORE STATUS: NOMINAL", 
            font=("Consolas", 11), 
            text_color="#00ffaa" # Kontrast-Grün für "Alles OK"
        )
        self.status_led.pack(side="right")

    def _create_bento_grid(self):
        """Baut das Bento-Box-Grid aus schwebenden Glas-Modulen"""
        # Haupt-Container für das Grid
        grid_container = ctk.CTkFrame(self, fg_color="transparent")
        grid_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        grid_container.grid_columnconfigure((0, 1, 2), weight=1, uniform="equal")
        grid_container.grid_rowconfigure((0, 1), weight=1, uniform="equal")

        # Modul 1: Agenten-Status-Zentrale (Bento-Box Links Oben)
        mod_agents = ctk.CTkFrame(grid_container, fg_color=self.color_glass_bg, border_color=self.color_border_glow, border_width=1, corner_radius=15)
        mod_agents.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self._add_module_title(mod_agents, "📡 AGENT STATUS REGISTRY")
        
        # Modul 2: Das KI-Auge (Bento-Box Mitte Oben)
        mod_eye = ctk.CTkFrame(grid_container, fg_color=self.color_glass_bg, border_color=self.color_border_glow, border_width=1, corner_radius=15)
        mod_eye.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self._add_module_title(mod_eye, "👁️ SCREEN CONTEXT VECTOR")

        # Modul 3: Vektor-Speicher Mindmap (Bento-Box Rechts Oben)
        mod_vector = ctk.CTkFrame(grid_container, fg_color=self.color_glass_bg, border_color=self.color_border_glow, border_width=1, corner_radius=15)
        mod_vector.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        self._add_module_title(mod_vector, "🕸️ LOCAL KNOWLEDGE WIREFRAME")

        # Modul 4: Live-Denk-Log (Bento-Box Unten gestreckt)
        mod_log = ctk.CTkFrame(grid_container, fg_color=self.color_glass_bg, border_color=self.color_border_glow, border_width=1, corner_radius=15)
        mod_log.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        self._add_module_title(mod_log, "⚡ LIVE COGNITIVE TELEMETRY")
        
        # Log-Textfeld im Matrix-Rot
        log_box = tk.Text(mod_log, bg="#0b0202", fg=self.color_neon_red, insertbackground=self.color_neon_red, font=("Consolas", 10), bd=0, highlightthickness=0)
        log_box.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        log_box.insert("end", "[SYSTEM] Aegis-Kanal initialisiert. Warte auf kognitive Impulse...\n")

    def _add_module_title(self, frame, text):
        lbl = ctk.CTkLabel(frame, text=text, font=("Orbitron", 11, "bold"), text_color="#ffffff")
        lbl.pack(anchor="w", padx=15, pady=10)

    # --- DESKTOP APP FEATURES ---
    def _init_global_shortcuts(self):
        """Überwacht systemweit Tastendrücke (z.B. für das Spotlight-Overlay)"""
        try:
            import keyboard
            # Wenn Strg+Space gedrückt wird, poppt das Spotlight auf
            keyboard.add_hotkey("ctrl+space", self.trigger_spotlight_overlay)
        except ImportError:
            # Falls Paket fehlt, im Hintergrund nachinstallieren
            import os
            os.system('pip install keyboard')

    def trigger_spotlight_overlay(self):
        """Öffnet das zentrierte, rahmenlose Eingabefeld über allen Fenstern"""
        # Wechselt zurück in den Hauptthread für UI-Aktionen
        self.after(0, self._show_spotlight_window)

    def _show_spotlight_window(self):
        spotlight = tk.Toplevel(self)
        spotlight.title("Aegis Spotlight")
        spotlight.overrideredirect(True) # Entfernt Windows-Rahmen
        spotlight.attributes("-topmost", True) # Immer im Vordergrund
        
        # Zentrieren auf dem Bildschirm
        screen_width = spotlight.winfo_screenwidth()
        screen_height = spotlight.winfo_screenheight()
        w, h = 600, 50
        x = (screen_width - w) // 2
        y = (screen_height - h) // 3
        spotlight.geometry(f"{w}x{h}+{x}+{y}")
        spotlight.configure(bg="#050507")

        # Roter Glührahmen via Frame-Verschachtelung
        glow_frame = tk.Frame(spotlight, bg=self.color_neon_red, bd=1)
        glow_frame.pack(fill="both", expand=True)

        entry = tk.Entry(glow_frame, bg="#100303", fg="#ffffff", insertbackground=self.color_neon_red, font=("Orbitron", 12), bd=0, justify="center")
        entry.pack(fill="both", expand=True, padx=2, pady=2)
        entry.focus_set()

        # Schließen bei Escape
        spotlight.bind("<Escape>", lambda e: spotlight.destroy())
        entry.bind("<Return>", lambda e: [print(f"[AEGIS COMMAND]: {entry.get()}"), spotlight.destroy()])

if __name__ == "__main__":
    app = AegisControlCenter()
    app.run()