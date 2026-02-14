"""Debug: Simulate the scraper's parsing logic"""
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

url = 'https://lankatruth.com/si/?cat=3'
BASE_URL = 'https://lankatruth.com/si/'

resp = requests.get(url, timeout=15, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

soup = BeautifulSoup(resp.content, 'lxml')

# Same selector as scraper
article_containers = (
    soup.select('article') or
    soup.select('div.post') or
    soup.select('div.news-item') or
    soup.select('div.article-item') or
    soup.select('.posts article') or
    soup.select('div[class*="post-"]')
)

print(f"Found {len(article_containers)} article containers\n")

articles_found = []

for i, container in enumerate(article_containers[:3], 1):
    print(f"--- Container {i} ---")
    
    # Extract article link (SAME AS SCRAPER)
    if container.name == 'a':
        link_elem = container
    else:
        link_elem = container.select_one('a[href*="/si/"]') or container.select_one('a')
    
    if not link_elem:
        print("  ✗ No link found")
        continue
    
    article_url = link_elem.get('href', '')
    print(f"  Link: {article_url[:80]}")
    
    # Make absolute URL
    if article_url.startswith('/'):
        article_url = urljoin(BASE_URL, article_url)
    elif not article_url.startswith('http'):
        article_url = urljoin(BASE_URL, article_url)
    
    # Skip if not a Sinhala article
    if '/si/' not in article_url:
        print(f"  ✗ Not Sinhala article")
        continue
    
    # Skip category/archive pages
    if '/page/' in article_url or any(cat in article_url for cat in ['news/', 'politics/', 'sports/']):
        if not re.search(r'/\d{4}/\d{2}/', article_url):
            print(f"  ✗ Skipped as category/archive page")
            continue
    
    # Extract headline (SAME AS SCRAPER)
    headline_elem = (
        container.select_one('h2.entry-title') or
        container.select_one('h3.entry-title') or
        container.select_one('h2') or
        container.select_one('h3') or
        container.select_one('.title') or
        container.select_one('.headline') or
        container.select_one('.post-title') or
        link_elem
    )
    
    headline = headline_elem.get_text(strip=True) if headline_elem else 'Untitled'
    print(f"  Headline: {headline[:60]}")
    
    # Skip if headline is empty or too short
    if len(headline) < 10:
        print(f"  ✗ Headline too short ({len(headline)} chars)")
        continue
    
    print(f"  ✓ VALID ARTICLE")
    articles_found.append((headline, article_url))

print(f"\n{'='*70}")
print(f"Total valid articles: {len(articles_found)}")
