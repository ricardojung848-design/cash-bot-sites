import tkinter as tk
from tkinter import ttk

from doctor_core.logging import log_doctor
from doctor_core.engine_manager import EngineManager
from doctor_core.state import DoctorState
from doctor_core.simulation import Phase6Simulation


class AgentDoctorApp:
    def __init__(self):
        self.engines = EngineManager()
        self.state = DoctorState()

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
            text="Agent_Doctor – PRO‑Architektur (Phase 5 + Phase 6 Simulation)",
            font=("Segoe UI", 13, "bold"),
        )
        header.pack(anchor="w", pady=(0, 10))

        self.status_label = ttk.Label(
            main,
            text="Status: Online – Engines geladen.",
            font=("Segoe UI", 10),
        )
        self.status_label.pack(anchor="w", pady=(0, 10))

        # Basis‑Buttons (kannst du später erweitern)
        btn_frame_top = ttk.Frame(main)
        btn_frame_top.pack(anchor="w", pady=(0, 10))

        ttk.Button(btn_frame_top, text="System prüfen").grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(btn_frame_top, text="Logs analysieren").grid(row=0, column=1, padx=5, pady=5)

        # Phase‑5‑Brain (Platzhalter)
        btn_frame_phase5 = ttk.Frame(main)
        btn_frame_phase5.pack(anchor="w", pady=(0, 10))

        ttk.Button(
            btn_frame_phase5,
            text="Phase‑5‑Brain aktualisieren",
            command=self.update_phase5_brain,
        ).grid(row=0, column=0, padx=5, pady=5)

        # Phase‑6‑Funktionen
        btn_frame_phase6 = ttk.Frame(main)
        btn_frame_phase6.pack(anchor="w", pady=(0, 10))

        ttk.Label(
            btn_frame_phase6,
            text="Phase‑6‑Funktionen:",
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=0, padx=5, pady=(0, 5), sticky="w")

        ttk.Button(
            btn_frame_phase6,
            text="Phase‑6‑Simulation starten",
            command=self.run_phase6_simulation,
        ).grid(row=1, column=0, padx=5, pady=5)

        self.log_box = tk.Text(
            main,
            bg="#000000",
            fg="#00ff88",
            insertbackground="#00ff88",
            height=18,
            borderwidth=0,
        )
        self.log_box.pack(fill="both", expand=True)

        log_doctor("Agent_Doctor PRO gestartet.")
        self._log_ui("Agent_Doctor PRO gestartet.")

    def _log_ui(self, msg: str):
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")

    def set_status(self, text: str):
        self.status_label.config(text=text)

    def update_phase5_brain(self):
        self._log_ui("Phase‑5‑Brain aktualisieren (hier kannst du deine Engines nutzen).")
        log_doctor("Phase‑5‑Brain aktualisieren – Platzhalter.")

    def run_phase6_simulation(self):
        self.set_status("Status: Phase‑6‑Simulation läuft...")
        self._log_ui("Phase‑6‑Simulation gestartet.")
        sim = Phase6Simulation(self.engines, self.state)
        sim.run()
        self._log_ui("Phase‑6‑Simulation abgeschlossen.")
        self.set_status("Status: Phase‑6‑Simulation abgeschlossen.")

    def run(self):
        self.root.mainloop()


def main():
    app = AgentDoctorApp()
    app.run()


if __name__ == "__main__":
    main()
