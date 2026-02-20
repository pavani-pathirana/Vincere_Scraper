"""Test script to analyze technews.lk structure"""

import requests
from bs4 import BeautifulSoup

# Test main page
print("=" * 80)
print("Testing technews.lk main page")
print("=" * 80)

r = requests.get('https://technews.lk', timeout=10)
soup = BeautifulSoup(r.text, 'lxml')

# Find categories
print("\nCategories found:")
categories = soup.select('nav a, .menu a, .nav-menu a')
for cat in categories[:15]:
    href = cat.get('href', '')
    text = cat.get_text(strip=True)
    if href and text:
        print(f"  {text}: {href}")

# Find article containers
print("\nArticle containers:")
articles = soup.select('article, .post, .entry')
print(f"  Found {len(articles)} article containers")

# Find article links
print("\nArticle links (first 10):")
links = soup.select('h2 a, h3 a, .entry-title a')
for i, link in enumerate(links[:10], 1):
    url = link.get('href', '')
    title = link.get_text(strip=True)
    print(f"  {i}. {title[:60]}")
    print(f"     URL: {url}")

# Test an article page
if links:
    test_url = links[0].get('href')
    print(f"\n{'=' * 80}")
    print(f"Testing article page: {test_url}")
    print("=" * 80)
    
    r2 = requests.get(test_url, timeout=10)
    soup2 = BeautifulSoup(r2.text, 'lxml')
    
    # Find content area
    print("\nContent selectors:")
    for selector in ['.entry-content', 'article .content', '.post-content', 
                    'article', '.single-post']:
        elem = soup2.select_one(selector)
        if elem:
            text = elem.get_text(strip=True)
            print(f"  {selector}: Found ({len(text)} chars)")
            if len(text) > 100:
                print(f"    Preview: {text[:150]}...")
    
    # Find date
    print("\nDate elements:")
    for selector in ['time', '.date', '.post-date', '.published']:
        elem = soup2.select_one(selector)
        if elem:
            print(f"  {selector}: {elem.get_text(strip=True)[:50]}")
            if elem.get('datetime'):
                print(f"    datetime attr: {elem.get('datetime')}")

print("\n" + "=" * 80)
