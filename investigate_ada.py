import requests
from bs4 import BeautifulSoup
import time

base_url = 'https://www.ada.lk'

print("="*70)
print("INVESTIGATING ADA.LK")
print("="*70)

# Step 1: Check homepage
print("\n1. Analyzing homepage structure...")
try:
    response = requests.get(base_url, timeout=10, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Check for various article container patterns
        patterns = [
            ('article', 'article'),
            ('.post', '.post class'),
            ('.news-item', '.news-item class'),
            ('.article-item', '.article-item class'),
            ('[class*="post"]', 'class containing "post"'),
            ('[class*="news"]', 'class containing "news"'),
            ('[class*="article"]', 'class containing "article"'),
            ('.item', '.item class'),
            ('.entry', '.entry class')
        ]
        
        print("\nSearching for article containers:")
        for selector, description in patterns:
            elements = soup.select(selector)
            if elements:
                print(f"  ✓ {description}: Found {len(elements)} elements")
                
                # Analyze first element
                first = elements[0]
                print(f"    Classes: {first.get('class')}")
                
                # Find links
                links = first.select('a[href]')
                if links:
                    print(f"    First link: {links[0].get('href')}")
                
                # Find headline
                headlines = first.select('h1, h2, h3, h4, .title, [class*="title"]')
                if headlines:
                    print(f"    Headline: {headlines[0].get_text(strip=True)[:60]}")
        
        # Check navigation
        print("\n2. Checking navigation menu:")
        nav_links = soup.select('nav a, .menu a, header a, .navigation a')
        print(f"Navigation links found: {len(nav_links)}")
        
        categories = {}
        for link in nav_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            if href and text:
                if any(keyword in href for keyword in ['category', 'tag', 'section', base_url]):
                    categories[text] = href
                    print(f"  {text[:40]}: {href}")
        
        # Check all links for article patterns
        print("\n3. Analyzing all links for article URL patterns:")
        all_links = soup.select('a[href]')
        article_candidates = []
        
        for link in all_links:
            href = link.get('href', '')
            if href:
                # Look for various URL patterns
                if any(pattern in href for pattern in ['/20', '/article/', '/news/', '/post/']):
                    article_candidates.append(href)
        
        print(f"Potential article URLs found: {len(article_candidates)}")
        if article_candidates:
            unique_patterns = {}
            for url in article_candidates[:10]:
                # Extract URL pattern
                if base_url in url:
                    path = url.replace(base_url, '')
                    parts = path.split('/')
                    pattern = '/'.join([p for p in parts[:3] if p])
                    unique_patterns[pattern] = unique_patterns.get(pattern, 0) + 1
            
            print("\nCommon URL patterns:")
            for pattern, count in sorted(unique_patterns.items(), key=lambda x: x[1], reverse=True):
                print(f"  {pattern}: {count} occurrences")
            
            # Test first article
            test_url = article_candidates[0]
            if not test_url.startswith('http'):
                test_url = base_url + test_url
            
            print(f"\n4. Testing article page: {test_url}")
            article_response = requests.get(test_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if article_response.status_code == 200:
                article_soup = BeautifulSoup(article_response.content, 'lxml')
                
                # Test content selectors
                print("\nContent selector analysis:")
                content_selectors = [
                    'article',
                    '.post-content',
                    '.entry-content',
                    '.article-content',
                    '.content',
                    '[class*="content"]',
                    '.news-body',
                    '.story-content'
                ]
                
                for selector in content_selectors:
                    elements = article_soup.select(selector)
                    if elements:
                        text = elements[0].get_text(strip=True)
                        if len(text) > 100:
                            print(f"  ✓ {selector}: {len(text)} chars")
                            print(f"    Preview: {text[:100]}...")
                
                # Find headlines
                print("\nHeadline analysis:")
                headline_selectors = ['h1', 'h2.title', '.headline', '.post-title', '[class*="title"]']
                for selector in headline_selectors:
                    elements = article_soup.select(selector)
                    if elements:
                        text = elements[0].get_text(strip=True)
                        if len(text) > 10:
                            print(f"  ✓ {selector}: {text[:80]}")
            else:
                print(f"  Article page returned: {article_response.status_code}")
                
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("INVESTIGATION COMPLETE")
print("="*70)
