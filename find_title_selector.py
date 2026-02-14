"""Find the correct title selector"""
import requests
from bs4 import BeautifulSoup

url = 'https://lankatruth.com/si/?cat=3'

print(f"Fetching {url}...")
resp = requests.get(url, timeout=15, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

print(f"Status: {resp.status_code}")

soup = BeautifulSoup(resp.content, 'lxml')

# Try to find articles
articles = soup.select('article')
print(f"Found {len(articles)} articles")

if not articles:
    print("No articles found!") 
    exit()

first_article = articles[0]

print("Article HTML structure:")
print("="*70)
print(first_article.prettify()[:2000])

print("\n" + "="*70)
print("Testing selectors:")
print("="*70)

selectors = [
    'h2',
    'h3',
    '.elementor-post__title',
    'h3.elementor-post__title',
    'h3.elementor-post__title a',
    '.entry-title',
    '.post-title',
    'a.elementor-post__title',
]

for selector in selectors:
    elem = first_article.select_one(selector)
    if elem:
        text = elem.get_text().strip()
        print(f"✓ {selector:40s} | {text[:60]}")
    else:
        print(f"✗ {selector:40s} | NOT FOUND")
