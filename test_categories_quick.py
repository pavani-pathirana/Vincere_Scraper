"""
Quick test of common Lankadeepa categories
"""
import requests
from bs4 import BeautifulSoup
import re

# Common news categories to test with different IDs
test_categories = [
    ('news', [101, 1, 2]),
    ('local', [100, 102, 10]),
    ('world', [103, 104, 11]),
    ('sports', [3]),
    ('business', [9]),
    ('entertainment', [15, 16, 17]),
    ('gossip', [18, 19]),
    ('articles', [20, 21]),
    ('thaksalawa', [55]),
    ('visheshanga', [26]),
    ('mathawada', [317]),
]

print("Testing Lankadeepa categories:")
print("="*70)

found_categories = {}

for cat_name, ids in test_categories:
    for cat_id in ids:
        url = f'https://www.lankadeepa.lk/{cat_name}/{cat_id}/'
        try:
            resp = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, 'lxml')
                
                # Count articles
                pattern = re.compile(rf'/{cat_name}/[^/]+/\d+-\d+')
                article_count = len([a for a in soup.select('a[href]') if pattern.search(a.get('href', ''))])
                
                # Test page 2
                page2 = f'https://www.lankadeepa.lk/{cat_name}/{cat_id}/30'
                resp2 = requests.get(page2, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                has_pages = resp2.status_code == 200
                
                if article_count > 5:
                    print(f"✓ {cat_name:20s} ID:{cat_id:4d} | Articles: {article_count:3d} | Pages: {has_pages}")
                    found_categories[cat_name] = cat_id
                    break  # Found working ID for this category
        except:
            pass

print("\n" + "="*70)
print("WORKING CATEGORIES")
print("="*70)
print("\nCATEGORIES = {")
print("    'latest': 'Latest',")
for cat, cat_id in sorted(found_categories.items()):
    cat_key = cat.replace('-', '_')
    cat_title = cat.replace('-', ' ').title()
    print(f"    '{cat_key}': '{cat_title}',")
print("}")

print("\n# get_category_urls():")
print("return {")
print(f"    'latest': f'{{self.BASE_URL}}/',")
for cat, cat_id in sorted(found_categories.items()):
    cat_key = cat.replace('-', '_')
    print(f"    '{cat_key}': f'{{self.BASE_URL}}/{cat}/{cat_id}/',")
print("}")
