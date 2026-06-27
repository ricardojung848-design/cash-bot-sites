"""
🔍 Programmatic SEO Content Generator

Pipeline 2: Programmatic SEO → Google Traffic → Affiliate-Einnahmen
- Automatische SEO-optimierte Content-Generierung
- Keyword-Clustering
- Internal Linking Strategy
- Monetarisierung durch Affiliate-Links
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
from openai import OpenAI


client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed", timeout=300.0)


class KeywordResearcher:
    """Recherchiert Keywords und organisiert sie in Cluster."""
    
    def __init__(self):
        self.keywords = []
        self.clusters = {}
    
    def extract_keywords_from_topic(self, topic: str, num_keywords: int = 50) -> List[str]:
        """
        Generiert eine Liste von Long-Tail Keywords für ein Thema.
        
        Args:
            topic: Haupt-Thema
            num_keywords: Anzahl zu generierender Keywords
        
        Returns:
            Liste von Keywords
        """
        
        print(f"[*] Recherchiere Keywords für: {topic}...")
        
        prompt = f"""
Du bist ein SEO-Expert. Generiere {num_keywords} hochqualitative Long-Tail Keywords 
für dieses Thema: '{topic}'

ANFORDERUNGEN:
- Jeder Keyword sollte 2-4 Worte lang sein
- Mix aus Question-Keywords (Wie, Was, Welcher) und Statement-Keywords
- Hohes Suchvolumen + niedriger Wettbewerb
- Relevant für Affiliate-Monetarisierung
- KEINE generischen Keywords

FORMAT:
Returne NUR eine JSON-Liste mit den Keywords, z.B.:
["keyword1", "keyword2", "keyword3"]
"""
        
        try:
            completion = client.chat.completions.create(
                model="local-model",
                messages=[{"role": "user", "content": prompt}]
            )
            
            response = completion.choices[0].message.content
            
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                keywords = json.loads(json_match.group())
            else:
                keywords = json.loads(response)
            
            self.keywords.extend(keywords)
            print(f"[+] {len(keywords)} Keywords generiert")
            return keywords
        
        except Exception as e:
            print(f"[-] Fehler bei Keyword-Generierung: {e}")
            return []
    
    def cluster_keywords(self) -> Dict[str, List[str]]:
        """
        Organisiert Keywords in semantische Cluster.
        
        Returns:
            Dict mit Clustern {cluster_name: [keywords]}
        """
        
        print("[*] Clustere Keywords...")
        
        prompt = f"""
Organisiere diese {len(self.keywords)} Keywords in 5-8 semantische Cluster:

Keywords: {json.dumps(self.keywords)}

FORMAT:
Returne ein JSON-Object mit Clustern:
{{
    "cluster_name_1": ["keyword1", "keyword2", ...],
    "cluster_name_2": ["keyword3", "keyword4", ...],
    ...
}}

Cluster-Namen sollten das Thema beschreiben, z.B. "Budget Options", "Features Comparison", etc.
"""
        
        try:
            completion = client.chat.completions.create(
                model="local-model",
                messages=[{"role": "user", "content": prompt}]
            )
            
            response = completion.choices[0].message.content
            
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                self.clusters = json.loads(json_match.group())
            else:
                self.clusters = json.loads(response)
            
            print(f"[+] Keywords in {len(self.clusters)} Cluster organisiert")
            return self.clusters
        
        except Exception as e:
            print(f"[-] Fehler beim Clustering: {e}")
            return {}


class SEOArticleGenerator:
    """Generiert SEO-optimierte Artikel für jedes Keyword-Cluster."""
    
    def __init__(self):
        self.articles = []
    
    def generate_article(self, 
                        keyword: str,
                        cluster_name: str,
                        related_keywords: List[str],
                        affiliate_products: List[str] = None) -> Dict:
        """
        Generiert einen SEO-optimierten Artikel mit Affiliate-Links.
        
        Args:
            keyword: Haupt-Keyword
            cluster_name: Name des Keyword-Clusters
            related_keywords: Verwandte Keywords zum Einbinden
            affiliate_products: Affiliate-Produkte zum Promoten
        
        Returns:
            Dict mit Artikel-Content
        """
        
        print(f"   [*] Generiere Artikel für '{keyword}'...")
        
        products_str = ", ".join(affiliate_products) if affiliate_products else "relevant products"
        related_str = ", ".join(related_keywords[:5]) if related_keywords else ""
        
        prompt = f"""
Du bist ein SEO & Affiliate-Marketing Experte. Schreibe einen professionellen 
Blogartikel der für Google ranking wird.

VORGABEN:
- Hauptkeyword: {keyword}
- Cluster: {cluster_name}
- Related Keywords zum Einbinden: {related_str}
- Länge: 1500-2000 Worte
- SEO-optimiert mit:
  * Meta-Title (60 chars max)
  * Meta-Description (160 chars max)
  * H1, H2 mit Keywords
  * Internal Linking Anchor Texts
  * Keyword Density 1-2%
  
STRUKTUR:
1. Introduction (mit Haupt-Keyword)
2. 3-4 Detaillierte Abschnitte (H2 mit Related Keywords)
3. Comparison Table (falls relevant)
4. FAQ (5-6 Fragen mit Answers)
5. Conclusion mit CTA

MONETARISIERUNG:
- Natürlich {products_str} erwähnen
- 2-3 Affiliate-Links wo es Sinn macht
- Authentische Empfehlungen (kein Hard-Sell)

FORMAT:
Returne JSON:
{{
    "meta_title": "...",
    "meta_description": "...",
    "keyword": "{keyword}",
    "content_outline": {{
        "introduction": "...",
        "sections": [
            {{"title": "...", "content": "...", "keywords": [...]}}
        ],
        "faq": [
            {{"question": "...", "answer": "..."}}
        ],
        "conclusion": "..."
    }},
    "affiliate_opportunities": ["product1", "product2"],
    "internal_links": [
        {{"anchor_text": "...", "target_page": "..."}}
    ],
    "estimated_traffic": "high/medium/low",
    "estimated_revenue_potential": "$X per month"
}}
"""
        
        try:
            completion = client.chat.completions.create(
                model="local-model",
                messages=[{"role": "user", "content": prompt}]
            )
            
            response = completion.choices[0].message.content
            
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                article = json.loads(json_match.group())
            else:
                article = json.loads(response)
            
            self.articles.append(article)
            return article
        
        except Exception as e:
            print(f"   [-] Fehler: {e}")
            return {}
    
    def generate_cluster_content_plan(self, cluster_name: str, keywords: List[str]) -> Dict:
        """
        Erstellt einen Content-Plan für einen ganzen Keyword-Cluster.
        
        Args:
            cluster_name: Name des Clusters
            keywords: Liste von Keywords im Cluster
        
        Returns:
            Content-Plan mit Interlinking-Strategie
        """
        
        print(f"\n[*] Erstelle Content-Plan für Cluster: {cluster_name}")
        
        plan = {
            "cluster_name": cluster_name,
            "pillar_keyword": keywords[0],  # Stärkster Keyword als Pillar
            "cluster_keywords": keywords[1:],  # Rest als Cluster-Content
            "pillar_article": None,
            "cluster_articles": [],
            "internal_linking_structure": {
                "pillar_to_cluster": [],
                "cluster_to_cluster": []
            }
        }
        
        print(f"   [*] Generiere Pillar-Artikel für: {keywords[0]}")
        pillar = self.generate_article(
            keyword=keywords[0],
            cluster_name=cluster_name,
            related_keywords=keywords[1:5],
            affiliate_products=["Main Affiliate Product"]
        )
        plan["pillar_article"] = pillar
        
        print(f"   [*] Generiere {len(keywords[1:5])} Cluster-Artikel...")
        for keyword in keywords[1:5]:
            article = self.generate_article(
                keyword=keyword,
                cluster_name=cluster_name,
                related_keywords=[k for k in keywords if k != keyword][:3],
                affiliate_products=["Related Product"]
            )
            plan["cluster_articles"].append(article)
        
        print(f"   [+] Content-Plan fertig: 1 Pillar + {len(plan['cluster_articles'])} Cluster-Artikel")
        
        return plan
    
    def build_internal_linking_map(self, content_plans: List[Dict]) -> Dict:
        """
        Erstellt eine strategische Internal-Linking Map.
        
        Args:
            content_plans: Liste von Content-Plans aus Clustern
        
        Returns:
            Internal Linking Strategie
        """
        
        print("\n[*] Erstelle Internal Linking Map...")
        
        linking_map = {
            "pillar_hub_links": [],  # Pillar-Seite verbindet alle Cluster
            "cluster_interconnects": [],  # Cluster verlinken aufeinander
            "breadcrumb_hierarchy": []
        }
        
        for plan in content_plans:
            pillar = plan["pillar_article"]["meta_title"]
            
            for article in plan["cluster_articles"]:
                linking_map["pillar_hub_links"].append({
                    "from": pillar,
                    "to": article["meta_title"],
                    "anchor_text": article["keyword"]
                })
        
        print(f"[+] {len(linking_map['pillar_hub_links'])} interne Links geplant")
        return linking_map


class SEOOptimizationGuide:
    """Generiert Optimierungs-Richtlinien für jeden Artikel."""
    
    @staticmethod
    def generate_on_page_seo_checklist(article: Dict) -> Dict:
        """
        Erstellt eine SEO-Checkliste für die On-Page Optimierung.
        
        Args:
            article: Artikel-Dict
        
        Returns:
            SEO-Optimierungs-Checkliste
        """
        
        return {
            "title_optimization": {
                "title": article.get("meta_title"),
                "length": len(article.get("meta_title", "")),
                "includes_keyword": article.get("keyword", "") in article.get("meta_title", ""),
                "power_words": ["How", "Best", "Top", "Complete", "Guide"]
            },
            "meta_description": {
                "description": article.get("meta_description"),
                "length": len(article.get("meta_description", "")),
                "includes_cta": any(cta in article.get("meta_description", "") for cta in ["Learn", "Discover", "Find"])
            },
            "content_optimization": {
                "keyword_density": "1-2%",
                "h1_count": "1 (Hauptkeyword)",
                "h2_usage": "2-4 (Related Keywords)",
                "internal_links": "3-5 (zu relevanten Seiten)",
                "external_links": "2-3 (authority, do-follow)"
            },
            "technical_seo": {
                "schema_markup": ["Article", "BreadcrumbList", "FAQ-Schema"],
                "mobile_friendly": True,
                "page_speed": ">90 PageSpeed Score",
                "ssl_certificate": True
            },
            "affiliate_optimization": {
                "disclosure": "Muss oben sichtbar sein",
                "link_placement": "Natürlich in Content integriert",
                "anchor_text": "Keyword + branded mix"
            }
        }
    
    @staticmethod
    def generate_link_building_strategy() -> Dict:
        """Erstellt eine Link-Building Strategie."""
        
        return {
            "backlink_sources": [
                "Industry Resource Pages",
                "Related Blog Posts",
                "Forum Mentions (Reddit, Quora)",
                "Wikipedia-ähnliche Seiten",
                "News & Media Coverage"
            ],
            "guest_posting_targets": [
                "High DA (30+) Blogs",
                "Industry-Specific Websites",
                "Competitor Blog Comments"
            ],
            "internal_link_strategy": {
                "pillar_linking": "Pillar linkt zu allen Cluster-Artikeln",
                "cluster_linking": "Cluster-Artikel verlinken sich gegenseitig",
                "breadcrumbs": "Hierarchische Breadcrumb Navigation"
            },
            "link_velocity": "5-10 neue Links pro Woche (organic growth)"
        }


class ProgrammaticSEOGenerator:
    """
    Master-Generator für komplette Programmatic SEO Kampagnen.
    """
    
    def __init__(self, niche: str = "affiliate-marketing"):
        self.niche = niche
        self.researcher = KeywordResearcher()
        self.article_generator = SEOArticleGenerator()
        self.content_plans = []
    
    def generate_seo_campaign(self, 
                             main_topic: str,
                             num_clusters: int = 5,
                             articles_per_cluster: int = 4) -> Dict:
        """
        Generiert eine komplette SEO-Kampagne mit Hunderten von Artikeln.
        
        Args:
            main_topic: Hauptthema der Kampagne
            num_clusters: Anzahl zu generierender Cluster
            articles_per_cluster: Artikel pro Cluster
        
        Returns:
            Kompletter Content-Plan
        """
        
        print("\n" + "="*60)
        print(f"🔍 PROGRAMMATIC SEO KAMPAGNE GENERATOR")
        print(f"   Thema: {main_topic}")
        print(f"   Cluster: {num_clusters}")
        print(f"   Content-Stücke: {num_clusters * articles_per_cluster}")
        print("="*60)
        
        num_keywords = num_clusters * articles_per_cluster * 2
        
        print(f"\n[PHASE 1] KEYWORD RESEARCH")
        print(f"{'='*60}")
        keywords = self.researcher.extract_keywords_from_topic(main_topic, num_keywords)
        
        print(f"\n[PHASE 2] KEYWORD CLUSTERING")
        print(f"{'='*60}")
        clusters = self.researcher.cluster_keywords()
        
        print(f"\n[PHASE 3] CONTENT GENERATION")
        print(f"{'='*60}")
        
        for cluster_name, cluster_keywords in clusters.items():
            plan = self.article_generator.generate_cluster_content_plan(
                cluster_name,
                cluster_keywords[:articles_per_cluster]
            )
            self.content_plans.append(plan)
        
        print(f"\n[PHASE 4] INTERNAL LINKING STRATEGY")
        print(f"{'='*60}")
        linking_map = self.article_generator.build_internal_linking_map(self.content_plans)
        
        campaign_summary = {
            "main_topic": main_topic,
            "created_at": datetime.now().isoformat(),
            "total_articles": num_clusters * (articles_per_cluster + 1),
            "clusters": len(clusters),
            "content_plans": self.content_plans,
            "internal_linking": linking_map,
            "seo_checklist": SEOOptimizationGuide.generate_on_page_seo_checklist({
                "meta_title": f"Best {main_topic} Tools 2024",
                "meta_description": f"Discover the top {main_topic} solutions. Compare features, pricing & reviews.",
                "keyword": main_topic
            }),
            "link_building_strategy": SEOOptimizationGuide.generate_link_building_strategy(),
            "estimated_monthly_traffic": f"{num_clusters * articles_per_cluster * 50}+ visitors",
            "estimated_monthly_revenue": f"${num_clusters * articles_per_cluster * 2}-${num_clusters * articles_per_cluster * 5}"
        }
        
        return campaign_summary
    
    def export_campaign(self, campaign: Dict, filename: str = None) -> str:
        """Exportiert den Campaign als JSON."""
        
        if filename is None:
            filename = f"seo_campaign_{self.niche}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(campaign, f, indent=2, ensure_ascii=False)
        
        print(f"\n[+] SEO Campaign exportiert: {filename}")
        return filename
    
    def generate_html_sitemap(self, campaign: Dict) -> str:
        """Generiert eine HTML Sitemap für alle Artikel."""
        
        html = f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>Sitemap - {campaign['main_topic']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #f5f5f5; padding: 40px; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
        h1 {{ color: #667eea; margin-bottom: 30px; }}
        .cluster {{ margin-bottom: 40px; }}
        .cluster h2 {{ color: #764ba2; margin-top: 0; }}
        .articles {{ margin-left: 20px; }}
        .article {{ margin: 10px 0; }}
        .article a {{ color: #667eea; text-decoration: none; }}
        .article a:hover {{ text-decoration: underline; }}
        .stats {{ background: #f0f0f0; padding: 15px; border-radius: 5px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📑 Sitemap: {campaign['main_topic']}</h1>
        <p>Insgesamt {campaign['total_articles']} Artikel</p>
"""
        
        for plan in campaign['content_plans']:
            html += f"""
        <div class="cluster">
            <h2>🔗 {plan['cluster_name']}</h2>
            <div class="articles">
                <div class="article">
                    <strong>🎯 Pillar:</strong> 
                    <a href="/articles/{plan['pillar_keyword']}.html">
                        {plan['pillar_article'].get('meta_title', plan['pillar_keyword'])}
                    </a>
                </div>
"""
            
            for article in plan['cluster_articles']:
                html += f"""
                <div class="article">
                    <a href="/articles/{article.get('keyword', 'article')}.html">
                        {article.get('meta_title', 'Article')}
                    </a>
                </div>
"""
            
            html += """
            </div>
        </div>
"""
        
        html += """
        <div class="stats">
            <h3>📊 Kampagnen-Statistiken</h3>
            <p><strong>Geschätzter monatlicher Traffic:</strong> """ + campaign['estimated_monthly_traffic'] + """</p>
            <p><strong>Geschätzter monatlicher Umsatz:</strong> """ + campaign['estimated_monthly_revenue'] + """</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html


def main():
    """Demo: Generiere eine komplette SEO-Kampagne."""
    
    generator = ProgrammaticSEOGenerator(niche="workflow-automation")
    
    campaign = generator.generate_seo_campaign(
        main_topic="Best Workflow Automation Tools",
        num_clusters=3,
        articles_per_cluster=3
    )
    
    generator.export_campaign(campaign)
    
    print("\n✅ SEO Kampagne generiert!")
    print(f"   📄 Artikel: {campaign['total_articles']}")
    print(f"   📊 Geschätzter Traffic: {campaign['estimated_monthly_traffic']}")
    print(f"   💰 Geschätzter Umsatz: {campaign['estimated_monthly_revenue']}")


if __name__ == "__main__":
    main()
