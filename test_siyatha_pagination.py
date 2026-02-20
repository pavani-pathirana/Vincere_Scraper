"""
Test Siyatha News pagination on entertainment page
"""

import requests
from bs4 import BeautifulSoup

url = 'https://siyathanews.lk/archives/category/entertainmentnews'

print(f"Testing: {url}\n")

r = requests.get(url, timeout=10)
r.encoding = 'utf-8'
soup = BeautifulSoup(r.text, 'lxml')

print("="*70)
print("PAGINATION LINKS")
print("="*70)

# Check for next page link
next_selectors = [
    'a.next',
    '.pagination a[rel="next"]',
    '.nav-next a',
    'a[rel="next"]',
    '.next-page a',
    '.page-numbers.next',
    'a.page-numbers.next',
]

for selector in next_selectors:
    elem = soup.select_one(selector)
    if elem:
        print(f"\n✓ Found with selector: {selector}")
        print(f"  URL: {elem.get('href')}")
        print(f"  Text: {elem.get_text(strip=True)}")

# Check all pagination elements
pagination = soup.select('.pagination, .nav-links, .page-numbers')
print(f"\nPagination containers: {len(pagination)}")

for container in pagination[:3]:
    print(f"\n  Container: {container.name} {container.get('class', [])}")
    links = container.select('a')
    print(f"  Links: {len(links)}")
    for link in links[:5]:
        print(f"    - {link.get_text(strip=True)}: {link.get('href')}")

# Check for page numbers
all_page_links = soup.select('a[href*="/page/"]')
print(f"\nAll /page/ links: {len(all_page_links)}")
for link in all_page_links[:5]:
    print(f"  {link.get_text(strip=True)}: {link.get('href')}")

# Check articles on page
article_links = soup.select('h3 a')
print(f"\nArticle links found: {len(article_links)}")
