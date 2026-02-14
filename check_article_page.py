"""Check LankaTruth article page HTML structure"""
import requests
from bs4 import BeautifulSoup

url = 'https://lankatruth.com/si/?p=195147'

resp = requests.get(url, timeout=15, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

print(f"Status: {resp.status_code}")
print(f"URL: {url}\n")

soup = BeautifulSoup(resp.content, 'lxml')

# Test different selectors for article content
selectors = [
    'article .entry-content',
    '.entry-content',
    'article .content',
    '.post-content',
    'article .article-content',
    '.elementor-widget-theme-post-content',
    '.single-post-content',
    'article p',
]

print("Testing content selectors:")
print("="*70)
for selector in selectors:
    elem = soup.select_one(selector)
    if elem:
        text = elem.get_text().strip()[:200]
        print(f"OK {selector:45s} | {len(text)} chars")
        print(f"  {text[:100]}...")
    else:
        print(f"NO {selector:45s} | NOT FOUND")

# Show article structure
print("\n" + "="*70)
print("ARTICLE TAG STRUCTURE:")
print("="*70)
article = soup.select_one('article')
if article:
    # Show first 2000 chars
    print(article.prettify()[:2000])
else:
    print("NO ARTICLE TAG")
