"""
Discover all Lankadeepa categories and their IDs
"""
import requests
from bs4 import BeautifulSoup
import re

url = 'https://www.lankadeepa.lk/'
response = requests.get(url, timeout=30, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

soup = BeautifulSoup(response.content, 'lxml')

print("="*70)
print("LANKADEEPA CATEGORY DISCOVERY")
print("="*70)

# Find navigation menu
nav_elements = soup.select('nav a[href]') + soup.select('.menu a[href]') + soup.select('header a[href]')

categories = {}
seen_urls = set()

for link in nav_elements:
    href = link.get('href', '')
    text = link.get_text(strip=True)
    
    # Look for category URLs that match pattern /category/ or /category/ID/
    if href and 'lankadeepa.lk' in href or href.startswith('/'):
        # Extract category patterns
        if re.search(r'/(news|business|sports|politics|entertainment|gossip|world|local)', href, re.IGNORECASE):
            if href not in seen_urls:
                seen_urls.add(href)
                # Extract category ID if present
                match = re.search(r'/([a-z-]+)/(\d+)/?', href)
                if match:
                    cat_name = match.group(1)
                    cat_id = match.group(2)
                    categories[cat_name] = {'id': cat_id, 'text': text, 'url': href}
                else:
                    # Category without ID
                    match = re.search(r'/([a-z-]+)/?$', href)
                    if match:
                        cat_name = match.group(1)
                        categories[cat_name] = {'id': None, 'text': text, 'url': href}

print("\nDiscovered categories:")
for cat, info in sorted(categories.items()):
    print(f"  {cat:20s} | ID: {info['id']:4s} | Text: {info['text']:20s} | URL: {info['url']}")

# Test each discovered category
print("\n" + "="*70)
print("TESTING CATEGORY URLS")
print("="*70)

test_categories = {
    'news': None,
    'local-news': None,
    'politics': None,
    'world-news': None,
    'entertainment': None,
    'gossip': None,
}

# Try to find IDs by testing URLs
for cat in test_categories.keys():
    test_url = f'https://www.lankadeepa.lk/{cat}/'
    try:
        resp = requests.get(test_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        if resp.status_code == 200:
            # Check if it has pagination pattern
            test_soup = BeautifulSoup(resp.content, 'lxml')
            articles = len(test_soup.select(f'a[href*="/{cat}/"]'))
            print(f"\n✓ {cat:20s} | Status: {resp.status_code} | Articles: {articles}")
            
            # Look for pagination links to extract ID
            for link in test_soup.select('a[href]'):
                href = link.get('href', '')
                match = re.search(rf'/{cat}/(\d+)/(\d+)', href)
                if match:
                    cat_id = match.group(1)
                    offset = match.group(2)
                    print(f"    Found pagination: ID={cat_id}, Offset={offset}")
                    test_categories[cat] = cat_id
                    break
        else:
            print(f"✗ {cat:20s} | Status: {resp.status_code}")
    except Exception as e:
        print(f"✗ {cat:20s} | Error: {e}")

print("\n" + "="*70)
print("RECOMMENDED CATEGORIES FOR SCRAPER")
print("="*70)
print("\nCATEGORIES = {")
for cat, cat_id in sorted(test_categories.items()):
    if cat_id:
        cat_key = cat.replace('-', '_')
        cat_title = cat.replace('-', ' ').title()
        print(f"    '{cat_key}': '{cat_title}',  # ID: {cat_id}")
print("}")
