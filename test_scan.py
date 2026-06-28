"""Manual Trend Scan Test"""
import sys
sys.path.insert(0, '.')

print('='*70)
print('[TREND SCAN TEST] Manueller Trend-Scan durchführen')
print('='*70)

from trend_radar.engine import TrendRadarEngine
engine = TrendRadarEngine()

print('\n[1] Starte manuellen Scan...')
engine.manual_scan()

print('\n[2] Ergebnisse nach Scan:')
keywords = engine.get_hot_keywords(limit=10)
print(f'    Keywords gefunden: {len(keywords)}')

niches = engine.get_hot_niches(limit=10)
print(f'    Niches gefunden: {len(niches)}')

programs = engine.get_discovered_programs()
print(f'    Programme gefunden: {len(programs)}')

print('\n[3] Hole Recommendations für Affiliate-Engine:')
recs = engine.get_recommendations_for_affiliate()
print(f'    Landingpage-Vorschläge: {len(recs.get("suggested_landing_pages", []))}')
for lp in recs.get('suggested_landing_pages', [])[:3]:
    print(f'      - {lp.get("topic")}: {len(lp.get("keywords", []))} Keywords')

print('\n[✓] Scan Test abgeschlossen!')
print('='*70)
