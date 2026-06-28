"""Quick Database Query Test"""
import sys
sys.path.insert(0, '.')

from trend_radar.db.database import TrendDatabase

db = TrendDatabase()

print("="*70)
print("[DATABASE QUERY TEST]")
print("="*70)

# Query Data
import sqlite3
conn = sqlite3.connect('trend_radar/db/trends.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("\n[Keywords in DB]")
cursor.execute("SELECT COUNT(*) as count FROM trending_keywords")
count = cursor.fetchone()['count']
print(f"  Total: {count}")

if count > 0:
    cursor.execute("SELECT * FROM trending_keywords LIMIT 5")
    for row in cursor.fetchall():
        print(f"    - {dict(row)['keyword']}")

print("\n[Niches in DB]")
cursor.execute("SELECT COUNT(*) as count FROM niches")
count = cursor.fetchone()['count']
print(f"  Total: {count}")

if count > 0:
    cursor.execute("SELECT * FROM niches LIMIT 3")
    for row in cursor.fetchall():
        print(f"    - {dict(row)['niche']}")

print("\n[Programs in DB]")
cursor.execute("SELECT COUNT(*) as count FROM discovered_programs")
count = cursor.fetchone()['count']
print(f"  Total: {count}")

conn.close()
db.close()

print("\n[✓] Query Test abgeschlossen!")
print("="*70)
