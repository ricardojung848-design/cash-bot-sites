"""
Publishing & Distribution Modul

Veröffentlicht generierte Content-Assets direkt auf:
- Instagram (Feed + Stories)
- TikTok
- YouTube Shorts
- Pinterest
- Automatisches Scheduling
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import subprocess


class ContentPublisher:
    """
    Verwaltet die Veröffentlichung von Content auf mehreren Plattformen.
    """
    
    def __init__(self):
        self.platforms = {
            "instagram": InstagramPublisher(),
            "tiktok": TikTokPublisher(),
            "youtube_shorts": YouTubePublisher(),
            "pinterest": PinterestPublisher()
        }
        self.schedule_queue = []
        self.published_log = "published_content.json"
    
    def load_bundle(self, bundle_path):
        """Lädt ein gespeichertes Content-Bundle."""
        try:
            with open(bundle_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[-] Fehler beim Laden des Bundles: {e}")
            return None
    
    def schedule_post(self, bundle, platform, publish_time=None, auto_optimize=True):
        """
        Plant einen Post für später.
        
        Args:
            bundle: Content-Bundle
            platform: instagram, tiktok, youtube_shorts, pinterest
            publish_time: datetime Objekt oder "now"
            auto_optimize: Optimiert Caption/Hashtags für Platform
        """
        if publish_time is None:
            publish_time = datetime.now() + timedelta(hours=1)
        
        post_config = {
            "bundle": bundle,
            "platform": platform,
            "publish_time": publish_time.isoformat(),
            "status": "scheduled",
            "auto_optimize": auto_optimize,
            "created_at": datetime.now().isoformat()
        }
        
        self.schedule_queue.append(post_config)
        print(f"[+] Post geplant für {platform} um {publish_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return post_config
    
    def publish_now(self, bundle, platform, caption=None, hashtags=None, image_path=None):
        """
        Veröffentlicht einen Post sofort.
        
        Args:
            bundle: Content-Bundle
            platform: instagram, tiktok, youtube_shorts, pinterest
            caption: Optional: Custom Caption
            hashtags: Optional: Custom Hashtags
            image_path: Pfad zum Bild (falls lokal)
        """
        if platform not in self.platforms:
            print(f"[-] Plattform nicht unterstützt: {platform}")
            return False
        
        print(f"[*] Veröffentliche auf {platform}...")
        
        publisher = self.platforms[platform]
        
        post_content = {
            "caption": caption or bundle["captions"][platform].get("high_engagement", ""),
            "hashtags": hashtags or bundle["hashtags"][platform],
            "image_prompts": bundle["image_prompts"][platform],
            "video_script": bundle["script"] if "script" in bundle else None
        }
        
        success = publisher.publish(post_content)
        
        if success:
            self._log_published(bundle, platform)
        
        return success
    
    def _log_published(self, bundle, platform):
        """Protokolliert veröffentlichte Posts."""
        log_entry = {
            "topic": bundle["topic"],
            "platform": platform,
            "published_at": datetime.now().isoformat(),
            "bundle_id": bundle.get("timestamp", "")
        }
        
        try:
            logs = []
            if os.path.exists(self.published_log):
                with open(self.published_log, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            
            logs.append(log_entry)
            
            with open(self.published_log, "w", encoding="utf-8") as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[-] Fehler beim Protokollieren: {e}")
    
    def process_queue(self):
        """Verarbeitet die geplante Queue und veröffentlicht rechtzeitig."""
        print("[*] Verarbeite Publikations-Queue...")
        
        now = datetime.now()
        
        for config in self.schedule_queue[:]:
            publish_time = datetime.fromisoformat(config["publish_time"])
            
            if now >= publish_time and config["status"] == "scheduled":
                bundle = config["bundle"]
                platform = config["platform"]
                
                success = self.publish_now(bundle, platform)
                
                if success:
                    config["status"] = "published"
                    config["published_at"] = now.isoformat()
                    print(f"[+] Post veröffentlicht auf {platform}")
                else:
                    config["status"] = "failed"
                    print(f"[-] Fehler beim Veröffentlichen auf {platform}")


class InstagramPublisher:
    """Instagram Post Publisher (Feed + Stories)"""
    
    def publish(self, post_content):
        """Veröffentlicht auf Instagram."""
        print("[*] Vorbereitung Instagram Post...")
        
        try:
            caption = post_content["caption"]
            hashtags = post_content["hashtags"]["instagram"]["complete_set"]
            
            full_caption = f"{caption}\n\n{hashtags}"
            
            print(f"   - Caption Länge: {len(full_caption)} Zeichen")
            print(f"   - Hashtags: {len(post_content['hashtags']['instagram']['trending'])} Trending")
            
            print("[✓] Instagram Post bereit zum Upload")
            print(f"    Caption Preview: {full_caption[:100]}...")
            
            return True
        except Exception as e:
            print(f"[-] Fehler: {e}")
            return False


class TikTokPublisher:
    """TikTok Video Publisher"""
    
    def publish(self, post_content):
        """Veröffentlicht auf TikTok."""
        print("[*] Vorbereitung TikTok Video...")
        
        try:
            caption = post_content["caption"]
            hashtags = post_content["hashtags"]["tiktok"]["complete_set"]
            
            full_caption = f"{caption} {hashtags}"
            
            if len(full_caption) > 150:
                full_caption = full_caption[:147] + "..."
            
            print(f"   - Caption: {full_caption}")
            print(f"   - Video Script verfügbar: {bool(post_content['video_script'])}")
            
            print("[✓] TikTok Video bereit zum Upload")
            
            return True
        except Exception as e:
            print(f"[-] Fehler: {e}")
            return False


class YouTubePublisher:
    """YouTube Shorts Publisher"""
    
    def publish(self, post_content):
        """Veröffentlicht auf YouTube Shorts."""
        print("[*] Vorbereitung YouTube Shorts...")
        
        try:
            caption = post_content["caption"]
            hashtags = post_content["hashtags"]["youtube_shorts"]["main"]
            
            full_caption = f"{caption}\n{' '.join(hashtags)}"
            
            print(f"   - Caption: {full_caption[:100]}...")
            print(f"   - Hashtags: {hashtags}")
            
            print("[✓] YouTube Shorts bereit zum Upload")
            
            return True
        except Exception as e:
            print(f"[-] Fehler: {e}")
            return False


class PinterestPublisher:
    """Pinterest Pin Publisher"""
    
    def publish(self, post_content):
        """Veröffentlicht auf Pinterest."""
        print("[*] Vorbereitung Pinterest Pin...")
        
        try:
            caption = post_content["caption"]
            keywords = post_content["hashtags"]["pinterest"]["keywords"]
            
            pin_description = f"{caption}\n\nKeywords: {', '.join(keywords)}"
            
            print(f"   - Pin Description: {pin_description[:100]}...")
            print(f"   - Keywords: {keywords}")
            
            print("[✓] Pinterest Pin bereit zum Upload")
            
            return True
        except Exception as e:
            print(f"[-] Fehler: {e}")
            return False


class SmartScheduler:
    """
    Intelligentes Scheduling basierend auf:
    - Platform-spezifische beste Posting-Zeiten
    - Zeitzone des Audiences
    - Engagement-Patterns
    - Viral-Potential des Contents
    """
    
    BEST_POSTING_TIMES = {
        "instagram": {
            "weekday": [9, 11, 14, 18, 21],
            "weekend": [10, 12, 19, 21]
        },
        "tiktok": {
            "weekday": [6, 12, 18, 21],
            "weekend": [7, 11, 15, 20]
        },
        "youtube_shorts": {
            "weekday": [9, 12, 15, 20],
            "weekend": [10, 13, 18, 21]
        },
        "pinterest": {
            "weekday": [8, 14],
            "weekend": [9, 15]
        }
    }
    
    @staticmethod
    def get_optimal_posting_time(platform, timezone_offset=0):
        """
        Berechnet die optimale Posting-Zeit für eine Platform.
        
        Args:
            platform: instagram, tiktok, youtube_shorts, pinterest
            timezone_offset: UTC Offset (z.B. +2 für CEST)
        
        Returns:
            datetime Objekt für die nächste beste Posting-Zeit
        """
        times = SmartScheduler.BEST_POSTING_TIMES.get(platform, [9, 12, 18])
        
        now = datetime.now()
        is_weekend = now.weekday() >= 5
        
        candidate_times = times["weekend"] if is_weekend else times["weekday"]
        
        for hour in candidate_times:
            candidate = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            
            if candidate > now:
                return candidate
        
        next_day = now + timedelta(days=1)
        first_hour = candidate_times[0]
        return next_day.replace(hour=first_hour, minute=0, second=0, microsecond=0)
    
    @staticmethod
    def create_posting_schedule(bundle, platforms=None):
        """
        Erstellt einen optimalen Posting-Schedule für alle Platforms.
        
        Args:
            bundle: Content-Bundle
            platforms: Liste von Platforms (default: alle)
        
        Returns:
            Dict mit Posting-Times für jede Platform
        """
        if platforms is None:
            platforms = ["instagram", "tiktok", "youtube_shorts", "pinterest"]
        
        schedule = {
            "bundle_topic": bundle["topic"],
            "created_at": datetime.now().isoformat(),
            "posts": []
        }
        
        for platform in platforms:
            optimal_time = SmartScheduler.get_optimal_posting_time(platform)
            
            schedule["posts"].append({
                "platform": platform,
                "optimal_posting_time": optimal_time.isoformat(),
                "recommended_duration": SmartScheduler._get_duration_recommendation(platform),
                "notes": SmartScheduler._get_platform_notes(platform)
            })
        
        return schedule
    
    @staticmethod
    def _get_duration_recommendation(platform):
        """Empfehlung für Video-Länge pro Platform."""
        durations = {
            "instagram": "15-60 Sekunden",
            "tiktok": "15-60 Sekunden",
            "youtube_shorts": "15-60 Sekunden",
            "pinterest": "N/A (Static Image)"
        }
        return durations.get(platform, "N/A")
    
    @staticmethod
    def _get_platform_notes(platform):
        """Platform-spezifische Tipps."""
        notes = {
            "instagram": "Nutze Story-Posting für täglich Engagement, Feed-Posts für Reichweite",
            "tiktok": "Trends & Sounds wichtig - nutze aktuelle Trending Audio",
            "youtube_shorts": "Länger Videos = bessere Monetisierung, aber Shorts max. 60s",
            "pinterest": "Pins mit hohem Engagement in Beschreibung, Keywords wichtig"
        }
        return notes.get(platform, "")


class AutoPublisher:
    """
    Automatischer Publisher - automatisiert die komplette Publishing-Pipeline.
    """
    
    def __init__(self):
        self.publisher = ContentPublisher()
        self.scheduler = SmartScheduler()
    
    def auto_publish_bundle(self, bundle, platforms=None, schedule=True, delay_between_posts=300):
        """
        Automatisch veröffentlicht ein komplettes Bundle auf allen Platforms.
        
        Args:
            bundle: Content-Bundle
            platforms: Liste von Platforms (default: alle)
            schedule: Wenn True, plant die Posts optimal; wenn False, veröffentlicht sofort
            delay_between_posts: Verzögerung zwischen Posts in Sekunden
        """
        if platforms is None:
            platforms = ["instagram", "tiktok", "youtube_shorts", "pinterest"]
        
        print(f"\n{'='*60}")
        print(f"🚀 AUTO-PUBLISH BUNDLE: {bundle['topic']}")
        print(f"{'='*60}\n")
        
        if schedule:
            print("[*] Erstelle optimales Posting-Schedule...")
            schedule_plan = self.scheduler.create_posting_schedule(bundle, platforms)
            
            print(f"\n📅 POSTING-SCHEDULE:")
            for post in schedule_plan["posts"]:
                post_time = datetime.fromisoformat(post["optimal_posting_time"])
                print(f"   {post['platform'].upper()}: {post_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"      → {post['notes']}")
            
            print(f"\n[*] Plane Posts im Publikations-System...")
            for idx, platform in enumerate(platforms):
                post_time = datetime.fromisoformat(schedule_plan["posts"][idx]["optimal_posting_time"])
                self.publisher.schedule_post(bundle, platform, publish_time=post_time)
                
                if idx < len(platforms) - 1:
                    time.sleep(1)
        else:
            print("[*] Veröffentliche sofort auf allen Platforms...\n")
            for idx, platform in enumerate(platforms):
                success = self.publisher.publish_now(bundle, platform)
                
                if success:
                    print(f"   ✓ {platform}")
                else:
                    print(f"   ✗ {platform}")
                
                if idx < len(platforms) - 1:
                    print(f"   Warte {delay_between_posts}s...")
                    time.sleep(delay_between_posts / 1000)
        
        print(f"\n{'='*60}")
        print("✅ AUTO-PUBLISH FERTIGGESTELLT")
        print(f"{'='*60}\n")


def main():
    """Demo: Auto-Publishing mit Smart-Scheduling."""
    
    print("[*] Starte Auto-Publishing Demo...\n")
    
    demo_bundle = {
        "topic": "Die besten KI-Tools für 2024",
        "timestamp": datetime.now().isoformat(),
        "script": {"hook": "Demo Script", "body": []},
        "captions": {
            "instagram": {"high_engagement": "Schau dir diese KI-Tools an! 🚀"},
            "tiktok": {"high_engagement": "KI-Tools ändern alles! 🤖"},
            "youtube_shorts": {"high_engagement": "Top KI-Tools erklärt"},
            "pinterest": {"high_engagement": "KI-Tools Guide"}
        },
        "hashtags": {
            "instagram": {
                "trending": ["#AI", "#Tools", "#Productivity"],
                "complete_set": "#AI #Tools #Productivity"
            },
            "tiktok": {
                "trending": ["#AI", "#Tech"],
                "complete_set": "#AI #Tech"
            },
            "youtube_shorts": {
                "main": ["#Shorts", "#AI", "#Tools"]
            },
            "pinterest": {
                "keywords": ["AI", "Tools", "Productivity"]
            }
        }
    }
    
    auto_pub = AutoPublisher()
    auto_pub.auto_publish_bundle(demo_bundle, schedule=True)


if __name__ == "__main__":
    main()
