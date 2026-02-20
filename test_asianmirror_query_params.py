"""
Test Asian Mirror pagination with query parameters
"""

import requests
from bs4 import BeautifulSoup

# Test the pagination pattern
urls = [
    'https://sinhala.asianmirror.lk/news/political/?l=0&r=10',    # Page 1
    'https://sinhala.asianmirror.lk/news/political/?l=9&r=20',    # Page 2
    'https://sinhala.asianmirror.lk/news/political/?l=19&r=30',   # Page 3
]

for i, url in enumerate(urls, 1):
    print(f"\n{'='*70}")
    print(f"PAGE {i}: {url}")
    print('='*70)
    
    r = requests.get(url, timeout=10)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, 'lxml')
    
    article_links = soup.select('li.listitem a')
    
    # Filter to actual articles
    valid_articles = []
    for link in article_links:
        href = link.get('href', '')
        if '/news/' in href and href.count('/') >= 6:
            # Skip category pages
            if not href.rstrip('/').endswith(('/political', '/local', '/sports', '/international', '/business', '/crime', '/special', '/technological')):
                valid_articles.append(href)
    
    print(f"Valid articles: {len(valid_articles)}")
    
    # Show URL patterns
    patterns = {}
    for url in valid_articles:
        # Extract pattern like /news/breaking/ or /news/political/
        parts = url.split('/')
        if len(parts) >= 5:
            pattern = '/'.join(parts[:5]) + '/'
            patterns[pattern] = patterns.get(pattern, 0) + 1
    
    print("\nURL patterns:")
    for pattern, count in patterns.items():
        print(f"  {pattern}: {count} articles")
    
    # Show first 3 articles
    print("\nSample articles:")
    for url in valid_articles[:3]:
        print(f"  - {url}")
