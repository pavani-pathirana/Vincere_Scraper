"""Analyze structure of new Sinhala news sites"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

sites = {
    'colombotimes': {
        'url': 'https://colombotimes.lk/sinhala/',
        'name': 'Colombo Times Sinhala'
    },
    'lakvahini': {
        'url': 'https://lakvahini.lk/',
        'name': 'Lakvahini'
    },
    'asianmirror': {
        'url': 'https://sinhala.asianmirror.lk/',
        'name': 'Asian Mirror Sinhala'
    },
    'siyathanews': {
        'url': 'https://siyathanews.lk/',
        'name': 'Siyatha News'
    }
}

for site_key, site_info in sites.items():
    print(f"\n{'='*70}")
    print(f"SITE: {site_info['name']}")
    print(f"URL: {site_info['url']}")
    print(f"{'='*70}")
    
    try:
        r = requests.get(site_info['url'], timeout=15)
        print(f"Status: {r.status_code}")
        print(f"Encoding: {r.encoding}")
        print(f"Content-Type: {r.headers.get('Content-Type')}")
        
        soup = BeautifulSoup(r.text, 'lxml')
        
        # Find potential article links
        print(f"\nSearching for article patterns...")
        
        # Try common article selectors
        selectors = [
            'article a',
            'article h2 a',
            'article h3 a',
            '.post a',
            '.entry a',
            'h2 a',
            'h3 a',
            '[class*="post"] a',
            '[class*="article"] a'
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            if len(links) > 5:
                print(f"✓ {selector}: {len(links)} links")
                # Show first 3 links
                for i, link in enumerate(links[:3], 1):
                    href = link.get('href', '')
                    text = link.get_text(strip=True)[:60]
                    if href and text:
                        full_url = urljoin(site_info['url'], href)
                        print(f"  {i}. {text}")
                        print(f"     → {full_url}")
                break
        
        # Look for categories/navigation
        print(f"\nLooking for categories...")
        nav_links = soup.select('nav a, .menu a, .nav a')[:10]
        for link in nav_links:
            text = link.get_text(strip=True)
            href = link.get('href', '')
            if text and href and len(text) < 30:
                print(f"  - {text}: {urljoin(site_info['url'], href)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

print(f"\n{'='*70}")
print("Analysis complete!")
