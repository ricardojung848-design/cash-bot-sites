"""Integration Test: Affiliate-Engine + Trend-Radar"""
import sys
sys.path.insert(0, '.')

print('='*70)
print('[INTEGRATION TEST] Affiliate-Engine + Trend-Radar')
print('='*70)

from trend_radar.engine import TrendRadarEngine
engine = TrendRadarEngine()

print('\n[1] Hole heiße Keywords...')
keywords = engine.get_hot_keywords(limit=5)
print(f'    Gefunden: {len(keywords)} Keywords')
if keywords:
    print(f'    Beispiel: {keywords[0].get("keyword", "N/A")}')

print('[2] Hole heiße Nischen...')
niches = engine.get_hot_niches(limit=5)
print(f'    Gefunden: {len(niches)} Nischen')
if niches:
    print(f'    Beispiel: {niches[0].get("niche", "N/A")}')

print('[3] Hole Geschäftsmöglichkeiten...')
opps = engine.get_opportunities()
print(f'    Emerging Niches: {len(opps.get("emerging_niches", []))}')
print(f'    High Potential Keywords: {len(opps.get("high_potential_keywords", []))}')

print('[4] Hole Affiliate-Engine Empfehlungen...')
recs = engine.get_recommendations_for_affiliate()
sugg = recs.get('suggested_landing_pages', [])
print(f'    Vorschläge: {len(sugg)} Landingpages')
keywords = recs.get('trending_keywords_to_target', [])
print(f'    Keywords zum Targeting: {len(keywords)}')

print('\n[✓] Integration Test erfolgreich!')
print('='*70)

# Statistiken
print('\nSTATISTIKEN:')
print(f'  - Total Keywords in DB: {len(engine.get_hot_keywords(limit=1000))}')
print(f'  - Total Niches in DB: {len(engine.get_hot_niches(limit=500))}')
print(f'  - Discovered Programs: {len(engine.get_discovered_programs())}')
print(f'  - Scheduler Status: {engine.get_scheduler_status()["scheduler_running"]}')
