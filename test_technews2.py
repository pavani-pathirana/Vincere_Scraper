"""Test technews.lk article structure"""
import requests
from bs4 import BeautifulSoup

# Test news category
print("Testing https://technews.lk/news/")
r = requests.get('https://technews.lk/news/', timeout=10)
soup = BeautifulSoup(r.text, 'lxml')

# Find articles
articles = soup.select('article')
print(f"Articles found: {len(articles)}")

if articles:
    first = articles[0]
    print("\nFirst article HTML structure:")
    print(first.prettify()[:800])
    
    # Find link
    link = first.select_one('a')
    if link:
        print(f"\nFirst article URL: {link.get('href')}")
        print(f"First article title: {link.get_text(strip=True)[:80]}")

# Find all links
links = []
for a in soup.select('a'):
    href = a.get('href', '')
    if '/news/' in href and href.startswith('/news/'):
        links.append(href)

print(f"\nFound {len(links)} article links")
print("Sample URLs:")
for url in list(set(links))[:10]:
    print(f"  {url}")

# Test pagination
print("\nPagination:")
next_links = soup.select('a[href*="page"]')
for link in next_links[:5]:
    print(f"  {link.get_text(strip=True)}: {link.get('href')}")
