"""
Extended search for more Lankadeepa categories
"""
import requests
from bs4 import BeautifulSoup
import re

# More categories to test
test_ = [
    ('news', range(1, 120)),  # Test IDs 1-119
    ('sports', range(1, 20)),
    ('local', range(1, 20)),
    ('world', range(1, 20)),
    ('foreign', range(1, 20)),
    ('entertainment', range(1, 30)),
    ('cinema', range(1, 20)),
    ('gossip', range(1, 30)),
]

print("Extended category search:")
print("="*70)

found = {}

for cat_name, id_range in test_:
    print(f"\nSearching {cat_name}...", end='')
    for cat_id in id_range:
        url = f'https://www.lankadeepa.lk/{cat_name}/{cat_id}/'
        try:
            resp = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, 'lxml')
                pattern = re.compile(rf'/{cat_name}/[^/]+/\d+-\d+')
                count = len([a for a in soup.select('a[href]') if pattern.search(a.get('href', ''))])
                
                if count > 5:
                    # Test pagination
                    p2 = requests.get(f'{url}30', timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
                    if p2.status_code == 200:
                        print(f"\n  ✓ ID {cat_id:3d}: {count:3d} articles")
                        found[cat_name] = cat_id
                        break
        except:
            continue
    
    if cat_name not in found:
        print(" ✗ Not found")

print("\n" + "="*70)
print("ALL WORKING CATEGORIES:")
print("="*70)

# Add previously found ones
found.update({
    'business': 9,
    'mathawada': 317,
    'thaksalawa': 55,
    'visheshanga': 26,
})

for cat, cat_id in sorted(found.items()):
    print(f"  {cat:20s} | ID: {cat_id}")
