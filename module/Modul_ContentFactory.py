import os
import json
import re
import random
import subprocess
from datetime import datetime, timedelta
from openai import OpenAI
import gspread
from oauth2client.service_account import ServiceAccountCredentials

client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed", timeout=300.0)

class ContentFactory:
    """
    Vollautomatische Content-Generierung für alle Social-Media-Plattformen.
    - Skripte, Video-Konzepte, Bild-Prompts, Captions, Hashtags
    """
    
    def __init__(self, research_data=None):
        """
        Args:
            research_data: Dict mit Daten aus der Self-Research Engine
                         {topics: [], trends: [], keywords: [], products: []}
        """
        self.research_data = research_data or {}
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = "generated_content"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_script(self, topic, duration_seconds=30, style="motivational"):
        """
        Generiert ein Skript für Video-Inhalte.
        
        Args:
            topic: Thema des Videos
            duration_seconds: Länge des Videos (default 30s für TikTok/Reels)
            style: motivational, educational, entertaining, sales
        
        Returns:
            Dict mit Skript-Zeilen, Timing und Notizen
        """
        print(f"[*] Generiere {duration_seconds}s Skript über '{topic}' ({style})...")
        
        prompts_per_second = 2  # ~60 Wörter für 30 Sekunden
        word_count = duration_seconds * prompts_per_second
        
        prompt = f"""
Du bist ein erfahrener Video-Skript-Autor für viral gehende Social-Media-Videos.
Generiere ein prägnantes, engagierendes Skript für ein {duration_seconds}-Sekunden Video.

THEMA: {topic}
STIL: {style}
ZIELGRUPPE: Social-Media-Nutzer (TikTok/Instagram/YouTube Shorts)

ANFORDERUNGEN:
1. Hook (erste 3 Sekunden): Muss SOFORT Aufmerksamkeit greifen
2. Body (Hauptteil): Wechsel zwischen Information/Emotion/Spannung
3. CTA (letzte 2 Sekunden): Call-to-Action (Like, Comment, Share, Follow)
4. MAXIMAL {word_count} Worte
5. Sprechgeschwindigkeit: 160-180 WPM (normal)
6. Pausen und Dramaturgie einplanen

ANTWORT-FORMAT (JSON):
{{
    "hook": "First 3 seconds - MUST GRAB ATTENTION",
    "body": [
        {{"second": 3, "text": "...", "action": "description of visual/B-roll"}},
        {{"second": 10, "text": "...", "action": "description of visual"}},
        ...
    ],
    "cta": "Last 2 seconds - Call To Action",
    "total_seconds": {duration_seconds},
    "speaker_notes": "Tone, pacing, emphasis points",
    "b_roll_suggestions": ["clip 1", "clip 2", "clip 3"]
}}
"""
        
        try:
            completion = client.chat.completions.create(
                model="local-model",
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = completion.choices[0].message.content
            
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                script_data = json.loads(json_match.group())
            else:
                script_data = json.loads(response_text)
            
            return script_data
        except Exception as e:
            print(f"[-] Fehler bei Script-Generierung: {e}")
            return None
    
    def generate_image_prompt(self, topic, style="realistic", platform="instagram"):
        """
        Erstellt professionelle Prompts für KI-Bildgeneratoren.
        
        Args:
            topic: Thema für die Grafik
            style: realistic, abstract, cartoon, minimalist, luxury, edgy
            platform: instagram, tiktok, pinterest, youtube_thumbnail
        
        Returns:
            Dict mit Prompts für verschiedene KI-Tools
        """
        print(f"[*] Generiere Bild-Prompts für {platform} - Stil: {style}...")
        
        dimensions = {
            "instagram": "1080x1350",
            "instagram_story": "1080x1920",
            "tiktok": "1080x1920",
            "pinterest": "1000x1500",
            "youtube_thumbnail": "1280x720"
        }
        
        dim = dimensions.get(platform, "1080x1080")
        
        prompt = f"""
Du bist ein Profi-Prompt-Engineer für KI-Bildgeneratoren (DALL-E, Midjourney, Stable Diffusion).
Erstelle DETAILLIERTE, professionelle Prompts für eine Social-Media-Grafik.

VORGABEN:
- Thema: {topic}
- Stil: {style}
- Plattform: {platform} ({dim})
- Zielgruppe: Junge Erwachsene (18-35 Jahre)

ANFORDERUNGEN:
1. Midjourney Prompt (detailliert, 150+ Worte, kreative Parameter)
2. DALL-E 3 Prompt (klar, strukturiert, beschreibend)
3. Stable Diffusion Prompt (mit Quality/Style/Negative Tags)
4. Color Palette (HEX-Codes) - 5 Farben
5. Design Notes (Komposition, Fokus, Stimmung)

ANTWORT-FORMAT (JSON):
{{
    "midjourney": "Detailed prompt with parameters --quality 2 --style raw",
    "dalle3": "Clear descriptive prompt for DALL-E 3",
    "stable_diffusion": "prompt, --quality high, --negative low quality",
    "color_palette": ["#FF6B6B", "#4ECDC4", "#FFE66D", "#95E1D3", "#000000"],
    "design_notes": "Composition, focal point, mood, technical details",
    "dimensions": "{dim}",
    "suggestions": ["variation 1", "variation 2", "variation 3"]
}}
"""
        
        try:
            completion = client.chat.completions.create(
                model="local-model",
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = completion.choices[0].message.content
            
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                prompts = json.loads(json_match.group())
            else:
                prompts = json.loads(response_text)
            
            return prompts
        except Exception as e:
            print(f"[-] Fehler bei Bild-Prompt-Generierung: {e}")
            return None
    
    def generate_caption(self, topic, platform="instagram", engagement_goal="reach"):
        """
        Erzeugt virale Captions optimiert für jede Plattform.
        
        Args:
            topic: Thema/Kontext des Posts
            platform: instagram, tiktok, youtube_shorts, pinterest
            engagement_goal: reach, engagement, conversions, brand_awareness
        
        Returns:
            Dict mit mehreren Caption-Varianten
        """
        print(f"[*] Generiere virale Captions für {platform} ({engagement_goal})...")
        
        platform_specs = {
            "instagram": {
                "max_length": 2200,
                "hashtags": 20,
                "emojis": 5,
                "format": "Hook + Story + CTA + Hashtags"
            },
            "tiktok": {
                "max_length": 150,
                "hashtags": 8,
                "emojis": 3,
                "format": "Hook + CTA + Hashtags"
            },
            "youtube_shorts": {
                "max_length": 5000,
                "hashtags": 15,
                "emojis": 5,
                "format": "Hook + Context + CTA + Hashtags"
            },
            "pinterest": {
                "max_length": 300,
                "hashtags": 5,
                "emojis": 2,
                "format": "Hook + Value Prop + CTA"
            }
        }
        
        specs = platform_specs.get(platform, platform_specs["instagram"])
        
        prompt = f"""
Du bist ein Master-Copywriter für Viral-Marketing auf Social Media.
Erstelle MEHRERE hochkonvertierende Captions für diesen Post.

KONTEXT:
- Thema: {topic}
- Plattform: {platform}
- Ziel: {engagement_goal}
- Zielgruppe: Young Adults & Millennials
- Max. Länge: {specs['max_length']} Zeichen
- Hashtags: ~{specs['hashtags']}
- Emojis: ~{specs['emojis']}

ENGAGEMENT-ZIELE:
- reach: Maximale Sichtbarkeit (Neugier, Share-würdig)
- engagement: Likes, Comments, Shares (emotionales Engagement)
- conversions: Click-Through & Sales (Urgency, Value, CTA)
- brand_awareness: Marken-Präsenz (Authentizität, Community-Building)

MENSCHLICHE VARIATION (WICHTIG):
- Nicht überperfekt schreiben, sondern natürlich
- Satzlängen sichtbar mischen (kurz/mittel/lang)
- Emoji-Verwendung variieren (Menge + Position)
- Stil pro Variante leicht verändern (direkt, story, erklärend)
- Caption-Längen nicht immer gleich
- Hashtag-Empfehlungen nicht maximal/perfekt ausoptimieren

ANTWORT-FORMAT (JSON):
{{
    "high_engagement": "Caption variant that drives comments & shares",
    "viral_hook": "Caption variant with strong curiosity hook",
    "sales_focused": "Caption variant optimized for conversions/clicks",
    "community_building": "Caption variant for brand loyalty",
    "trending_angle": "Caption using trending elements/formats",
    "all_variants": [
        {{"text": "Caption 1", "tone": "tone", "expected_engagement": "type"}},
        {{"text": "Caption 2", "tone": "tone", "expected_engagement": "type"}}
    ],
    "hashtag_recommendations": {{
        "trending": ["#trend1", "#trend2"],
        "niche": ["#niche1", "#niche2"],
        "branded": ["#brand1", "#brand2"]
    }},
    "emoji_suggestions": ["🚀", "💡", "✨"],
    "posting_time_tips": "Best times to post on {platform}",
    "platform_specific_tips": "Format hints for {platform}"
}}
"""
        
        try:
            completion = client.chat.completions.create(
                model="local-model",
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = completion.choices[0].message.content
            
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                captions = json.loads(json_match.group())
            else:
                captions = json.loads(response_text)

            return self._apply_human_variability(captions, platform)
        except Exception as e:
            print(f"[-] Fehler bei Caption-Generierung: {e}")
            return None

    def _apply_human_variability(self, captions, platform):
        """
        Bricht KI-Perfektion leicht auf:
        - variiert Caption-Längen
        - mischt Satzstrukturen
        - verteilt Emojis ungleichmäßig
        - erzeugt selten kleine natürliche Vertipper
        - reduziert Hashtag-Perfektion
        """
        if not isinstance(captions, dict):
            return captions

        emoji_pool = captions.get("emoji_suggestions", ["🚀", "✨", "💡", "🔥", "🤝", "📈"])
        text_keys = ["high_engagement", "viral_hook", "sales_focused", "community_building", "trending_angle"]

        for key in text_keys:
            if isinstance(captions.get(key), str):
                captions[key] = self._humanize_caption_text(captions[key], platform, emoji_pool)

        all_variants = captions.get("all_variants", [])
        if isinstance(all_variants, list):
            for idx, variant in enumerate(all_variants):
                if isinstance(variant, dict) and isinstance(variant.get("text"), str):
                    variant["text"] = self._humanize_caption_text(variant["text"], platform, emoji_pool)
                    variant["length_profile"] = self._pick_length_profile(platform, idx)

        hashtags = captions.get("hashtag_recommendations")
        if isinstance(hashtags, dict):
            for group_name, values in hashtags.items():
                if isinstance(values, list):
                    random.shuffle(values)
                    keep = max(1, int(len(values) * random.uniform(0.55, 0.9)))
                    hashtags[group_name] = values[:keep]

        captions["humanization_notes"] = {
            "orthografie": "leichte natürliche Variation aktiv",
            "emoji_variation": "Menge und Position variieren pro Variante",
            "stil_rotation": "direkt / story / erklärend",
            "hashtag_perfection_break": True
        }
        return captions

    def _pick_length_profile(self, platform, salt=0):
        if platform == "tiktok":
            options = ["kurz", "kurz", "mittel"]
        elif platform == "pinterest":
            options = ["kurz", "mittel"]
        else:
            options = ["kurz", "mittel", "lang"]
        return options[salt % len(options)]

    def _humanize_caption_text(self, text, platform, emoji_pool):
        profile = random.choice(["kurz", "mittel", "lang"] if platform != "tiktok" else ["kurz", "mittel"])
        output = self._vary_sentence_flow(text)
        output = self._adjust_caption_length(output, profile)
        output = self._add_emoji_variation(output, emoji_pool, profile)
        output = self._inject_minor_typo(output)
        return output.strip()

    def _vary_sentence_flow(self, text):
        parts = [p.strip() for p in re.split(r'(?<=[.!?])\s+', text) if p.strip()]
        if len(parts) < 2:
            return text

        if random.random() < 0.45:
            random.shuffle(parts)
        if random.random() < 0.35:
            parts.insert(0, random.choice(["Ehrlich gesagt.", "Kurzer Realtalk.", "Ganz simpel:"]))
        return " ".join(parts)

    def _adjust_caption_length(self, text, profile):
        targets = {
            "kurz": (80, 150),
            "mittel": (170, 320),
            "lang": (350, 560)
        }
        min_len, max_len = targets[profile]

        if len(text) > max_len:
            cut = text[:max_len]
            last_stop = max(cut.rfind("."), cut.rfind("!"), cut.rfind("?"))
            if last_stop > int(min_len * 0.7):
                cut = cut[:last_stop + 1]
            text = cut.rstrip()

        if len(text) < min_len:
            fillers = [
                "Wenn du magst, zeig ich im nächsten Post ein konkretes Beispiel.",
                "Schreib mir kurz, ob du dazu einen Deep-Dive willst.",
                "Ich teste das gerade live im Alltag und teile die Ergebnisse."
            ]
            while len(text) < min_len and fillers:
                text = f"{text} {fillers.pop(0)}".strip()

        return text

    def _add_emoji_variation(self, text, emoji_pool, profile):
        if not emoji_pool:
            return text

        emoji_limits = {"kurz": (0, 2), "mittel": (1, 3), "lang": (1, 4)}
        low, high = emoji_limits[profile]
        count = random.randint(low, high)
        if count == 0:
            return text

        emojis = random.sample(emoji_pool, min(count, len(emoji_pool)))
        placement = random.choice(["end", "start", "mixed"])

        if placement == "start":
            return f"{' '.join(emojis)} {text}"
        if placement == "end":
            return f"{text} {' '.join(emojis)}"

        chunks = text.split(" ")
        if len(chunks) > 6:
            pos = random.randint(3, len(chunks) - 2)
            chunks.insert(pos, random.choice(emojis))
            return " ".join(chunks) + f" {random.choice(emojis)}"
        return f"{text} {' '.join(emojis)}"

    def _inject_minor_typo(self, text):
        # Nur selten, damit es natürlich bleibt
        if random.random() > 0.22:
            return text

        words = text.split()
        candidates = [i for i, w in enumerate(words) if len(w) > 5 and w.isalpha()]
        if not candidates:
            return text

        idx = random.choice(candidates)
        word = words[idx]
        if len(word) < 6:
            return text

        typo_mode = random.choice(["drop", "swap"])
        pos = random.randint(1, len(word) - 2)

        if typo_mode == "drop":
            broken = word[:pos] + word[pos + 1:]
        else:
            chars = list(word)
            chars[pos], chars[pos - 1] = chars[pos - 1], chars[pos]
            broken = "".join(chars)

        words[idx] = broken
        return " ".join(words)

    def _choose_video_duration(self, platform, requested_duration):
        """
        Wählt pro Generierung eine leicht andere Videolänge.
        """
        presets = {
            "tiktok": [15, 22, 28, 35, 42, 55],
            "instagram_reels": [18, 24, 30, 38, 46, 58],
            "youtube_shorts": [20, 28, 35, 45, 52, 60]
        }
        options = presets.get(platform, [requested_duration, 24, 30, 40, 50])
        if requested_duration not in options:
            options.append(requested_duration)
        return random.choice(options)

    def _pick_video_variation_profile(self, platform):
        """
        Liefert zufällige Variations-Profile für Musik, Schnitt, Filter, Thumbnail und Hook-Struktur.
        """
        music_styles = ["Lo-Fi Minimal", "Trend-Pop Cut", "Cinematic Bass", "Acoustic Warm", "Tech Pulse"]
        edit_styles = ["Schnell mit Jump-Cuts", "Rhythmisch mit Beat-Cuts", "Clean mit Hard-Cuts", "Punch-In Zoom-Mix", "Story mit ruhigen Übergängen"]
        filters = ["Kontrast Neon", "Warm & Soft", "Clean Natural", "Film Grain Light", "High Clarity Cool"]
        thumbnails = ["Close-Up mit Bold-Text", "Before/After Split", "Minimal mit Key-Keyword", "Emotion-Face + 2-Wort-Hook", "Dark-Contrast mit Neon-Accent"]
        hook_structures = [
            "Problem -> überraschende Lösung",
            "Mythos -> Reality Check",
            "Bold Statement -> Beweis",
            "Mini-Story -> Erkenntnis",
            "Frage -> schnelle Antwort"
        ]

        return {
            "platform": platform,
            "music_style": random.choice(music_styles),
            "editing_style": random.choice(edit_styles),
            "filter_style": random.choice(filters),
            "thumbnail_style": random.choice(thumbnails),
            "hook_structure": random.choice(hook_structures)
        }

    def _apply_video_variability(self, concept, profile, chosen_duration):
        """
        Ergänzt/normalisiert Video-Konzept um menschlich wirkende Produktions-Variabilität.
        """
        if not isinstance(concept, dict):
            concept = {}

        concept["duration_seconds"] = chosen_duration
        concept["hook_structure"] = profile["hook_structure"]
        concept["editing_style"] = profile["editing_style"]
        concept["filter_style"] = profile["filter_style"]
        concept["thumbnail_style"] = profile["thumbnail_style"]

        music = concept.get("music", {})
        if not isinstance(music, dict):
            music = {}
        music.setdefault("mood", profile["music_style"])
        music.setdefault("notes", f"Variation aktiv: {profile['music_style']} für abwechslungsreichen Feed-Mix.")
        concept["music"] = music

        tips = concept.get("editing_tips", "")
        if not isinstance(tips, str):
            tips = ""
        extra_tips = (
            f"Primärer Schnittstil: {profile['editing_style']}. "
            f"Filter: {profile['filter_style']}. "
            f"Thumbnail: {profile['thumbnail_style']}."
        )
        concept["editing_tips"] = f"{tips} {extra_tips}".strip()

        concept["variation_profile"] = {
            "music": profile["music_style"],
            "schnitt": profile["editing_style"],
            "filter": profile["filter_style"],
            "thumbnail": profile["thumbnail_style"],
            "hook": profile["hook_structure"],
            "duration_seconds": chosen_duration
        }
        return concept
    
    def generate_hashtag_bundle(self, topic, niche="general", platforms=None):
        """
        Erstellt optimierte Hashtag-Bündel mit Mix aus Trending + Nische.
        
        Args:
            topic: Haupt-Thema
            niche: Art des Inhalts (tech, lifestyle, beauty, business, etc.)
            platforms: Liste von Plattformen für die Optimiert werden soll
        
        Returns:
            Dict mit Hashtag-Strategien pro Plattform
        """
        if platforms is None:
            platforms = ["instagram", "tiktok", "youtube", "pinterest"]
        
        print(f"[*] Generiere Hashtag-Bundle für {topic} ({niche})...")
        
        prompt = f"""
Du bist ein Hashtag-Strategist mit Expertise in virallem Wachstum.
Erstelle optimierte Hashtag-Bündel für dieses Thema.

KONTEXT:
- Thema: {topic}
- Nische: {niche}
- Zielplattformen: {', '.join(platforms)}

STRATEGIE:
Kombiniere:
1. TRENDING HASHTAGS (aktuell viral, hohe Reichweite)
2. NICHE HASHTAGS (spezialisiert, hohe Engagement-Rate)
3. BRANDED HASHTAGS (branded, Community-Building)
4. LONG-TAIL HASHTAGS (spezifisch, geringer Wettbewerb)

QUALITÄTS-METRIKEN:
- Balance zwischen Popularität und Nischen-Fokus
- Mix: 30% Trending, 40% Niche, 20% Long-Tail, 10% Branded
- Plattform-spezifisch optimiert

ANTWORT-FORMAT (JSON):
{{
    "instagram": {{
        "trending": ["#trend1", "#trend2", "#trend3", "#trend4", "#trend5"],
        "niche": ["#niche1", "#niche2", "#niche3", "#niche4", "#niche5", "#niche6"],
        "long_tail": ["#long1", "#long2", "#long3"],
        "branded": ["#brand1", "#brand2"],
        "complete_set": "#complete #hashtag #bundle",
        "total_count": 20,
        "engagement_prediction": "high/medium/low",
        "competition_level": "high/medium/low"
    }},
    "tiktok": {{
        "trending": ["#trend1", "#trend2", "#trend3"],
        "niche": ["#niche1", "#niche2", "#niche3", "#niche4"],
        "challenge": "#challenge_hashtag",
        "complete_set": "#tiktok #hashtags",
        "total_count": 10,
        "virial_potential": "high/medium/low"
    }},
    "youtube_shorts": {{
        "main": ["#shorts", "#short1", "#short2"],
        "niche": ["#niche1", "#niche2"],
        "challenge": "#challenge",
        "total_count": 6
    }},
    "pinterest": {{
        "keywords": ["keyword1", "keyword2", "keyword3"],
        "niche": ["#niche1", "#niche2"],
        "trending": ["#trend1", "#trend2"],
        "total_count": 8
    }},
    "strategy_notes": "Why this mix works, best practices, timing tips",
    "rotation_suggestions": "How to rotate hashtags across posts for max reach",
    "competitor_analysis": "Similar hashtags used by competitors in {niche}"
}}
"""
        
        try:
            completion = client.chat.completions.create(
                model="local-model",
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = completion.choices[0].message.content
            
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                hashtags = json.loads(json_match.group())
            else:
                hashtags = json.loads(response_text)
            
            return hashtags
        except Exception as e:
            print(f"[-] Fehler bei Hashtag-Generierung: {e}")
            return None
    
    def generate_video_concept(self, topic, platform="tiktok", duration=30):
        """
        Erstellt komplettes Video-Konzept mit Storyboard, Schnitt-Plan, Musik.
        
        Args:
            topic: Video-Thema
            platform: tiktok, instagram_reels, youtube_shorts
            duration: Video-Länge in Sekunden
        
        Returns:
            Dict mit vollständigem Video-Konzept
        """
        chosen_duration = self._choose_video_duration(platform, duration)
        profile = self._pick_video_variation_profile(platform)
        print(f"[*] Generiere Video-Konzept für {platform} - {chosen_duration}s...")
        
        prompt = f"""
Du bist ein erfahrener Videoproduktions-Direktor für Viral-Content.
Erstelle ein vollständiges, professionelles Video-Konzept.

SPEZIFIKATIONEN:
- Plattform: {platform}
- Dauer: {chosen_duration} Sekunden
- Thema: {topic}
- Zielgruppe: Social-Media-Nutzer (14-35 Jahre)
- Hook-Struktur (verwenden): {profile['hook_structure']}
- Bevorzugter Musikcharakter: {profile['music_style']}
- Bevorzugter Schnittstil: {profile['editing_style']}
- Filter-Look: {profile['filter_style']}
- Thumbnail-Stil: {profile['thumbnail_style']}

KONZEPT-STRUKTUR:
1. Hook/Opening (erste 2 Sekunden)
2. Storyboard (Frame-by-Frame Beschreibung)
3. Schnitt-Anweisungen (Übergänge, Effekte)
4. Audio-Design (Musik, Voice-Over, SFX)
5. Text/Graphics Overlay (Timing, Stil)
6. CTA & Ending

QUALITÄTS-STANDARDS:
- Schnellschnitt & Dynamik (halten Aufmerksamkeit)
- Mobile-First Format (Vertikalvideo optimiert)
- Trending Audio/Musik (Lizenzfrei empfohlen)
- Klare visueller Fokus (kein Chaos)

ANTWORT-FORMAT (JSON):
{{
    "title": "Video Title/Concept Name",
    "target_audience": "Demographics and psychographics",
    "hook": "First 2 seconds - MUST grab attention",
    "storyboard": [
        {{
            "frame": 1,
            "seconds": "0-2",
            "scene": "Description of visual",
            "action": "Actor/Camera/Graphic action",
            "audio": "Music/VO/SFX",
            "text_overlay": "On-screen text if any",
            "notes": "Technical/creative notes"
        }},
        ...
    ],
    "transitions": [
        {{"from_frame": 1, "to_frame": 2, "type": "cut/fade/zoom/slide"}}
    ],
    "music": {{
        "title": "Song name",
        "artist": "Artist name",
        "mood": "Mood/Genre",
        "timing": "Start and end times",
        "license": "Free or premium",
        "notes": "Why this music works"
    }},
    "graphics_and_overlays": [
        {{"text": "Text content", "start": "0s", "end": "3s", "style": "Font/Color/Size"}}
    ],
    "cta": "Last 2-3 seconds - Clear Call-to-Action",
    "editing_tips": "Speed ramping, color grading, effects recommendations",
    "equipment_needed": ["Phone camera", "Lighting", "etc"],
    "estimated_production_time": "X hours",
    "viral_potential": "high/medium/low with reasons"
}}
"""
        
        try:
            completion = client.chat.completions.create(
                model="local-model",
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = completion.choices[0].message.content
            
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                concept = json.loads(json_match.group())
            else:
                concept = json.loads(response_text)

            return self._apply_video_variability(concept, profile, chosen_duration)
        except Exception as e:
            print(f"[-] Fehler bei Video-Konzept-Generierung: {e}")
            return None
    
    def generate_content_bundle(self, topic, platforms=None, include_research=True):
        """
        Generiert ein KOMPLETTES Content-Bundle für ein Thema.
        - Script + Bild-Prompts + Captions + Hashtags + Video-Konzept
        
        Args:
            topic: Haupt-Thema
            platforms: Liste von Zielplattformen
            include_research: Nutze Research-Daten wenn verfügbar
        
        Returns:
            Dict mit all Content Assets
        """
        if platforms is None:
            platforms = ["instagram", "tiktok", "youtube_shorts", "pinterest"]
        
        print(f"\n{'='*60}")
        print(f"[*] GENERIERE CONTENT-BUNDLE FÜR: {topic}")
        print(f"[*] Plattformen: {', '.join(platforms)}")
        print(f"{'='*60}\n")
        
        bundle = {
            "topic": topic,
            "timestamp": self.timestamp,
            "platforms": platforms,
            "assets": {}
        }
        
        bundle["script"] = self.generate_script(topic, duration_seconds=30)
        bundle["image_prompts"] = {}
        bundle["captions"] = {}
        bundle["hashtags"] = {}
        bundle["video_concept"] = self.generate_video_concept(topic)
        
        for platform in platforms:
            bundle["image_prompts"][platform] = self.generate_image_prompt(topic, platform=platform)
            bundle["captions"][platform] = self.generate_caption(topic, platform=platform)
            bundle["hashtags"][platform] = self.generate_hashtag_bundle(topic, platforms=[platform])
        
        bundle["created_at"] = datetime.now().isoformat()
        bundle["usage_instructions"] = {
            "script": "Use as basis for video voiceover and timing",
            "image_prompts": "Copy/paste into DALL-E, Midjourney, or Stable Diffusion",
            "captions": "Adapt based on platform-specific trending elements",
            "hashtags": "Rotate hashtags across posts for maximum reach",
            "video_concept": "Follow storyboard for consistent production"
        }
        
        return bundle
    
    def save_bundle_to_sheet(self, bundle, spreadsheet_name="CashBot_Content"):
        """
        Speichert generierte Content-Assets in Google Sheets zur Verwaltung.
        """
        try:
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            
            if not os.path.exists("credentials.json"):
                print("[-] Fehler: 'credentials.json' nicht gefunden")
                return False
            
            creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
            gc = gspread.authorize(creds)
            
            sheet = gc.open(spreadsheet_name).sheet1
            
            row_data = [
                bundle["topic"],
                json.dumps(bundle["script"]),
                json.dumps(bundle["image_prompts"]),
                json.dumps(bundle["captions"]),
                json.dumps(bundle["hashtags"]),
                json.dumps(bundle["video_concept"]),
                bundle["created_at"],
                "Pending"
            ]
            
            sheet.append_row(row_data)
            print(f"[+] Content-Bundle in Google Sheets gespeichert: {spreadsheet_name}")
            return True
        except Exception as e:
            print(f"[-] Fehler beim Speichern in Google Sheets: {e}")
            return False
    
    def export_bundle(self, bundle, format="json"):
        """
        Exportiert Content-Bundle in verschiedene Formate.
        
        Args:
            bundle: Das Content-Bundle
            format: json, markdown, csv
        
        Returns:
            Pfad zur exportierten Datei
        """
        topic_slug = bundle["topic"].lower().replace(" ", "_").replace("ä", "ae").replace("ü", "ue").replace("ö", "oe")
        
        if format == "json":
            filepath = os.path.join(self.output_dir, f"bundle_{topic_slug}_{self.timestamp}.json")
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(bundle, f, indent=2, ensure_ascii=False)
            print(f"[+] JSON exportiert: {filepath}")
            return filepath
        
        elif format == "markdown":
            filepath = os.path.join(self.output_dir, f"bundle_{topic_slug}_{self.timestamp}.md")
            md_content = self._bundle_to_markdown(bundle)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(md_content)
            print(f"[+] Markdown exportiert: {filepath}")
            return filepath
        
        return None
    
    def _bundle_to_markdown(self, bundle):
        """Konvertiert Bundle zu Markdown-Format."""
        md = f"""# Content Bundle: {bundle['topic']}
**Erstellt:** {bundle['created_at']}
**Plattformen:** {', '.join(bundle['platforms'])}

---

## 📹 Video-Script
{json.dumps(bundle['script'], indent=2, ensure_ascii=False)}

---

## 🎨 Bild-Prompts
"""
        for platform, prompts in bundle['image_prompts'].items():
            md += f"\n### {platform.upper()}\n"
            md += f"{json.dumps(prompts, indent=2, ensure_ascii=False)}\n"
        
        md += "\n---\n## 📝 Captions\n"
        for platform, captions in bundle['captions'].items():
            md += f"\n### {platform.upper()}\n"
            md += f"{json.dumps(captions, indent=2, ensure_ascii=False)}\n"
        
        md += "\n---\n## #️⃣ Hashtags\n"
        for platform, hashtags in bundle['hashtags'].items():
            md += f"\n### {platform.upper()}\n"
            md += f"{json.dumps(hashtags, indent=2, ensure_ascii=False)}\n"
        
        return md


def main():
    """Demo: Generiere ein Content-Bundle für ein Trend-Thema."""
    
    topics = [
        "AI-Tools für automatisierte Content-Erstellung",
        "Die Top 5 Affiliate-Nischen 2024",
        "TikTok-Trends für Online-Business"
    ]
    
    factory = ContentFactory()
    
    for topic in topics:
        bundle = factory.generate_content_bundle(
            topic=topic,
            platforms=["instagram", "tiktok", "youtube_shorts", "pinterest"],
            include_research=True
        )
        
        factory.export_bundle(bundle, format="json")
        factory.export_bundle(bundle, format="markdown")
        
        print(f"\n[+] Content-Bundle fertiggestellt: {topic}\n")


if __name__ == "__main__":
    main()
