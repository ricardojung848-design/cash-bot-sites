# modules/video_engine.py

import os
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from core.utils import log_worker, error_worker

class VideoEngine:
    def __init__(self, assets_dir: str):
        self.assets_dir = assets_dir

    def create_reel(self, script: dict, voice_path: str, output_path: str) -> str:
        """
        Erstellt ein 9:16 Reel mit:
        - B-Roll
        - Text-Overlays
        - Voiceover
        - Musik
        """

        try:
            # 1. B-Roll laden
            broll_path = os.path.join(self.assets_dir, "broll.mp4")
            music_path = os.path.join(self.assets_dir, "music.mp3")

            base = VideoFileClip(broll_path).resize((1080, 1920))

            # 2. Voiceover
            voice = AudioFileClip(voice_path)

            # 3. Musik
            music = AudioFileClip(music_path).volumex(0.15)

            # 4. Text-Overlays
            clips = [base]

            y_offset = 200
            for line in script["content"]:
                txt = TextClip(
                    line,
                    fontsize=70,
                    color="white",
                    stroke_color="black",
                    stroke_width=3,
                    method="caption",
                    size=(900, None)
                ).set_position(("center", y_offset)).set_duration(3)
                clips.append(txt)
                y_offset += 200

            # 5. Audio mischen
            final_audio = voice.volumex(1.0).audio_fadein(0.5).audio_fadeout(0.5)
            final = CompositeVideoClip(clips).set_audio(final_audio)

            # 6. Export
            final.write_videofile(output_path, fps=30, codec="libx264", audio_codec="aac")

            log_worker(f"🎬 Reel exportiert: {output_path}")
            return output_path

        except Exception as e:
            error_worker(f"❌ Video-Fehler: {e}")
            return ""
