# modules/render_engine.py

import subprocess
import os
from core.utils import log_worker, error_worker

class RenderEngine:
    def __init__(self, ffmpeg_path: str = "ffmpeg") -> None:
        self.ffmpeg = ffmpeg_path

    def render_reel(self, text: str, output_path: str) -> bool:
        """
        Erstellt ein einfaches Reel mit Text auf schwarzem Hintergrund.
        """
        try:
            log_worker("🎬 Render Reel mit FFmpeg...")

            cmd = [
                self.ffmpeg,
                "-f", "lavfi",
                "-i", "color=c=black:s=1080x1920:d=6",
                "-vf", f"drawtext=text='{text}':fontcolor=white:fontsize=64:x=(w-text_w)/2:y=(h-text_h)/2",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                output_path
            ]

            subprocess.run(cmd, check=True)
            log_worker(f"🎉 Reel gerendert: {output_path}")
            return True

        except Exception as e:
            error_worker(f"Render Error: {e}")
            return False
