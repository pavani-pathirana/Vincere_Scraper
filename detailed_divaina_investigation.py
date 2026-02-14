"""Detailed Divaina investigation"""
import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

url = 'https://www.divaina.lk/category/main-news'
resp = requests.get(url, timeout=15, headers=headers)
soup = BeautifulSoup(resp.content, 'lxml')

print(f"Status: {resp.status_code}")
print(f"URL: {url}\n")

# Find main content area
main = soup.select_one('main') or soup.select_one('#main') or soup.select_one('.main')
print(f"Main area found: {main is not None}")

if main:
    # Look for all article-like links
    links = main.select('a[href*="/politics/"], a[href*="/news/"], a[href*="/main-news/"]')
    print(f"Article links found: {len(links)}")
    
    if links:
        # Analyze first few
        for i, link in enumerate(links[:5], 1):
            href = link.get('href', '')
            text = link.get_text().strip()
            
            # Skip short texts (likely images or read-more buttons)
            if len(text) < 20:
                continue
            
            print(f"\n--- Link {i} ---")
            print(f"URL: {href[:80]}")
            print(f"Text: {text[:60]}")
            
            # Find parent container
            parent = link.parent
            depth = 0
            while parent and depth < 5:
                if parent.name in ['article', 'div', 'li'] and parent.get('class'):
                    print(f"Parent ({parent.name}): {parent.get('class')}")
                    break
                parent = parent.parent
                depth += 1
    
    # Try different selectors
    print("\n" + "="*70)
    print("Testing selectors:")
    for selector in ['article', '.post', 'div[class*="post"]', '.item', '.entry']:
        items = main.select(selector)
        # Filter for those with article links
        valid = []
        for item in items:
            links = item.select('a[href]')
            has_article = any('/politics/' in l.get('href', '') or '/news/' in l.get('href', '') or '/main-news/' in l.get('href','') for l in links)
            if has_article:
                valid.append(item)
        if valid:
            print(f"  {selector}: {len(valid)} valid items")
            # Show first one
            first = valid[0]
            print(f"    Classes: {first.get('class')}")
            link = first.select_one('a[href*="/politics/"], a[href*="/news/"], a[href*="/main-news/"]')
            if link:
                print(f"    Sample URL: {link.get('href', '')[:60]}")

# Test article page
print("\n" + "="*70)
print("Testing article page")
print("="*70)

article_url = 'https://www.divaina.lk/politics/48%e0%b7%80%e0%b7%99%e0%b6%b1%e0%b7%92-%e0%b6%bb%e0%b7%90%e0%b6%9c%e0%b7%94%e0%b6%b8%e0%b7%8a-%e0%b6%a4%e0%b7%8a%e2%80%8d%e0%b6%bb%e0%b6%ba%e0%b7%94%e0%b6%af%e0%b7%8f%e0%b6%ba%e0%b7%92%e0%b6%9a/250889'

resp = requests.get(article_url, timeout=15, headers=headers)
if resp.status_code == 200:
    soup = BeautifulSoup(resp.content, 'lxml')
    
    for selector in ['.entry-content', '.jeg_content', 'article .content', '.article-content', '.post-content']:
        elem = soup.select_one(selector)
        if elem:
            text = elem.get_text().strip()
            if len(text) > 100:
                print(f"✓ Content: {selector} ({len(text)} chars)")
                break
    else:
        print("✗ No content found")
        # Try article tag
        article = soup.select_one('article')
        if article:
            print(f"  Article tag found: {len(article.get_text())} chars")
            print(f"  Article classes: {article.get('class')}")
