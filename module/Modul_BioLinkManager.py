"""
💰 Affiliate Link Manager & Bio-Link Optimizer

Pipeline 1: Social Media Reels → Bio-Link (Optimiert) → Affiliate-Einnahmen
- Dynamische Bio-Link Verwaltung
- A/B Testing für CTR
- Click Tracking & Attribution
- Revenue Reporting
"""

import os
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from urllib.parse import urlencode, quote
import secrets


class AffiliateLink:
    """Repräsentiert einen Affiliate-Link mit Tracking & Metadata."""
    
    def __init__(self, 
                 url: str, 
                 affiliate_id: str,
                 program: str,
                 niche: str,
                 campaign_name: str = ""):
        
        self.url = url
        self.affiliate_id = affiliate_id
        self.program = program  # Amazon, CJ Affiliate, ShareASale, etc.
        self.niche = niche
        self.campaign_name = campaign_name
        self.short_code = secrets.token_urlsafe(6)
        self.created_at = datetime.now().isoformat()
        self.click_count = 0
        self.conversion_count = 0
        self.revenue_earned = 0.0
        self.last_clicked = None
    
    def generate_tracking_url(self, platform: str = "default", 
                             source: str = "bio_link") -> str:
        """
        Generiert einen Tracking-URL mit UTM-Parametern.
        
        Args:
            platform: instagram, tiktok, youtube, pinterest
            source: bio_link, direct, email, etc.
        
        Returns:
            Vollständiger URL mit Tracking
        """
        
        utms = {
            'utm_source': platform,
            'utm_medium': source,
            'utm_campaign': self.campaign_name or self.niche,
            'utm_content': self.short_code,
            'ref': self.affiliate_id
        }
        
        separator = '&' if '?' in self.url else '?'
        tracking_url = self.url + separator + urlencode(utms)
        
        return tracking_url
    
    def register_click(self, platform: str = "unknown"):
        """Protokolliert einen Click auf den Link."""
        self.click_count += 1
        self.last_clicked = datetime.now().isoformat()
        return {
            "platform": platform,
            "timestamp": self.last_clicked,
            "total_clicks": self.click_count
        }
    
    def register_conversion(self, amount: float):
        """Protokolliert eine Conversion & Revenue."""
        self.conversion_count += 1
        self.revenue_earned += amount
        return {
            "amount": amount,
            "total_revenue": self.revenue_earned,
            "conversion_count": self.conversion_count
        }
    
    def to_dict(self) -> Dict:
        """Konvertiert zu Dictionary für Speicherung."""
        return {
            "url": self.url,
            "affiliate_id": self.affiliate_id,
            "program": self.program,
            "niche": self.niche,
            "campaign_name": self.campaign_name,
            "short_code": self.short_code,
            "created_at": self.created_at,
            "click_count": self.click_count,
            "conversion_count": self.conversion_count,
            "revenue_earned": self.revenue_earned,
            "last_clicked": self.last_clicked,
            "ctr": round(self.conversion_count / max(self.click_count, 1) * 100, 2),
            "avg_revenue_per_click": round(self.revenue_earned / max(self.click_count, 1), 2)
        }


class BioLinkManager:
    """
    Verwaltet die Bio-Link Landing Page für Instagram/TikTok.
    - Dynamische Link-Verwaltung
    - A/B Testing verschiedener Layouts
    - Click Tracking
    - Revenue Reporting
    """
    
    def __init__(self, account_name: str = "cashbot"):
        self.account_name = account_name
        self.links: Dict[str, AffiliateLink] = {}
        self.bio_link_data = {
            "account_name": account_name,
            "title": "🚀 Deine Chance auf Passives Einkommen",
            "description": "Entdecke die besten Tools & Affiliate-Nischen",
            "created_at": datetime.now().isoformat(),
            "links": []
        }
        self.ab_tests = []
        self.storage_file = f"bio_links_{account_name}.json"
        self._load_from_storage()
    
    def add_affiliate_link(self, 
                          url: str,
                          affiliate_id: str,
                          program: str,
                          niche: str,
                          title: str = "",
                          description: str = "",
                          emoji: str = "🔗") -> AffiliateLink:
        """
        Fügt einen neuen Affiliate-Link zur Bio-Link Seite hinzu.
        
        Args:
            url: Original Affiliate-URL
            affiliate_id: Deine Affiliate ID
            program: Amazon, ShareASale, CJ Affiliate, etc.
            niche: Kategorie (Tech, Business, Lifestyle, etc.)
            title: Link-Titel in Bio
            description: Kurzbeschreibung
            emoji: Icon für die Bio
        
        Returns:
            AffiliateLink Objekt
        """
        
        link = AffiliateLink(url, affiliate_id, program, niche, f"{niche}_biolink")
        
        link_id = link.short_code
        self.links[link_id] = link
        
        bio_entry = {
            "id": link_id,
            "title": title or f"{emoji} {niche}",
            "description": description,
            "emoji": emoji,
            "program": program,
            "position": len(self.bio_link_data["links"]) + 1
        }
        
        self.bio_link_data["links"].append(bio_entry)
        
        print(f"[+] Link hinzugefügt: {title or niche}")
        
        return link
    
    def generate_landing_page_html(self, layout: str = "modern") -> str:
        """
        Generiert eine professionelle Bio-Link Landing Page.
        
        Args:
            layout: modern, minimal, premium, viral
        
        Returns:
            HTML-Code der Landing Page
        """
        
        links_html = ""
        for link_data in self.bio_link_data["links"]:
            link_id = link_data["id"]
            link_obj = self.links[link_id]
            tracking_url = link_obj.generate_tracking_url(platform="instagram", source="bio_link")
            
            links_html += f"""
            <div class="link-card" onclick="trackClick('{link_id}')">
                <a href="{tracking_url}" target="_blank">
                    <span class="emoji">{link_data['emoji']}</span>
                    <div class="link-content">
                        <h3>{link_data['title']}</h3>
                        <p>{link_data['description']}</p>
                    </div>
                    <span class="arrow">→</span>
                </a>
            </div>
            """
        
        html = f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.bio_link_data['title']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', -apple-system, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 500px;
            margin: 0 auto;
            padding-top: 40px;
        }}
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }}
        .header h1 {{
            font-size: 2rem;
            margin-bottom: 10px;
            animation: slideDown 0.6s ease-out;
        }}
        .header p {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        .links {{
            display: flex;
            flex-direction: column;
            gap: 15px;
        }}
        .link-card {{
            background: white;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        .link-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }}
        .link-card a {{
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 20px;
            text-decoration: none;
            color: #333;
        }}
        .emoji {{
            font-size: 2rem;
            min-width: 50px;
            text-align: center;
        }}
        .link-content {{
            flex: 1;
            text-align: left;
        }}
        .link-content h3 {{
            font-size: 1.1rem;
            margin-bottom: 5px;
            color: #667eea;
        }}
        .link-content p {{
            font-size: 0.9rem;
            color: #666;
        }}
        .arrow {{
            font-size: 1.5rem;
            color: #667eea;
        }}
        .footer {{
            text-align: center;
            color: white;
            margin-top: 40px;
            font-size: 0.9rem;
            opacity: 0.8;
        }}
        @keyframes slideDown {{
            from {{ opacity: 0; transform: translateY(-20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{self.bio_link_data['title']}</h1>
            <p>{self.bio_link_data['description']}</p>
        </div>
        <div class="links">
            {links_html}
        </div>
        <div class="footer">
            <p>💡 Handgepickte Tools & Affiliate-Programme</p>
            <p style="margin-top: 10px; font-size: 0.8rem;">
                Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            </p>
        </div>
    </div>
    
    <script>
        function trackClick(linkId) {{
            fetch('/api/track-click', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{link_id: linkId}})
            }});
        }}
    </script>
</body>
</html>
        """
        
        return html
    
    def save_landing_page(self, layout: str = "modern"):
        """Speichert die Landing Page als HTML-Datei."""
        html = self.generate_landing_page_html(layout)
        filename = f"biolink_{self.account_name}.html"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
        
        print(f"[+] Bio-Link Page gespeichert: {filename}")
        return filename
    
    def create_ab_test(self, variant_name: str, layout: str, link_order: List[str]):
        """
        Erstellt ein A/B-Test mit verschiedenen Link-Ordnungen.
        
        Args:
            variant_name: Name der Variante (z.B. "high_ctr_first")
            layout: Layout-Style
            link_order: Reihenfolge der Link-IDs
        """
        
        test = {
            "variant_name": variant_name,
            "layout": layout,
            "link_order": link_order,
            "created_at": datetime.now().isoformat(),
            "clicks": 0,
            "conversions": 0,
            "ctr": 0.0,
            "status": "active"
        }
        
        self.ab_tests.append(test)
        print(f"[+] A/B-Test erstellt: {variant_name}")
    
    def get_performance_stats(self) -> Dict:
        """Gibt detaillierte Performance-Statistiken zurück."""
        
        total_clicks = sum(link.click_count for link in self.links.values())
        total_revenue = sum(link.revenue_earned for link in self.links.values())
        total_conversions = sum(link.conversion_count for link in self.links.values())
        
        stats = {
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
            "total_revenue": round(total_revenue, 2),
            "overall_ctr": round(total_conversions / max(total_clicks, 1) * 100, 2),
            "avg_revenue_per_click": round(total_revenue / max(total_clicks, 1), 2),
            "links": [link.to_dict() for link in self.links.values()],
            "top_performers": sorted(
                [link.to_dict() for link in self.links.values()],
                key=lambda x: x['revenue_earned'],
                reverse=True
            )[:3]
        }
        
        return stats
    
    def _save_to_storage(self):
        """Speichert Bio-Link Daten persistent."""
        data = {
            "bio_link_data": self.bio_link_data,
            "links": {k: v.to_dict() for k, v in self.links.items()},
            "ab_tests": self.ab_tests
        }
        
        with open(self.storage_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load_from_storage(self):
        """Lädt Bio-Link Daten aus Storage."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.bio_link_data = data.get("bio_link_data", self.bio_link_data)
                    self.ab_tests = data.get("ab_tests", [])
                print(f"[+] Bio-Links aus Storage geladen")
            except Exception as e:
                print(f"[-] Fehler beim Laden: {e}")


class AffiliateNetworkConnector:
    """
    Verbindet mit verschiedenen Affiliate-Netzwerken.
    - Amazon Associates
    - CJ Affiliate
    - ShareASale
    - Awin
    """
    
    NETWORKS = {
        "amazon": {
            "base_url": "https://amazon.com",
            "requires": ["associate_id"],
            "commission_rate": "1-10%"
        },
        "cj_affiliate": {
            "base_url": "https://click.cj.com",
            "requires": ["advertiser_id", "publisher_id"],
            "commission_rate": "varies"
        },
        "shareasale": {
            "base_url": "https://www.shareasale.com",
            "requires": ["affiliate_id", "merchant_id"],
            "commission_rate": "varies"
        },
        "awin": {
            "base_url": "https://www.awin.com",
            "requires": ["account_id", "advertiser_id"],
            "commission_rate": "varies"
        }
    }
    
    @staticmethod
    def get_network_info(network: str) -> Dict:
        """Gibt Info über ein Affiliate-Netzwerk zurück."""
        return AffiliateNetworkConnector.NETWORKS.get(network, {})
    
    @staticmethod
    def list_networks() -> List[str]:
        """Listet alle unterstützten Netzwerke auf."""
        return list(AffiliateNetworkConnector.NETWORKS.keys())


def main():
    """Demo: Bio-Link Manager mit mehreren Affiliate-Links."""
    
    print("\n" + "="*60)
    print("🔗 BIO-LINK MANAGER DEMO")
    print("="*60 + "\n")
    
    manager = BioLinkManager(account_name="cashbot")
    
    manager.add_affiliate_link(
        url="https://www.amazon.com/s?k=automation+software",
        affiliate_id="cashbot-20",
        program="Amazon",
        niche="Automation Tools",
        title="🤖 Top Automation Tools",
        description="Die besten Tools für dein Business",
        emoji="🤖"
    )
    
    manager.add_affiliate_link(
        url="https://zapier.com/invite/ref?d=abc123",
        affiliate_id="cashbot_zapier",
        program="Zapier",
        niche="Workflow Automation",
        title="⚡ Zapier Pro",
        description="Automatisiere deine Workflows",
        emoji="⚡"
    )
    
    manager.add_affiliate_link(
        url="https://www.hostinger.com?aid=cashbot",
        affiliate_id="cashbot_hostinger",
        program="Hostinger",
        niche="Web Hosting",
        title="🌐 Web Hosting",
        description="Günstig & zuverlässig",
        emoji="🌐"
    )
    
    manager.add_affiliate_link(
        url="https://www.namecheap.com/?aff=cashbot",
        affiliate_id="cashbot_namecheap",
        program="Namecheap",
        niche="Domain Registration",
        title="📝 Domain Registrar",
        description="Günstige Domains",
        emoji="📝"
    )
    
    print("\n[*] Generiere Bio-Link Landing Page...")
    manager.save_landing_page(layout="modern")
    
    print("\n[*] Erstelle A/B-Tests...")
    manager.create_ab_test(
        variant_name="high_ctr_first",
        layout="modern",
        link_order=["tool_1", "tool_2", "tool_3"]
    )
    
    print("\n[*] Simuliere Clicks & Conversions...")
    links = list(manager.links.values())
    
    for link in links:
        clicks = __import__('random').randint(5, 50)
        for _ in range(clicks):
            link.register_click(platform="instagram")
        
        conversions = __import__('random').randint(0, 3)
        for _ in range(conversions):
            link.register_conversion(__import__('random').uniform(2.0, 10.0))
    
    print("\n[📊] PERFORMANCE STATS:")
    stats = manager.get_performance_stats()
    print(f"   Total Clicks: {stats['total_clicks']}")
    print(f"   Total Conversions: {stats['total_conversions']}")
    print(f"   Total Revenue: ${stats['total_revenue']:.2f}")
    print(f"   Overall CTR: {stats['overall_ctr']:.2f}%")
    
    print("\n[🏆] TOP 3 PERFORMERS:")
    for i, link in enumerate(stats['top_performers'], 1):
        print(f"   {i}. Program: {link['program']} - ${link['revenue_earned']:.2f}")
    
    manager._save_to_storage()
    
    print("\n✅ Demo abgeschlossen!")


if __name__ == "__main__":
    main()
