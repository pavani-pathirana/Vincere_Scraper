"""
Deep search for actual political category articles on Asian Mirror
"""

import requests
from bs4 import BeautifulSoup

# Check multiple deep pages for political-specific articles
test_pages = [
    (1, 'https://sinhala.asianmirror.lk/news/political/?l=0&r=10'),
    (15, 'https://sinhala.asianmirror.lk/news/political/?l=149&r=160'),
    (50, 'https://sinhala.asianmirror.lk/news/political/?l=489&r=500'),
    (100, 'https://sinhala.asianmirror.lk/news/political/?l=989&r=1000'),
    (150, 'https://sinhala.asianmirror.lk/news/political/?l=1489&r=1500'),
]

for page_num, url in test_pages:
    print(f"\nPage {page_num}: {url}")
    
    r = requests.get(url, timeout=10)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, 'lxml')
    
    article_links = soup.select('li.listitem a')
    
    # Categorize by URL pattern
    by_category = {}
    
    for link in article_links:
        href = link.get('href', '')
        if '/news/' not in href or href.count('/') < 6:
            continue
        
        # Extract category from URL (e.g., /news/breaking/ or /news/political/)
        parts = href.split('/')
        if len(parts) >= 5:
            category = parts[4]  # The category part
            by_category[category] = by_category.get(category, 0) + 1
    
    print(f"  Categories found: {by_category}")
    
    # Show unique article IDs
    article_ids = set()
    for link in article_links:
        href = link.get('href', '')
        if '/news/' in href:
            # Get the slug/ID from URL
            slug = href.rstrip('/').split('/')[-1]
            article_ids.add(slug)
    
    print(f"  Unique article IDs: {len(article_ids)}")
    print(f"  Sample IDs: {list(article_ids)[:5]}")
