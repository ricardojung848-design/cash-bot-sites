"""
Tracking Link Manager
Verwaltet Affiliate-Links mit UTM-Parametern und Analytics
"""
import uuid
import hashlib
from datetime import datetime
from typing import Dict, List
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from affiliate_engine.db.database import AffiliateDatabase
from affiliate_engine.config import TRACKING_CONFIG

class TrackingLinkManager:
    """Verwaltet Affiliate-Links und Tracking"""
    
    def __init__(self):
        self.db = AffiliateDatabase()
        self.config = TRACKING_CONFIG

    def create_tracking_link(self, landing_page_id: int, program_id: int,
                            original_url: str, campaign_name: str) -> Dict:
        """
        Erstelle Tracking-Link mit UTM-Parametern
        
        Args:
            landing_page_id: ID der Landing Page
            program_id: ID des Affiliate-Programms
            original_url: Originale Affiliate-URL
            campaign_name: Name der Kampagne
        
        Returns:
            Dict mit Tracking-Link und Metadaten
        """
        
        if not self.config["enable_utm_params"]:
            return {
                "tracking_link": original_url,
                "utm_enabled": False,
                "status": "ok"
            }
        
        # 1. Baue UTM-Parameter
        utm_params = {
            "utm_source": self.config["utm_source"],
            "utm_medium": self.config["utm_medium"],
            "utm_campaign": campaign_name,
            "utm_content": f"lp_{landing_page_id}",
        }
        
        # 2. Generiere Tracking-Link
        tracking_link = self._add_utm_to_url(original_url, utm_params)
        
        # 3. Speichere in Datenbank
        link_id = self.db.add_tracking_link(
            landing_page_id=landing_page_id,
            prog_id=program_id,
            original=original_url,
            tracking=tracking_link,
            utm_source=utm_params["utm_source"],
            utm_medium=utm_params["utm_medium"],
            utm_campaign=utm_params["utm_campaign"],
            utm_content=utm_params["utm_content"],
        )
        
        # 4. Optional: Link-Verkürzung
        short_link = None
        if self.config["enable_link_shortening"]:
            short_link = self._create_short_link(tracking_link)
        
        return {
            "id": link_id,
            "original_url": original_url,
            "tracking_link": tracking_link,
            "short_link": short_link,
            "utm_params": utm_params,
            "status": "created",
            "timestamp": datetime.now().isoformat(),
        }

    def _add_utm_to_url(self, url: str, utm_params: Dict) -> str:
        """Füge UTM-Parameter zu URL hinzu"""
        parsed = urlparse(url)
        
        # Parsing bestehende Parameter
        query_params = parse_qs(parsed.query, keep_blank_values=True)
        
        # Füge UTM-Parameter hinzu (flatten dict)
        for key, value in utm_params.items():
            query_params[key] = [value]
        
        # Rebuild URL
        new_query = urlencode(query_params, doseq=True)
        new_parsed = parsed._replace(query=new_query)
        
        return urlunparse(new_parsed)

    def _create_short_link(self, url: str) -> str:
        """Erstelle verkürzten Link (Placeholder)"""
        # Dies würde externe Service wie bit.ly oder custom Short-URL verwenden
        hash_obj = hashlib.sha256(url.encode())
        short_code = hash_obj.hexdigest()[:8]
        return f"https://aff.short/{short_code}"

    def get_tracking_link(self, link_id: int) -> Dict:
        """Hole Tracking-Link Details"""
        links = self.db.get_tracking_links(link_id)
        if links:
            return dict(links[0])
        return None

    def register_click(self, link_id: int) -> Dict:
        """Registriere Click auf Link"""
        self.db.log_click(link_id)
        
        return {
            "link_id": link_id,
            "event": "click",
            "timestamp": datetime.now().isoformat(),
            "status": "recorded"
        }

    def register_conversion(self, link_id: int, revenue: float = 0.0) -> Dict:
        """Registriere Conversion"""
        self.db.log_conversion(link_id, revenue)
        
        return {
            "link_id": link_id,
            "event": "conversion",
            "revenue": revenue,
            "timestamp": datetime.now().isoformat(),
            "status": "recorded"
        }

    def get_link_stats(self, link_id: int) -> Dict:
        """Hole Stats für einen Link"""
        link = self.get_tracking_link(link_id)
        
        if not link:
            return {"error": "Link nicht gefunden"}
        
        return {
            "link_id": link_id,
            "original_url": link.get("original_link"),
            "tracking_link": link.get("tracking_link"),
            "clicks": link.get("clicks", 0),
            "conversions": link.get("conversions", 0),
            "revenue": link.get("revenue", 0),
            "conversion_rate": (link.get("conversions", 0) / max(link.get("clicks", 1), 1)) * 100,
            "created_at": link.get("created_at"),
        }

    def generate_html_with_tracking(self, landing_page_id: int, 
                                   html_content: str, 
                                   tracking_links: Dict[str, str]) -> str:
        """
        Ersetze Links in HTML mit Tracking-Links
        
        Args:
            landing_page_id: ID der LP
            html_content: Ursprünglicher HTML
            tracking_links: Dict von {original_url: tracking_url}
        
        Returns:
            HTML mit eingebetteten Tracking-Links
        """
        
        modified_html = html_content
        
        # Ersetze alle Links
        for original, tracking in tracking_links.items():
            # Ersetze in href-Attributen
            modified_html = modified_html.replace(f'href="{original}"', f'href="{tracking}"')
            modified_html = modified_html.replace(f"href='{original}'", f"href='{tracking}'")
        
        # Optional: Tracking-Pixel hinzufügen
        if self.config.get("enable_pixel_tracking"):
            pixel_html = self._get_tracking_pixel_html(landing_page_id)
            # Füge Pixel vor </body> ein
            modified_html = modified_html.replace("</body>", f"{pixel_html}\n</body>")
        
        return modified_html

    def _get_tracking_pixel_html(self, landing_page_id: int) -> str:
        """Erstelle Tracking-Pixel HTML"""
        pixel_url = f"https://tracking.affiliate-engine.local/pixel?lp={landing_page_id}"
        return f'<img src="{pixel_url}" alt="" style="display:none;width:1px;height:1px;">'

    def create_bulk_tracking_links(self, landing_page_id: int, 
                                  programs: List[Dict], 
                                  campaign_name: str) -> List[Dict]:
        """Erstelle Tracking-Links für mehrere Programme"""
        results = []
        
        for program in programs:
            # Generiere Link basierend auf Programm
            program_link = self._get_program_link(program)
            
            result = self.create_tracking_link(
                landing_page_id=landing_page_id,
                program_id=program.get("id", 0),
                original_url=program_link,
                campaign_name=campaign_name,
            )
            results.append(result)
        
        return results

    def _get_program_link(self, program: Dict) -> str:
        """Generiere Link für Programm"""
        program_name = program.get("name", "").lower()
        
        if program_name == "amazon":
            return f"https://www.amazon.de/dp/ASIN?tag=YOUR_TAG"
        elif program_name == "digistore24":
            return f"https://www.digistore24.com/product/YOUR_PRODUCT_ID"
        elif program_name == "awin":
            return f"https://www.awin1.com/awclick.php?mid=MERCHANT_ID&id=PUBLISHER_ID"
        else:
            return "https://example.com"

    def get_analytics(self, landing_page_id: int = None, days: int = 30) -> Dict:
        """Hole Analytics-Daten"""
        analytics = self.db.get_analytics(days)
        
        return {
            "period_days": days,
            "total_clicks": analytics.get("total_clicks", 0),
            "total_conversions": analytics.get("total_conversions", 0),
            "total_revenue": analytics.get("total_revenue", 0),
            "active_pages": analytics.get("active_pages", 0),
            "avg_conversion_rate": "~2-5%" if analytics.get("total_clicks", 0) > 0 else "N/A",
            "timestamp": datetime.now().isoformat(),
        }

if __name__ == "__main__":
    manager = TrackingLinkManager()
    
    # Test
    result = manager.create_tracking_link(
        landing_page_id=1,
        program_id=1,
        original_url="https://www.amazon.de/dp/B123456789",
        campaign_name="SEO-Engine-Test"
    )
    
    print("[✓] Tracking-Link erstellt:")
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
