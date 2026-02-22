"""Detailed analysis of roar.media categories and structure"""

import requests
from bs4 import BeautifulSoup

# Test main page
r = requests.get('https://archive.roar.media/sinhala/tech-s/', timeout=10)
soup = BeautifulSoup(r.text, 'lxml')

print("Article list analysis:")
print("=" * 80)

# Find all article cards
articles = soup.select('article')
print(f"Found {len(articles)} articles\n")

for i, article in enumerate(articles[:3], 1):
    print(f"Article {i}:")
    
    # Find link
    link = article.select_one('a')
    if link:
        print(f"  URL: {link.get('href')}")
        print(f"  Title: {link.get_text(strip=True)[:80]}")
    
    # Find date
    date = article.select_one('time')
    if date:
        print(f"  Date: {date.get_text(strip=True)}")
    
    # Find category
    category = article.select_one('.category, [class*="cat"]')
    if category:
        print(f"  Category: {category.get_text(strip=True)}")
    
    print()

# Check for different category pages
print("\n" + "=" * 80)
print("Testing category variations:")
print("=" * 80)

category_urls = [
    'https://archive.roar.media/sinhala/tech-s/',
    'https://archive.roar.media/sinhala/tech/',
    'https://archive.roar.media/sinhala/',
]

for url in category_urls:
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'lxml')
            articles = soup.select('article')
            title = soup.select_one('title')
            print(f"{url}")
            print(f"  Status: {r.status_code}, Articles: {len(articles)}, Title: {title.get_text(strip=True) if title else 'N/A'}")
    except Exception as e:
        print(f"{url}: Error - {e}")

# Test pagination
print("\n" + "=" * 80)
print("Testing pagination:")
print("=" * 80)

for page_num in [2, 3]:
    url = f'https://archive.roar.media/sinhala/tech-s/page/{page_num}/'
    try:
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, 'lxml')
        articles = soup.select('article')
        print(f"Page {page_num}: {r.status_code}, {len(articles)} articles")
    except Exception as e:
        print(f"Page {page_num}: Error - {e}")
