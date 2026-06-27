"""
Integrations-Modul: Self-Research Engine → Content-Factory

Verbindet die Trend-Recherche mit der automatischen Content-Generierung.
- Recherchierte Trends/Keywords direkt in Content-Assets umwandeln
- A/B-Testing Varianten generieren
- Batch-Processing von Hunderten von Themen
"""

import os
import json
import time
from datetime import datetime, timedelta
from Modul_ContentFactory import ContentFactory
import gspread
from oauth2client.service_account import ServiceAccountCredentials


class ResearchToContentPipeline:
    """
    Pipeline: Trends aus Research → Content-Factory → Google Sheets → Git-Push
    """
    
    def __init__(self, research_sheet="CashBot_Trends", output_sheet="CashBot_Content"):
        self.research_sheet_name = research_sheet
        self.output_sheet_name = output_sheet
        self.factory = ContentFactory()
        self.processed_count = 0
        self.skipped_count = 0
    
    def connect_to_sheets(self):
        """Verbindung zu Google Sheets herstellen."""
        try:
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            
            if not os.path.exists("credentials.json"):
                print("[-] Fehler: 'credentials.json' fehlt!")
                return None
            
            creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
            gc = gspread.authorize(creds)
            return gc
        except Exception as e:
            print(f"[-] Fehler bei Google Sheets Verbindung: {e}")
            return None
    
    def fetch_research_data(self, gc, status_filter="Ready for Content"):
        """
        Holt recherchierte Themen aus dem Research-Sheet.
        
        Args:
            gc: Google Sheets Client
            status_filter: Status der zu verarbeitenden Einträge
        
        Returns:
            Liste von Themen-Dicts
        """
        try:
            sheet = gc.open(self.research_sheet_name).sheet1
            records = sheet.get_all_records()
            
            filtered = [
                r for r in records
                if r.get("Status") == status_filter
            ]
            
            print(f"[+] {len(filtered)} Themen mit Status '{status_filter}' gefunden")
            return filtered
        except Exception as e:
            print(f"[-] Fehler beim Abrufen der Research-Daten: {e}")
            return []
    
    def create_output_sheet_if_needed(self, gc):
        """Erstellt Output-Sheet falls nicht vorhanden."""
        try:
            try:
                gc.open(self.output_sheet_name)
            except gspread.exceptions.SpreadsheetNotFound:
                spreadsheet = gc.create(
                    self.output_sheet_name,
                    {'rows': 1000, 'cols': 10}
                )
                worksheet = spreadsheet.sheet1
                headers = [
                    "Topic",
                    "Script",
                    "Image_Prompts",
                    "Captions_Instagram",
                    "Captions_TikTok",
                    "Hashtags",
                    "Video_Concept",
                    "Status",
                    "Created_At",
                    "Platform_Links"
                ]
                worksheet.append_row(headers)
                print(f"[+] Neues Sheet erstellt: {self.output_sheet_name}")
        except Exception as e:
            print(f"[-] Fehler beim Erstellen des Output-Sheets: {e}")
    
    def process_research_item(self, item):
        """
        Generiert Content-Assets für ein einzelnes Research-Item.
        
        Args:
            item: Dict mit Thema und Kontext aus Research
        
        Returns:
            Content-Bundle oder None
        """
        topic = item.get("Keyword") or item.get("Topic") or item.get("Trend")
        
        if not topic:
            print("[-] Fehler: Kein Thema im Research-Item gefunden")
            return None
        
        print(f"\n[*] Verarbeite: {topic}")
        
        try:
            bundle = self.factory.generate_content_bundle(
                topic=topic,
                platforms=["instagram", "tiktok", "youtube_shorts", "pinterest"]
            )
            
            bundle["research_context"] = {
                "search_volume": item.get("Search_Volume", ""),
                "competition": item.get("Competition", ""),
                "trend_date": item.get("Trend_Date", ""),
                "source": item.get("Source", "")
            }
            
            self.processed_count += 1
            return bundle
        except Exception as e:
            print(f"[-] Fehler bei Content-Generierung für '{topic}': {e}")
            self.skipped_count += 1
            return None
    
    def save_to_output_sheet(self, gc, bundle, research_item):
        """Speichert Content-Bundle im Output-Sheet."""
        try:
            sheet = gc.open(self.output_sheet_name).sheet1
            
            row_data = [
                bundle["topic"],
                json.dumps(bundle.get("script", {})),
                json.dumps(bundle.get("image_prompts", {})),
                json.dumps(bundle.get("captions", {}).get("instagram", {})),
                json.dumps(bundle.get("captions", {}).get("tiktok", {})),
                json.dumps(bundle.get("hashtags", {})),
                json.dumps(bundle.get("video_concept", {})),
                "Ready for Publication",
                datetime.now().isoformat(),
                f"https://research.example.com/content/{bundle['topic']}"
            ]
            
            sheet.append_row(row_data)
            print(f"[+] Gespeichert in Output-Sheet: {bundle['topic']}")
            return True
        except Exception as e:
            print(f"[-] Fehler beim Speichern in Sheet: {e}")
            return False
    
    def run_pipeline(self, batch_size=None, delay_between_items=2):
        """
        Führt die komplette Pipeline aus.
        
        Args:
            batch_size: Maximale Anzahl zu verarbeitender Items (None = alle)
            delay_between_items: Verzögerung zwischen Items (API-Rate-Limit)
        """
        print("\n" + "="*70)
        print("🚀 RESEARCH-TO-CONTENT PIPELINE GESTARTET")
        print("="*70 + "\n")
        
        gc = self.connect_to_sheets()
        if not gc:
            print("[-] Pipeline abgebrochen: Google Sheets nicht verfügbar")
            return False
        
        self.create_output_sheet_if_needed(gc)
        
        research_items = self.fetch_research_data(gc, status_filter="Ready for Content")
        
        if batch_size:
            research_items = research_items[:batch_size]
        
        print(f"[*] Starte Content-Generierung für {len(research_items)} Themen...\n")
        
        for idx, item in enumerate(research_items, 1):
            print(f"\n[{idx}/{len(research_items)}] Verarbeite Research-Item...")
            
            bundle = self.process_research_item(item)
            
            if bundle:
                self.save_to_output_sheet(gc, bundle, item)
                self.factory.export_bundle(bundle, format="json")
                self.factory.export_bundle(bundle, format="markdown")
            
            if idx < len(research_items):
                print(f"[*] Warte {delay_between_items}s vor nächstem Item (API-Rate-Limiting)...")
                time.sleep(delay_between_items)
        
        print("\n" + "="*70)
        print(f"✅ PIPELINE FERTIGGESTELLT")
        print(f"   Verarbeitet: {self.processed_count}")
        print(f"   Übersprungen: {self.skipped_count}")
        print("="*70 + "\n")
        
        return True
    
    def generate_performance_report(self, gc):
        """Generiert einen Report über die Content-Performance."""
        try:
            sheet = gc.open(self.output_sheet_name).sheet1
            records = sheet.get_all_records()
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "total_content_assets": len(records),
                "by_status": {},
                "by_platform": {
                    "instagram": 0,
                    "tiktok": 0,
                    "youtube_shorts": 0,
                    "pinterest": 0
                },
                "recent_items": []
            }
            
            for record in records:
                status = record.get("Status", "Unknown")
                report["by_status"][status] = report["by_status"].get(status, 0) + 1
            
            recent = sorted(
                records,
                key=lambda x: x.get("Created_At", ""),
                reverse=True
            )[:5]
            
            report["recent_items"] = [{"topic": r.get("Topic"), "created": r.get("Created_At")} for r in recent]
            
            return report
        except Exception as e:
            print(f"[-] Fehler beim Generieren des Reports: {e}")
            return None


class ABTestContentVariants:
    """
    A/B-Testing für generierte Content-Assets.
    - Mehrere Varianten pro Thema
    - Performance-Tracking
    """
    
    def __init__(self):
        self.factory = ContentFactory()
        self.variants_dir = "content_variants"
        os.makedirs(self.variants_dir, exist_ok=True)
    
    def generate_ab_variants(self, topic, num_variants=3):
        """
        Generiert mehrere Content-Varianten für A/B-Testing.
        
        Args:
            topic: Thema
            num_variants: Anzahl der zu generierenden Varianten
        
        Returns:
            Dict mit Varianten-Bundles
        """
        print(f"\n[*] Generiere {num_variants} A/B-Test Varianten für: {topic}")
        
        variants = {
            "topic": topic,
            "num_variants": num_variants,
            "variants": [],
            "comparison_notes": ""
        }
        
        for i in range(num_variants):
            print(f"   - Variante {i+1}/{num_variants}...")
            
            bundle = self.factory.generate_content_bundle(topic)
            bundle["variant_id"] = f"variant_{i+1}"
            bundle["variant_number"] = i + 1
            
            variants["variants"].append(bundle)
        
        variants["comparison_guide"] = self._generate_comparison_guide(variants)
        
        self._save_variants(topic, variants)
        
        return variants
    
    def _generate_comparison_guide(self, variants):
        """Erstellt einen Vergleichs-Guide für die Varianten."""
        guide = f"""
# A/B-Test Vergleichsguide: {variants['topic']}

## Varianten-Übersicht
"""
        
        for v in variants["variants"]:
            if isinstance(v.get("captions"), dict):
                ig_caption = v.get("captions", {}).get("instagram", {}).get("high_engagement", "")[:50] + "..."
            else:
                ig_caption = "N/A"
            
            guide += f"\n### {v.get('variant_id')}\n"
            guide += f"- Instagram Caption: {ig_caption}\n"
            guide += f"- Hashtags: {len(v.get('hashtags', {}).get('instagram', {}).get('trending', []))} Trending\n"
        
        guide += """

## Test-Strategie
1. Poste alle 3 Varianten innerhalb von 24 Stunden
2. Monitore: Engagement Rate, Click-Through Rate, Reach
3. Nach 48 Stunden: Best-Performer skalieren

## Metriken zum Tracken
- Likes/Reactions
- Comments (Engagement Quality)
- Shares
- Saves
- CTR (Click-Through Rate)
- Time Spent
"""
        
        return guide
    
    def _save_variants(self, topic, variants):
        """Speichert Varianten als JSON-Dateien."""
        topic_slug = topic.lower().replace(" ", "_")
        filepath = os.path.join(self.variants_dir, f"ab_test_{topic_slug}.json")
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(variants, f, indent=2, ensure_ascii=False)
        
        print(f"[+] A/B-Test Varianten gespeichert: {filepath}")


def main():
    """Demo: Starte die komplette Pipeline."""
    
    print("\n" + "="*70)
    print("🔧 INTIALISIERE RESEARCH-TO-CONTENT PIPELINE")
    print("="*70)
    
    pipeline = ResearchToContentPipeline(
        research_sheet="CashBot_Trends",
        output_sheet="CashBot_Content"
    )
    
    pipeline.run_pipeline(batch_size=5, delay_between_items=3)
    
    print("\n[*] Demo A/B-Testing...")
    ab_tester = ABTestContentVariants()
    ab_tester.generate_ab_variants("KI-Tools für Content-Erstellung", num_variants=3)
    
    print("\n✅ Alles fertiggestellt!")


if __name__ == "__main__":
    main()
