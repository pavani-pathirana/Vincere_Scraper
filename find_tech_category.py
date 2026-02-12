import requests
from bs4 import BeautifulSoup
import re

# Test various possible technology category names and IDs
technology_tests = [
    ('technology', range(1, 30)),
    ('tech', range(1, 30)),
    ('it', range(1, 20)),
    ('digital', range(1, 20)),
]

print("Searching for technology category:")
print("="*60)

for cat_name, id_range in technology_tests:
    print(f"\nTesting {cat_name}...")
    for cat_id in id_range:
        url = f'https://www.lankadeepa.lk/{cat_name}/{cat_id}/'
        try:
            resp = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, 'lxml')
                pattern = re.compile(rf'/{cat_name}/[^/]+/\d+-\d+')
                count = len([a for a in soup.select('a[href]') if pattern.search(a.get('href', ''))])
                
                if count > 3:
                    print(f"  ✓ FOUND: {cat_name}/{cat_id} has {count} articles")
                    # Test pagination
                    p2 = requests.get(f'{url}30', timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
                    print(f"    Pagination page 2: {p2.status_code}")
                    break
        except:
            continue

print("\nIf no technology category found, it may not exist as a separate category.")
print("Technology articles might be under 'business' or 'news' categories.")
