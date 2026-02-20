"""
Test deeper pages of Asian Mirror political section
"""

import requests
from bs4 import BeautifulSoup

# Test deeper pages
test_pages = [
    (1, 'https://sinhala.asianmirror.lk/news/political/?l=0&r=10'),
    (50, 'https://sinhala.asianmirror.lk/news/political/?l=489&r=500'),
    (100, 'https://sinhala.asianmirror.lk/news/political/?l=989&r=1000'),
    (200, 'https://sinhala.asianmirror.lk/news/political/?l=1989&r=2000'),
]

for page_num, url in test_pages:
    print(f"\n{'='*70}")
    print(f"PAGE {page_num}: {url}")
    print('='*70)
    
    r = requests.get(url, timeout=10)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, 'lxml')
    
    article_links = soup.select('li.listitem a')
    
    # Collect all article URLs
    article_urls = []
    for link in article_links:
        href = link.get('href', '')
        text = link.get_text(strip=True)
        if '/news/' in href and href.count('/') >= 6:
            if not href.rstrip('/').endswith(('/political', '/local', '/sports', '/international', '/business', '/crime', '/special', '/technological')):
                article_urls.append((text, href))
    
    print(f"Articles found: {len(article_urls)}")
    
    if article_urls:
        print("\nFirst 5 articles:")
        for text, href in article_urls[:5]:
            # Extract just the slug
            slug = href.split('/')[-2] if href.endswith('/') else href.split('/')[-1]
            print(f"  • {text[:60]}")
            print(f"    /{slug}/")
