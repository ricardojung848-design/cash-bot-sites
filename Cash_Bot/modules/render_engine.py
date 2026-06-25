import subprocess
import os
from pathlib import Path
from typing import Optional

from doctor_core.logging import log_doctor
from doctor_core.engine_manager import EngineManager


class RenderEngine:
    """
    PRO-Version der RenderEngine:
    - Kapselt systemnahe FFmpeg-Aufrufe zur automatisierten Videogenerierung.
    - Vollständig thread-sicher konzipiert für die asynchrone parallele Ausführung in der FabrikEngine.
    - Sichert die automatische Erstellung von Zielverzeichnissen vor dem Render-Prozess.
    """

    def __init__(self, engine_manager: EngineManager, ffmpeg_path: str = "ffmpeg"):
        self.engines = engine_manager
        self.ffmpeg = ffmpeg_path

    def render_reel(self, text: str, output_path: str) -> bool:
        """
        Erstellt ein standardisiertes Hochkant-Reel (1080x1920, 6 Sekunden) 
        mit zentriertem Text auf schwarzem Hintergrund via FFmpeg.
        """
        try:
            log_doctor("RenderEngine: Starte FFmpeg-Prozess für Video-Generierung...")
            
            # Sicherstellen, dass der Zielordner auf der Festplatte existiert
            target_file = Path(output_path).resolve()
            target_file.parent.mkdir(parents=True, exist_ok=True)

            # FFmpeg-Kommandozeilen-Argumente für ein sauberes H.264-Video
            cmd = [
                self.ffmpeg,
                "-y",  # Vorhandene Dateien ohne Nachfrage überschreiben
                "-f", "lavfi",
                "-i", "color=c=black:s=1080x1920:d=6",
                "-vf", f"drawtext=text='{text}':fontcolor=white:fontsize=64:x=(w-text_w)/2:y=(h-text_h)/2",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                str(target_file)
            ]

            # Ausführen des Subprozesses; stdout/stderr werden abgefangen, falls Fehler auftreten
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            log_doctor(f"RenderEngine: 🎉 Reel erfolgreich gerendert -> {target_file}")
            return True

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode("utf-8", errors="ignore") if e.stderr else str(e)
            log_doctor(f"RenderEngine-Fehler: FFmpeg-Prozess fehlgeschlagen: {error_msg}")
            return False
        except Exception as e:
            log_doctor(f"RenderEngine-Kritisch: Unerwarteter Fehler beim Rendern: {e}")
            return False


# Abwärtskompatibler Einstiegspunkt für ältere Programmteile
def render_reel_legacy(text: str, output_path: str, engine_manager: EngineManager) -> bool:
    """Erlaubt Legacy-Modulen den Aufruf der neuen Render-Logik."""
    renderer = RenderEngine(engine_manager)
    return renderer.render_reel(text, output_path)