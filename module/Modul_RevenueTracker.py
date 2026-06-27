"""
💰 Revenue Tracking & Attribution Dashboard

Trackt Affiliate-Einnahmen aus beiden Pipelines:
- Pipeline 1: Bio-Link Clicks → Conversions → Revenue
- Pipeline 2: SEO Traffic → Clicks → Conversions → Revenue

Unified Revenue Reporting & Performance Analytics
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List
import random


class ClickTracker:
    """Trackt Clicks auf Affiliate-Links mit Attribution."""
    
    def __init__(self):
        self.clicks = []
        self.conversions = []
        self.storage_file = "click_tracking.json"
        self._load_data()
    
    def track_click(self, 
                   link_id: str,
                   source: str,  # bio_link, seo_article
                   platform: str,  # instagram, tiktok, google_organic
                   user_agent: str = "",
                   referrer: str = "") -> Dict:
        """
        Protokolliert einen Click auf einen Affiliate-Link.
        
        Args:
            link_id: ID des Affiliate-Links
            source: Herkunft des Clicks
            platform: Platform/Channel
            user_agent: Browser Info
            referrer: Referer URL
        
        Returns:
            Click-Record mit Session-ID
        """
        
        import uuid
        
        session_id = str(uuid.uuid4())
        
        click_record = {
            "session_id": session_id,
            "link_id": link_id,
            "source": source,
            "platform": platform,
            "timestamp": datetime.now().isoformat(),
            "user_agent": user_agent,
            "referrer": referrer,
            "converted": False,
            "conversion_amount": None,
            "conversion_date": None
        }
        
        self.clicks.append(click_record)
        return click_record
    
    def register_conversion(self, 
                          session_id: str,
                          amount: float,
                          program: str = "unknown") -> Dict:
        """
        Registriert eine erfolgreiche Conversion.
        
        Args:
            session_id: Session ID des ursprünglichen Clicks
            amount: Affiliate-Provision
            program: Affiliate-Programm
        
        Returns:
            Conversion-Record
        """
        
        for click in self.clicks:
            if click["session_id"] == session_id:
                click["converted"] = True
                click["conversion_amount"] = amount
                click["conversion_date"] = datetime.now().isoformat()
        
        conversion = {
            "session_id": session_id,
            "amount": amount,
            "program": program,
            "timestamp": datetime.now().isoformat()
        }
        
        self.conversions.append(conversion)
        return conversion
    
    def _load_data(self):
        """Lädt gespeicherte Tracking-Daten."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, "r") as f:
                    data = json.load(f)
                    self.clicks = data.get("clicks", [])
                    self.conversions = data.get("conversions", [])
            except:
                pass
    
    def save_data(self):
        """Speichert Tracking-Daten persistent."""
        with open(self.storage_file, "w") as f:
            json.dump({
                "clicks": self.clicks,
                "conversions": self.conversions
            }, f, indent=2)


class RevenueCalculator:
    """Berechnet Umsätze pro Link, Source und Platform."""
    
    def __init__(self, tracker: ClickTracker):
        self.tracker = tracker
    
    def calculate_metrics(self) -> Dict:
        """
        Berechnet alle wichtigen Revenue-Metriken.
        
        Returns:
            Dict mit allen Metriken
        """
        
        if not self.tracker.clicks:
            return self._empty_metrics()
        
        total_clicks = len(self.tracker.clicks)
        total_conversions = len(self.tracker.conversions)
        total_revenue = sum(c["amount"] for c in self.tracker.conversions)
        
        metrics = {
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
            "total_revenue": round(total_revenue, 2),
            "conversion_rate": round(total_conversions / max(total_clicks, 1) * 100, 2),
            "avg_revenue_per_click": round(total_revenue / max(total_clicks, 1), 2),
            "avg_revenue_per_conversion": round(total_revenue / max(total_conversions, 1), 2),
            "roi": round((total_revenue / max(total_clicks * 0.1, 1)) * 100, 2)  # Simplified
        }
        
        metrics["by_source"] = self._calculate_by_source()
        metrics["by_platform"] = self._calculate_by_platform()
        metrics["by_date"] = self._calculate_by_date()
        
        return metrics
    
    def _calculate_by_source(self) -> Dict:
        """Berechnet Metriken pro Source."""
        sources = {}
        
        for click in self.tracker.clicks:
            source = click["source"]
            if source not in sources:
                sources[source] = {"clicks": 0, "conversions": 0, "revenue": 0}
            
            sources[source]["clicks"] += 1
            
            if click["converted"]:
                sources[source]["conversions"] += 1
                sources[source]["revenue"] += click["conversion_amount"] or 0
        
        for source in sources:
            sources[source]["ctr"] = round(
                sources[source]["conversions"] / max(sources[source]["clicks"], 1) * 100, 2
            )
            sources[source]["revenue"] = round(sources[source]["revenue"], 2)
        
        return sources
    
    def _calculate_by_platform(self) -> Dict:
        """Berechnet Metriken pro Platform."""
        platforms = {}
        
        for click in self.tracker.clicks:
            platform = click["platform"]
            if platform not in platforms:
                platforms[platform] = {"clicks": 0, "conversions": 0, "revenue": 0}
            
            platforms[platform]["clicks"] += 1
            
            if click["converted"]:
                platforms[platform]["conversions"] += 1
                platforms[platform]["revenue"] += click["conversion_amount"] or 0
        
        for platform in platforms:
            platforms[platform]["ctr"] = round(
                platforms[platform]["conversions"] / max(platforms[platform]["clicks"], 1) * 100, 2
            )
            platforms[platform]["revenue"] = round(platforms[platform]["revenue"], 2)
        
        return platforms
    
    def _calculate_by_date(self) -> Dict:
        """Berechnet Umsatz pro Tag."""
        daily = {}
        
        for conversion in self.tracker.conversions:
            date = conversion["timestamp"][:10]
            if date not in daily:
                daily[date] = {"conversions": 0, "revenue": 0}
            
            daily[date]["conversions"] += 1
            daily[date]["revenue"] += conversion["amount"]
        
        for date in daily:
            daily[date]["revenue"] = round(daily[date]["revenue"], 2)
        
        return daily
    
    def _empty_metrics(self) -> Dict:
        """Gibt leere Metriken zurück."""
        return {
            "total_clicks": 0,
            "total_conversions": 0,
            "total_revenue": 0.0,
            "conversion_rate": 0.0,
            "avg_revenue_per_click": 0.0,
            "avg_revenue_per_conversion": 0.0,
            "by_source": {},
            "by_platform": {},
            "by_date": {}
        }


class RevenueForecaster:
    """Prognostiziert zukünftige Umsätze basierend auf historischen Daten."""
    
    @staticmethod
    def forecast_monthly_revenue(current_metrics: Dict, growth_rate: float = 0.15) -> Dict:
        """
        Prognostiziert den Umsatz für den nächsten Monat.
        
        Args:
            current_metrics: Aktuelle Metriken
            growth_rate: Erwartete Wachstumsrate (z.B. 0.15 = 15%)
        
        Returns:
            Prognose-Daten
        """
        
        daily_revenue = current_metrics["total_revenue"] / max(len(current_metrics["by_date"]), 1)
        monthly_forecast = daily_revenue * 30 * (1 + growth_rate)
        
        forecast = {
            "current_daily_revenue": round(daily_revenue, 2),
            "projected_monthly_revenue": round(monthly_forecast, 2),
            "growth_rate": f"{growth_rate * 100:.0f}%",
            "scenarios": {
                "conservative": {
                    "growth_rate": "5%",
                    "monthly_revenue": round(daily_revenue * 30 * 1.05, 2)
                },
                "normal": {
                    "growth_rate": "15%",
                    "monthly_revenue": round(monthly_forecast, 2)
                },
                "optimistic": {
                    "growth_rate": "30%",
                    "monthly_revenue": round(daily_revenue * 30 * 1.30, 2)
                }
            },
            "recommendations": [
                "Erhöhe Traffic durch bessere SEO & Promotion",
                "Teste höher-zahlende Affiliate-Programme",
                "Optimiere Bio-Link Click-through Rate",
                "Erweitere auf zusätzliche Nischen"
            ]
        }
        
        return forecast


class RevenueHTMLDashboard:
    """Generiert ein HTML-Dashboard für Revenue-Tracking."""
    
    @staticmethod
    def generate_dashboard(metrics: Dict, forecast: Dict) -> str:
        """
        Generiert ein schönes HTML-Dashboard.
        
        Args:
            metrics: Aktuelle Metriken
            forecast: Prognose-Daten
        
        Returns:
            HTML-String
        """
        
        by_source_html = ""
        for source, data in metrics.get("by_source", {}).items():
            by_source_html += f"""
            <div class="metric-card">
                <h4>{source.upper()}</h4>
                <p>Clicks: {data['clicks']}</p>
                <p>Conversions: {data['conversions']}</p>
                <p>Revenue: ${data['revenue']:.2f}</p>
                <p>CTR: {data['ctr']:.2f}%</p>
            </div>
            """
        
        by_platform_html = ""
        for platform, data in metrics.get("by_platform", {}).items():
            by_platform_html += f"""
            <div class="metric-card">
                <h4>{platform.upper()}</h4>
                <p>Clicks: {data['clicks']}</p>
                <p>Revenue: ${data['revenue']:.2f}</p>
                <p>CTR: {data['ctr']:.2f}%</p>
            </div>
            """
        
        html = f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💰 Revenue Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', -apple-system, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        .header {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            color: #667eea;
            margin-bottom: 10px;
        }}
        .header p {{
            color: #666;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }}
        .metric-card h3 {{
            font-size: 0.9rem;
            color: #999;
            margin-bottom: 10px;
            text-transform: uppercase;
        }}
        .metric-value {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        .metric-details {{
            font-size: 0.9rem;
            color: #666;
        }}
        .section {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5rem;
        }}
        .cards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .forecast-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
        }}
        .forecast-card h4 {{
            margin-bottom: 10px;
        }}
        .forecast-value {{
            font-size: 2rem;
            font-weight: bold;
        }}
        .recommendation {{
            background: #f0f4ff;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 4px;
        }}
        .footer {{
            text-align: center;
            color: white;
            margin-top: 40px;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💰 Revenue Dashboard</h1>
            <p>Affiliate Earnings Tracking & Attribution Analytics</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>Total Revenue</h3>
                <div class="metric-value">${{metrics.get('total_revenue', 0):.2f}}</div>
                <div class="metric-details">All Sources & Platforms</div>
            </div>
            
            <div class="metric-card">
                <h3>Total Clicks</h3>
                <div class="metric-value">{metrics.get('total_clicks', 0)}</div>
                <div class="metric-details">Affiliate Link Clicks</div>
            </div>
            
            <div class="metric-card">
                <h3>Conversions</h3>
                <div class="metric-value">{metrics.get('total_conversions', 0)}</div>
                <div class="metric-details">CTR: {metrics.get('conversion_rate', 0):.2f}%</div>
            </div>
            
            <div class="metric-card">
                <h3>Avg Revenue/Click</h3>
                <div class="metric-value">${{metrics.get('avg_revenue_per_click', 0):.2f}}</div>
                <div class="metric-details">Revenue Per Click</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Performance by Source</h2>
            <div class="cards-grid">
                {by_source_html}
            </div>
        </div>
        
        <div class="section">
            <h2>📱 Performance by Platform</h2>
            <div class="cards-grid">
                {by_platform_html}
            </div>
        </div>
        
        <div class="section">
            <h2>📈 Revenue Forecast</h2>
            <div class="cards-grid">
                <div class="forecast-card">
                    <h4>Current Daily</h4>
                    <div class="forecast-value">${{forecast.get('current_daily_revenue', 0):.2f}}</div>
                </div>
                <div class="forecast-card">
                    <h4>Normal Growth (15%)</h4>
                    <div class="forecast-value">${{forecast['scenarios']['normal']['monthly_revenue']:.2f}}</div>
                    <p style="margin-top: 10px; font-size: 0.9rem;">Next Month</p>
                </div>
                <div class="forecast-card">
                    <h4>Optimistic (30%)</h4>
                    <div class="forecast-value">${{forecast['scenarios']['optimistic']['monthly_revenue']:.2f}}</div>
                    <p style="margin-top: 10px; font-size: 0.9rem;">Best Case</p>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>💡 Optimization Recommendations</h2>
            {''.join(f'<div class="recommendation">{rec}</div>' for rec in forecast.get('recommendations', []))}
        </div>
        
        <div class="footer">
            <p>🤖 Powered by CashBot Automation Engine</p>
            <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html


class UnifiedMonetizationEngine:
    """Zentrale Engine für beide Monetarisierungs-Pipelines."""
    
    def __init__(self):
        self.tracker = ClickTracker()
        self.calculator = RevenueCalculator(self.tracker)
        self.forecaster = RevenueForecaster()
    
    def simulate_pipeline_1_activity(self, num_clicks: int = 100):
        """Simuliert Bio-Link Pipeline Aktivität."""
        print(f"\n[*] Simuliere Pipeline 1 (Bio-Link) mit {num_clicks} Clicks...")
        
        for _ in range(num_clicks):
            session = self.tracker.track_click(
                link_id=f"bio_link_{random.randint(1, 5)}",
                source="bio_link",
                platform=random.choice(["instagram", "tiktok"]),
            )
            
            if random.random() < 0.08:  # 8% conversion rate
                self.tracker.register_conversion(
                    session["session_id"],
                    amount=random.uniform(2.0, 15.0),
                    program=random.choice(["Amazon", "CJ Affiliate", "ShareASale"])
                )
        
        print(f"   [+] Bio-Link Pipeline simuliert")
    
    def simulate_pipeline_2_activity(self, num_clicks: int = 300):
        """Simuliert SEO Pipeline Aktivität."""
        print(f"\n[*] Simuliere Pipeline 2 (SEO) mit {num_clicks} Clicks...")
        
        for _ in range(num_clicks):
            session = self.tracker.track_click(
                link_id=f"seo_link_{random.randint(1, 10)}",
                source="seo_article",
                platform=random.choice(["google_organic", "google_ads"]),
            )
            
            if random.random() < 0.05:  # 5% conversion rate (lower than bio)
                self.tracker.register_conversion(
                    session["session_id"],
                    amount=random.uniform(1.0, 8.0),
                    program=random.choice(["Amazon", "CJ Affiliate", "Awin"])
                )
        
        print(f"   [+] SEO Pipeline simuliert")
    
    def generate_report(self) -> str:
        """Generiert den kompletten Revenue-Report."""
        
        metrics = self.calculator.calculate_metrics()
        forecast = self.forecaster.forecast_monthly_revenue(metrics)
        
        self.tracker.save_data()
        
        dashboard_html = RevenueHTMLDashboard.generate_dashboard(metrics, forecast)
        
        with open("revenue_dashboard.html", "w", encoding="utf-8") as f:
            f.write(dashboard_html)
        
        print("\n[+] Dashboard generiert: revenue_dashboard.html")
        
        return metrics


def main():
    """Demo: Vereinigte Monetarisierungs-Pipeline."""
    
    print("\n" + "="*60)
    print("💰 UNIFIED MONETIZATION ENGINE DEMO")
    print("="*60)
    
    engine = UnifiedMonetizationEngine()
    
    engine.simulate_pipeline_1_activity(num_clicks=100)
    engine.simulate_pipeline_2_activity(num_clicks=300)
    
    metrics = engine.generate_report()
    
    print("\n" + "="*60)
    print("📊 REVENUE SUMMARY")
    print("="*60)
    print(f"Total Revenue: ${metrics['total_revenue']:.2f}")
    print(f"Total Clicks: {metrics['total_clicks']}")
    print(f"Total Conversions: {metrics['total_conversions']}")
    print(f"Overall CTR: {metrics['conversion_rate']:.2f}%")
    print(f"Avg per Click: ${metrics['avg_revenue_per_click']:.2f}")
    
    print("\n" + "="*60)
    print("✅ Demo fertiggestellt!")
    print("="*60)


if __name__ == "__main__":
    main()
