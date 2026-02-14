"""Deep dive into article structures"""
import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Test each site's article list and article page
tests = [
    {
        'name': 'AdaDerana',
        'list_url': 'https://sinhala.adaderana.lk/politics.php',
        'article_url': None  # Will get from list
    },
    {
        'name': 'BBC Sinhala',
        'list_url': 'https://www.bbc.com/sinhala',
        'article_url': None
    },
    {
        'name': 'Divaina',
        'list_url': 'https://www.divaina.lk/category/main-news',
        'article_url': None
    },
    {
        'name': 'Silumina',
        'list_url': 'https://www.silumina.lk/category/news/',
        'article_url': None
    },
    {
        'name': 'Ada',
        'list_url': 'https://www.ada.lk/latest-news/11',
        'article_url': None
    },
]

for test in tests:
    print(f"\n{'='*70}")
    print(f"{test['name']}")
    print('='*70)
    
    try:
        # Get list page
        resp = requests.get(test['list_url'], timeout=15, headers=headers)
        print(f"List page: {resp.status_code}")
        
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, 'lxml')
            
            # Try different article selectors
            selectors = [
                'article', 
                '.post',
                '.news-item',
                '.article-item',
                'div[class*="news"]',
                'li.news-item',
                '.news-list li',
                '.story',
            ]
            
            found = False
            for selector in selectors:
                items = soup.select(selector)
                if items and len(items) > 3:
                    print(f"  Articles found: {selector} = {len(items)}")
                    
                    # Get first article link
                    first = items[0]
                    link = first.select_one('a')
                    if link:
                        href = link.get('href', '')
                        if href.startswith('/'):
                            parsed = requests.utils.urlparse(test['list_url'])
                            href = f"{parsed.scheme}://{parsed.netloc}{href}"
                        if href.startswith('http'):
                            test['article_url'] = href
                            print(f"  Sample article: {href[:80]}")
                            found = True
                            break
            
            if not found:
                # Try finding any links
                all_links = soup.select('a[href]')
                print(f"  Total links: {len(all_links)}")
                for link in all_links[:10]:
                    href = link.get('href', '')
                    text = link.get_text().strip()[:50]
                    if text and len(text) > 20:
                        print(f"    {text:50s} | {href[:60]}")
    
    except Exception as e:
        print(f"ERROR: {e}")

# Now test article pages
print(f"\n\n{'='*70}")
print("ARTICLE PAGE STRUCTURES")
print('='*70)

for test in tests:
    if test['article_url']:
        print(f"\n{test['name']}: {test['article_url']}")
        try:
            resp = requests.get(test['article_url'], timeout=15, headers=headers)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, 'lxml')
                
                # Try content selectors
                content_selectors = [
                    '.entry-content',
                    '.article-content',
                    '.post-content',
                    'article .content',
                    '.story-body',
                    '#article-body',
                ]
                
                for selector in content_selectors:
                    elem = soup.select_one(selector)
                    if elem:
                        text = elem.get_text().strip()[:200]
                        print(f"  Content: {selector} ({len(text)} chars)")
                        break
                else:
                    print("  Content: NOT FOUND")
        except Exception as e:
            print(f"  ERROR: {e}")
