"""
Discover LankaTruth category IDs
"""
import requests
from bs4 import BeautifulSoup
import time

# Test category IDs 1-20
base_url = 'https://lankatruth.com/si/'

print("Testing LankaTruth category IDs:")
print("="*70)

found_categories = {}

for cat_id in range(1, 15):
    url = f'{base_url}?cat={cat_id}'
    print(f"Testing: {url}", end=' ... ')
    try:
        resp = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        print(f"Status {resp.status_code}", end=' | ')
        
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, 'lxml')
            
            # Look for category name in page title or heading
            title = soup.select_one('title')
            title_text = title.get_text() if title else ''
            
            # Count articles
            articles = soup.select('article') or soup.select('.post')
            
            print(f"{len(articles)} articles | {title_text[:40]}")
            
            if len(articles) > 0:
                found_categories[cat_id] = {
                    'name': title_text,
                    'article_count': len(articles)
                }
        else:
            print(f"Failed")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Add delay to avoid rate limiting
    time.sleep(3)

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
for cat_id, info in found_categories.items():
    print(f"  {cat_id}: {info['name']}")

# Generate code
print("\n" + "="*70)
print("SCRAPER CODE")
print("="*70)
print("\nCATEGORIES = {")
for cat_id, info in found_categories.items():
    # Try to map to English keys
    name_lower = info['name'].lower()
    if 'ජාත්‍යන්තර' in info['name'] or 'international' in name_lower:
        key = 'international'
    elif 'දේශපාලන' in info['name'] or 'politics' in name_lower:
        key = 'politics'
    elif 'ක්‍රීඩා' in info['name'] or 'sports' in name_lower or 'sport' in name_lower:
        key = 'sports'
    elif 'ව්‍යාපාර' in info['name'] or 'business' in name_lower:
        key = 'business'
    elif 'විනෝද' in info['name'] or 'entertainment' in name_lower:
        key = 'entertainment'
    else:
        key = f'cat{cat_id}'
    
    print(f"    '{key}': {cat_id},  # {info['name'][:40]}")
print("}")
