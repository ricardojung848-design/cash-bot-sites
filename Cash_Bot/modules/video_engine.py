import os
import subprocess
from core.utils import log_worker, warn_worker, error_worker


class VideoEngine:
    def __init__(self, assets_dir: str) -> None:
        self.assets_dir = assets_dir
        self.broll_path = os.path.join(assets_dir, "broll.mp4")
        self.music_path = os.path.join(assets_dir, "music.mp3")

    # ---------------------------------------------------------
    # Hilfsfunktion: FFmpeg ausführen
    # ---------------------------------------------------------
    def _run_ffmpeg(self, cmd: list) -> bool:
        try:
            log_worker("FFmpeg wird ausgeführt...")
            subprocess.run(cmd, check=True)
            return True
        except Exception as e:
            error_worker(f"FFmpeg Fehler: {e}")
            return False

    # ---------------------------------------------------------
    # Hauptfunktion: Reel erstellen
    # ---------------------------------------------------------
    def create_reel(self, script: dict, voice_path: str, output_path: str) -> str:
        log_worker("Starte Video-Rendering...")

        # -----------------------------------------------------
        # 1) Prüfen, ob B‑Roll existiert
        # -----------------------------------------------------
        if not os.path.exists(self.broll_path):
            warn_worker("⚠️ Keine broll.mp4 gefunden – erstelle statischen Hintergrund.")

            # Fallback: 15 Sekunden schwarzes Video
            fallback_video = os.path.join(self.assets_dir, "fallback_broll.mp4")
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi",
                "-i", "color=c=black:s=1080x1920:d=15",
                fallback_video
            ]
            if not self._run_ffmpeg(cmd):
                return ""

            broll = fallback_video
        else:
            broll = self.broll_path

        # -----------------------------------------------------
        # 2) Prüfen, ob Musik existiert
        # -----------------------------------------------------
        music_exists = os.path.exists(self.music_path)

        # -----------------------------------------------------
        # 3) Voiceover + Musik mischen
        # -----------------------------------------------------
        mixed_audio = os.path.join(self.assets_dir, "mixed_audio.mp3")

        if music_exists:
            log_worker("🎵 Musik gefunden – mische Voice + Musik.")

            cmd = [
                "ffmpeg", "-y",
                "-i", voice_path,
                "-i", self.music_path,
                "-filter_complex",
                "[0:a]volume=1.0[a0];[1:a]volume=0.25[a1];[a0][a1]amix=inputs=2:duration=first:dropout_transition=2",
                mixed_audio
            ]
        else:
            warn_worker("⚠️ Keine music.mp3 gefunden – nutze nur Voiceover.")
            cmd = [
                "ffmpeg", "-y",
                "-i", voice_path,
                "-filter:a", "volume=1.0",
                mixed_audio
            ]

        if not self._run_ffmpeg(cmd):
            return ""

        # -----------------------------------------------------
        # 4) Finales Reel rendern (9:16)
        # -----------------------------------------------------
        cmd = [
            "ffmpeg", "-y",
            "-i", broll,
            "-i", mixed_audio,
            "-map", "0:v",
            "-map", "1:a",
            "-c:v", "libx264",
            "-preset", "medium",
            "-t", "15",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease",
            "-c:a", "aac",
            "-shortest",
            output_path
        ]

        if not self._run_ffmpeg(cmd):
            return ""

        log_worker(f"🎬 Reel erfolgreich erstellt: {output_path}")
        return output_path
