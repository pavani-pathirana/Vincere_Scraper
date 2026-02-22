"""Test script to analyze archive.roar.media structure"""

import requests
from bs4 import BeautifulSoup

# Test different URL variations
urls_to_test = [
    'https://archive.roar.media/sinhala/tech-s/',
    'https://archive.roar.media/sinhala/tech-s',
    'https://archive.roar.media/sinhala/',
]

for test_url in urls_to_test:
    print("=" * 80)
    print(f"Testing: {test_url}")
    print("=" * 80)
    
    try:
        r = requests.get(test_url, timeout=10)
        print(f"Status code: {r.status_code}")
        
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'lxml')
            
            # Check page title
            title = soup.select_one('title')
            if title:
                print(f"Page title: {title.get_text(strip=True)}")
            
            # Find all links
            links = soup.select('a[href]')
            print(f"Total links found: {len(links)}")
            
            # Find article-like elements
            articles = soup.select('article, .post, .entry, .card, .item')
            print(f"Article-like containers: {len(articles)}")
            
            # Show some links
            print("\nSample links:")
            for link in links[:10]:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                if text:
                    print(f"  {text[:50]}: {href[:80]}")
            
            break
            
    except Exception as e:
        print(f"Error: {e}")
    
    print()

print("\n" + "=" * 80)

# Find categories/sections
print("\nCategory links:")
nav_links = soup.select('nav a, .menu a, header a')
for link in nav_links[:20]:
    href = link.get('href', '')
    text = link.get_text(strip=True)
    if href and text and '/sinhala/' in href:
        print(f"  {text}: {href}")

# Find article containers
print("\nArticle containers:")
articles = soup.select('article, .post, .entry, .card')
print(f"  Found {len(articles)} article containers")

# Find article links
print("\nArticle links (first 10):")
links = soup.select('a[href*="/sinhala/"]')
article_links = []
for link in links:
    href = link.get('href', '')
    if '/tech-s/' in href or '/tech/' in href:
        text = link.get_text(strip=True)
        if text and len(text) > 10:
            article_links.append((text[:60], href))

# Remove duplicates
seen = set()
for text, href in article_links[:10]:
    if href not in seen:
        seen.add(href)
        print(f"  {text}")
        print(f"    URL: {href}")

# Find pagination
print("\nPagination:")
page_links = soup.select('a[href*="page"]')
for link in page_links[:5]:
    print(f"  {link.get_text(strip=True)}: {link.get('href')}")

# Test an article page if we found any
if article_links:
    test_url = article_links[0][1]
    print(f"\n{'=' * 80}")
    print(f"Testing article page: {test_url}")
    print("=" * 80)
    
    r2 = requests.get(test_url, timeout=10)
    soup2 = BeautifulSoup(r2.text, 'lxml')
    
    # Find title
    title = soup2.select_one('h1, .entry-title, .post-title')
    if title:
        print(f"\nTitle: {title.get_text(strip=True)[:80]}")
    
    # Find content
    print("\nContent selectors:")
    for selector in ['.entry-content', 'article .content', '.post-content', 
                    '.article-content', 'article', '.single-post']:
        elem = soup2.select_one(selector)
        if elem:
            text = elem.get_text(strip=True)
            print(f"  {selector}: Found ({len(text)} chars)")
            if len(text) > 100:
                print(f"    Preview: {text[:150]}...")
    
    # Find date
    print("\nDate elements:")
    for selector in ['time', '.date', '.post-date', '.published', '.entry-date']:
        elem = soup2.select_one(selector)
        if elem:
            print(f"  {selector}: {elem.get_text(strip=True)[:50]}")
            if elem.get('datetime'):
                print(f"    datetime attr: {elem.get('datetime')}")

print("\n" + "=" * 80)
