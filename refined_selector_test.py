"""Refined selector test - focus on main content"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def test_site(name, list_url, homepage):
    print(f"\n{'='*70}")
    print(f"{name}")
    print('='*70)
    
    try:
        resp = requests.get(list_url, timeout=15, headers=headers)
        print(f"Status: {resp.status_code}")
        
        if resp.status_code != 200:
            return None
        
        soup = BeautifulSoup(resp.content, 'lxml')
        
        # Find main content area first
        main_area = (
            soup.select_one('main') or
            soup.select_one('#main') or
            soup.select_one('.main') or
            soup.select_one('#content') or
            soup.select_one('.content-area') or
            soup.select_one('body')
        )
        
        print(f"Main area: {main_area.name if main_area else 'body'}")
        
        # Now search only in main area for articles
        selectors_to_try = [
            ('article', 'article tag'),
            ('.post', 'post class'),
            ('.jeg_post', 'jeg_post class'),
            ('div.news-story', 'news-story div'),
            ('div[class*="post"]', 'post-* classes'),
            ('[data-testid="card"]', 'BBC card'),
            ('.promo-card', 'promo card'),
        ]
        
        found = None
        for selector, desc in selectors_to_try:
            items = main_area.select(selector) if main_area else []
            # Filter out navigation items
            valid_items = []
            for item in items:
                # Must have a link
                link = item.select_one('a') if item.name != 'a' else item
                if link:
                    href = link.get('href', '')
                    # Skip navigation links
                    if href and not href.startswith('#') and 'category' not in href and 'topics' not in href:
                        valid_items.append(item)
            
            if len(valid_items) >= 5:
                print(f"\n✓ {desc}: {len(valid_items)} articles")
                first = valid_items[0]
                
                # Find link
                link = first.select_one('a') if first.name != 'a' else first
                if link:
                    href = link.get('href', '')
                    if href.startswith('/'):
                        href = urljoin(homepage, href)
                    elif not href.startswith('http'):
                        href = urljoin(homepage, href)
                    print(f"  Sample: {href[:80]}")
                
                # Find title
                for ts in ['h2', 'h3', '.title', '[data-testid="card-headline"]', '.jeg_post_title']:
                    title = first.select_one(ts)
                    if title and len(title.get_text().strip()) > 10:
                        print(f"  Title: {ts} = {title.get_text()[:60]}")
                        break
                
                found = {'selector': selector, 'count': len(valid_items), 'sample': href if 'href' in locals() else None}
                break
        
        if not found:
            print("\n✗ No articles found")
            # Show some debug info
            all_links = main_area.select('a[href]') if main_area else []
            news_links = [l for l in all_links if '/news/' in l.get('href', '') or '/article/' in l.get('href', '') or '.php' in l.get('href', '')][:5]
            if news_links:
                print(f"\nSample links found:")
                for l in news_links:
                    print(f"  {l.get('href', '')[:60]} | {l.get_text()[:40]}")
        
        return found
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

# Test each site
results = {}

results['AdaDerana'] = test_site(
    'AdaDerana',
    'https://sinhala.adaderana.lk/',
    'https://sinhala.adaderana.lk'
)

results['BBC'] = test_site(
    'BBC Sinhala',
    'https://www.bbc.com/sinhala',
    'https://www.bbc.com'
)

results['Divaina'] = test_site(
    'Divaina',
    'https://www.divaina.lk/category/main-news',
    'https://www.divaina.lk'
)

results['Silumina'] = test_site(
    'Silumina',
    'https://www.silumina.lk/category/news/',
    'https://www.silumina.lk'
)

results['Ada.lk'] = test_site(
    'Ada.lk',
    'https://www.ada.lk/',
    'https://www.ada.lk'
)

results['Gossip'] = test_site(
    'Gossip Lanka',
    'https://www.gossiplankanews.com/',
    'https://www.gossiplankanews.com'
)

# Summary
print(f"\n\n{'='*70}")
print("SUMMARY")
print('='*70)
for name, result in results.items():
    if result:
        print(f"{name:15s}: {result['selector']:30s} ({result['count']} articles)")
    else:
        print(f"{name:15s}: NOT FOUND")
