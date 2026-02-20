"""
Check Asian Mirror database state  
"""

import sqlite3

db = sqlite3.connect('vincere_state.db')
cursor = db.cursor()

# Get Asian Mirror URLs
cursor.execute("SELECT url, category, article_id FROM scraped_urls WHERE website = 'asianmirror' ORDER BY id DESC LIMIT 50")
rows = cursor.fetchall()

print(f"Asian Mirror URLs in database: {len(rows)}\n")

for i, (url, category, article_id) in enumerate(rows, 1):
    print(f"{i}. [{category}] {url}")
    print(f"   Article ID: {article_id}\n")

# Count by category
cursor.execute("SELECT category, COUNT(*) FROM scraped_urls WHERE website = 'asianmirror' GROUP BY category")
counts = cursor.fetchall()
print("\nAsian Mirror by category:")
for category, count in counts:
    print(f"  {category}: {count} articles")

db.close()
