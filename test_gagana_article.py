"""Test Gagana article page structure"""
import requests
from bs4 import BeautifulSoup

url = "https://gagana.lk/article/two-districts-under-landslide-watch-1771220934"

response = requests.get(url, timeout=15)
print(f"Status: {response.status_code}\n")

soup = BeautifulSoup(response.text, 'lxml')

# Try multiple content selectors
print("=== Testing content selectors ===")
selectors = [
    '.article-content',
    '.entry-content',
    '.post-content',
    'article',
    '.content',
    '[class*="article"]',
    '[class*="content"]',
    '.article-body',
    '.story-body'
]

for selector in selectors:
    elem = soup.select_one(selector)
    if elem:
        text = elem.get_text(strip=True)
        print(f"{selector}: Found ({len(text)} chars)")
        if len(text) > 100 and len(text) < 500:
            print(f"  Sample: {text[:200]}...")
    else:
        print(f"{selector}: Not found")

# Look for paragraphs in body
print("\n=== Paragraphs in body ===")
body = soup.select_one('body')
if body:
    paragraphs = body.select('p')
    print(f"Total <p> tags: {len(paragraphs)}")
    
    # Show text from first few paragraphs
    for i, p in enumerate(paragraphs[:5]):
        text = p.get_text(strip=True)
        if len(text) > 50:
            print(f"  P{i+1} ({len(text)} chars): {text[:80]}...")

# Look for headline
print("\n=== Headline ===")
headline_selectors = ['h1', 'h2', '.headline', '.title']
for sel in headline_selectors:
    elem = soup.select_one(sel)
    if elem:
        print(f"{sel}: {elem.get_text(strip=True)[:100]}")
        break
