"""
Manually discover LankaTruth category IDs by testing category slugs
"""
import requests
from bs4 import BeautifulSoup
import time

base_url = 'https://lankatruth.com/si/'

# Known category names to test
test_categories = {
    'politics': 'දේශපාලන',
    'sports': 'ක්‍රීඩා',
    'international': 'ජාත්‍යන්තර',
    'entertainment': 'විනෝදාස්වාදය',
    'business': 'ව්‍යාපාර',
}

found_categories = {}

# Try to find category IDs by:
# 1. Loading the homepage and looking for category links
print("Checking homepage for category links...")
try:
    resp = requests.get(base_url, timeout=15, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.content, 'lxml')
        
        # Look for navigation menu
        nav = soup.select('nav a') or soup.select('.menu a') or soup.select('#menu a')
        
        print(f"Found {len(nav)} navigation links:")
        for link in nav[:20]:  # First 20 links
            href = link.get('href', '')
            text = link.get_text().strip()
            if '?cat=' in href or 'category' in href.lower():
                print(f"  {text:30s} -> {href}")
                
                # Extract cat ID if present
                if '?cat=' in href:
                    cat_id = href.split('?cat=')[1].split('&')[0]
                    print(f"    ** FOUND: cat={cat_id} for {text}")
                    found_categories[text] = cat_id
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*70)
print("FOUND CATEGORIES:")
print("="*70)
for name, cat_id in found_categories.items():
    print(f"  {name}: {cat_id}")
