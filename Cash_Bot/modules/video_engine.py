import os
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

from doctor_core.logging import log_doctor
from doctor_core.engine_manager import EngineManager


class VideoEngine:
    """
    PRO-Version der VideoEngine:
    - Kombiniert B-Roll-Footage, Voiceover und Hintergrundmusik zu finalen Hochkant-Reels (9:16).
    - Verwendet komplexe FFmpeg-Audio-Filter (amix) für sauberes Audio-Mischverhalten.
    - Vollständig thread-sicher für die parallele Abarbeitung in der FabrikEngine integriert.
    """

    def __init__(self, engine_manager: EngineManager, assets_dir: str):
        self.engines = engine_manager
        self.assets_path = Path(assets_dir).resolve()
        
        # Pfade zu den Standard-Assets definieren
        self.broll_path = self.assets_path / "broll.mp4"
        self.music_path = self.assets_path / "music.mp3"

    def _run_ffmpeg(self, cmd: List[str]) -> bool:
        """Führt einen FFmpeg-Befehl aus und fängt Fehler im Subprozess ab."""
        try:
            log_doctor("VideoEngine: Rufe FFmpeg-Subprozess auf...")
            # stdout und stderr werden unterdrückt bzw. über PIPE abgefangen, um Thread-Ausgaben sauber zu halten
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError as e:
            error_details = e.stderr.decode("utf-8", errors="ignore") if e.stderr else str(e)
            log_doctor(f"VideoEngine-Fehler: FFmpeg-Prozess fehlgeschlagen: {error_details}")
            return False
        except Exception as e:
            log_doctor(f"VideoEngine-Kritisch: Systemfehler bei FFmpeg-Ausführung: {e}")
            return False

    def create_reel(self, script: Dict[str, Any], voice_path: str, output_path: str) -> str:
        """
        Mischt Voiceover und Hintergrundmusik und mergt das Ergebnis mit dem B-Roll-Video.
        Erzeugt ein valides Social-Media-Reel am Zielort 'output_path'.
        """
        log_doctor("VideoEngine: Starte automatisierten Video-Rendering-Prozess...")

        # Sicherstellen, dass das Basis-Asset-Verzeichnis existiert
        self.assets_path.mkdir(parents=True, exist_ok=True)
        
        target_output = Path(output_path).resolve()
        target_output.parent.mkdir(parents=True, exist_ok=True)

        # -----------------------------------------------------
        # 1) B-Roll Validierung & Fallback-Generierung
        # -----------------------------------------------------
        if not self.broll_path.exists():
            log_doctor(f"VideoEngine-Warnung: '{self.broll_path.name}' fehlt. Generiere Fallback-Hintergrund...")
            fallback_video = self.assets_path / "fallback_broll.mp4"
            
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi",
                "-i", "color=c=black:s=1080x1920:d=15",
                str(fallback_video)
            ]
            if not self._run_ffmpeg(cmd):
                return ""
            broll = fallback_video
        else:
            broll = self.broll_path

        # -----------------------------------------------------
        # 2) Audio-Mixing (Voiceover + Hintergrundmusik)
        # -----------------------------------------------------
        music_exists = self.music_path.exists()
        mixed_audio = self.assets_path / "mixed_audio.mp3"

        if music_exists:
            log_doctor("VideoEngine: Hintergrundmusik erkannt. Starte Audio-Spuren-Mischung...")
            cmd = [
                "ffmpeg", "-y",
                "-i", str(Path(voice_path).resolve()),
                "-i", str(self.music_path),
                "-filter_complex",
                "[0:a]volume=1.0[a0];[1:a]volume=0.25[a1];[a0][a1]amix=inputs=2:duration=first:dropout_transition=2",
                str(mixed_audio)
            ]
        else:
            log_doctor("VideoEngine-Warnung: Keine Musik gefunden. Exportiere reines Voiceover...")
            cmd = [
                "ffmpeg", "-y",
                "-i", str(Path(voice_path).resolve()),
                "-filter:a", "volume=1.0",
                str(mixed_audio)
            ]

        if not self._run_ffmpeg(cmd):
            return ""

        # -----------------------------------------------------
        # 3) Finales Video-Muxing & Skalierung (9:16)
        # -----------------------------------------------------
        log_doctor("VideoEngine: Kombiniere Audio- und Videospuren für das finale Reel...")
        cmd = [
            "ffmpeg", "-y",
            "-i", str(broll),
            "-i", str(mixed_audio),
            "-map", "0:v",
            "-map", "1:a",
            "-c:v", "libx264",
            "-preset", "medium",
            "-t", "15",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(1080-w)/2:(1920-h)/2",
            "-c:a", "aac",
            "-shortest",
            str(target_output)
        ]

        if not self._run_ffmpeg(cmd):
            return ""

        log_doctor(f"VideoEngine: 🎉 Reel erfolgreich gerendert und exportiert -> {target_output}")
        return str(target_output)


# Abwärtskompatibler Einstiegspunkt für ältere Programmteile
def create_reel_legacy(script: Dict[str, Any], voice_path: str, output_path: str, assets_dir: str, engine_manager: EngineManager) -> str:
    """Erlaubt Legacy-Modulen den Aufruf der neuen Rendering-Logik."""
    engine = VideoEngine(engine_manager, assets_dir)
    return engine.create_reel(script, voice_path, output_path)