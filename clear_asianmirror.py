"""
Clear Asian Mirror entries from database for fresh testing
"""

import sqlite3

db = sqlite3.connect('vincere_state.db')
cursor = db.cursor()

# Count before
cursor.execute("SELECT COUNT(*) FROM scraped_urls WHERE website = 'asianmirror'")
count_before = cursor.fetchone()[0]

# Delete
cursor.execute("DELETE FROM scraped_urls WHERE website = 'asianmirror'")
db.commit()

# Count after
cursor.execute("SELECT COUNT(*) FROM scraped_urls WHERE website = 'asianmirror'")
count_after = cursor.fetchone()[0]

print(f"Cleared {count_before} Asian Mirror entries from database")
print(f"Remaining: {count_after}")

db.close()
