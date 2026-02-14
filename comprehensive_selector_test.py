"""Comprehensive selector test for all 7 sites"""
import requests
from bs4 import BeautifulSoup
import time

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

sites = [
    {
        'name': 'AdaDerana',
        'homepage': 'https://sinhala.adaderana.lk/',
        'test_list': 'https://sinhala.adaderana.lk/sinhala-hot-news.php',
        'test_article': None,
    },
    {
        'name': 'BBC Sinhala',
        'homepage': 'https://www.bbc.com/sinhala',
        'test_list': 'https://www.bbc.com/sinhala',
        'test_article': None,
    },
    {
        'name': 'Divaina',
        'homepage': 'https://www.divaina.lk/',
        'test_list': 'https://www.divaina.lk/category/main-news',
        'test_article': None,
    },
    {
        'name': 'Silumina',
        'homepage': 'https://www.silumina.lk/',
        'test_list': 'https://www.silumina.lk/category/news/',
        'test_article': None,
    },
    {
        'name': 'Ada.lk',
        'homepage': 'https://www.ada.lk/',
        'test_list': 'https://www.ada.lk/latest-news/11',
        'test_article': None,
    },
    {
        'name': 'Gossip Lanka',
        'homepage': 'https://www.gossiplankanews.com/',
        'test_list': 'https://www.gossiplankanews.com/',
        'test_article': None,
    }
]

for site in sites:
    print(f"\n{'='*70}")
    print(f"{site['name'].upper()}")
    print('='*70)
    
    try:
        # Test list page
        resp = requests.get(site['test_list'], timeout=15, headers=headers)
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, 'lxml')
            
            # Try article selectors
            found_selector = None
            found_count = 0
            
            test_selectors = [
                ('article', 'article'),
                ('.post', 'div.post'),
                ('article.post', 'article.post'),
                ('.jeg_post', 'div.jeg_post'),
                ('div[class*="news"]', 'div with news class'),
                ('a[href*="/news/"]', 'news links'),
                ('li', 'li elements'),
            ]
            
            for selector, desc in test_selectors:
                items = soup.select(selector)
                if items and len(items) >= 5:
                    found_selector = selector
                    found_count = len(items)
                    print(f"\n✓ FOUND: {desc} = {found_count} items")
                    
                    # Analyze first item
                    first = items[0]
                    print(f"  Tag: {first.name}")
                    print(f"  Classes: {first.get('class', [])}")
                    
                    # Try to find link
                    link = first.select_one('a') if first.name != 'a' else first
                    if link:
                        href = link.get('href', '')
                        if not href.startswith('http') and href.startswith('/'):
                            from urllib.parse import urljoin
                            href = urljoin(site['homepage'], href)
                        print(f"  Link: {href[:80]}")
                        site['test_article'] = href
                    
                    # Try to find title
                    title_selectors = ['h2', 'h3', 'h1', '.title', '.headline', '[data-testid="card-headline"]']
                    for ts in title_selectors:
                        title = first.select_one(ts)
                        if title:
                            print(f"  Title selector: {ts}")
                            print(f"  Title: {title.get_text()[:60]}")
                            break
                    
                    break
            
            if not found_selector:
                print("\n✗ No article containers found")
                # Show sample HTML
                body = soup.select_one('body')
                if body:
                    # Get all unique class names
                    all_classes = set()
                    for elem in body.select('[class]'):
                        classes = elem.get('class', [])
                        if isinstance(classes, list):
                            all_classes.update(classes)
                    news_related = [c for c in all_classes if 'news' in c.lower() or 'post' in c.lower() or 'article' in c.lower()]
                    if news_related:
                        print(f"\n  News-related classes found: {news_related[:10]}")
        
        time.sleep(2)  # Rate limit
        
    except Exception as e:
        print(f"\nERROR: {e}")

# Test article pages
print(f"\n\n{'#'*70}")
print("#  ARTICLE PAGE TESTING")
print(f"{'#'*70}")

for site in sites:
    if site.get('test_article'):
        print(f"\n{site['name']}: {site['test_article'][:80]}")
        try:
            resp = requests.get(site['test_article'], timeout=15, headers=headers)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, 'lxml')
                
                # Try content selectors
                content_found = False
                content_selectors = [
                    '.entry-content',
                    '.article-content',
                    '.post-content',
                    'article .content',
                    '.story-body',
                    '.article-body',
                    '[data-component="text-block"]',
                ]
                
                for selector in content_selectors:
                    elem = soup.select_one(selector)
                    if elem:
                        text = elem.get_text().strip()
                        if len(text) > 100:
                            print(f"  ✓ Content: {selector} ({len(text)} chars)")
                            content_found = True
                            break
                
                if not content_found:
                    print(f"  ✗ Content selector not found")
                    # Try article or main tags
                    for tag in ['article', 'main', '.content']:
                        elem = soup.select_one(tag)
                        if elem:
                            text = elem.get_text().strip()
                            print(f"  ? Fallback {tag}: {len(text)} chars")
                            break
            
            time.sleep(2)
        except Exception as e:
            print(f"  ERROR: {e}")

print(f"\n{'='*70}")
print("Investigation complete!")
