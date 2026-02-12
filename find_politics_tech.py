"""
Find politics and technology category IDs for Lankadeepa
"""
import requests
from bs4 import BeautifulSoup
import re

categories_to_find = {
    'politics': range(1, 120),
    'technology': range(1, 120),
    'tech': range(1, 50),
}

print("Searching for politics and technology categories:")
print("="*70)

found = {}

for cat_name, id_range in categories_to_find.items():
    print(f"\nSearching {cat_name}...", end='', flush=True)
    
    for cat_id in id_range:
        url = f'https://www.lankadeepa.lk/{cat_name}/{cat_id}/'
        try:
            resp = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, 'lxml')
                
                # Count articles
                pattern = re.compile(rf'/{cat_name}/[^/]+/\d+-\d+')
                count = len([a for a in soup.select('a[href]') if pattern.search(a.get('href', ''))])
                
                if count > 5:
                    # Test pagination
                    p2 = requests.get(f'{url}30', timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
                    if p2.status_code == 200:
                        print(f" ✓ FOUND! ID:{cat_id:3d} | {count:3d} articles")
                        found[cat_name] = cat_id
                        break
        except:
            continue
    
    if cat_name not in found:
        print(" ✗ Not found")

print("\n" + "="*70)
print("RESULTS:")
print("="*70)

if found:
    for cat, cat_id in sorted(found.items()):
        print(f"  '{cat}': {cat_id}")
    
    print("\nAdd to scraper:")
    print("CATEGORIES = {")
    for cat, cat_id in sorted(found.items()):
        cat_title = cat.replace('-', ' ').title()
        print(f"    '{cat}': '{cat_title}',")
    print("}")
    
    print("\nget_category_urls():")
    for cat, cat_id in sorted(found.items()):
        print(f"    '{cat}': f'{{self.BASE_URL}}/{cat}/{cat_id}/',")
else:
    print("No categories found")
