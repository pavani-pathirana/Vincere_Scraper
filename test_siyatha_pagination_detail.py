"""
Find exact pagination selector for Siyatha News
"""

import requests
from bs4 import BeautifulSoup

url = 'https://siyathanews.lk/archives/category/entertainmentnews'

print(f"Testing: {url}\n")

r = requests.get(url, timeout=10)
r.encoding = 'utf-8'
soup = BeautifulSoup(r.text, 'lxml')

# Find all links with /page/ in href
page_links = soup.select('a[href*="/page/"]')

print("="*70)
print(f"FOUND {len(page_links)} PAGINATION LINKS")
print("="*70)

for i, link in enumerate(page_links[:10], 1):
    href = link.get('href')
    text = link.get_text(strip=True)
    classes = link.get('class', [])
    parent = link.parent
    parent_classes = parent.get('class', []) if parent else []
    
    print(f"\n{i}. Text: '{text}' | Classes: {classes}")
    print(f"   URL: {href}")
    print(f"   Parent: {parent.name} {parent_classes}")
    
    # Show HTML
    print(f"   HTML: {str(link)[:100]}")

# Look for page 2 specifically
print("\n" + "="*70)
print("LOOKING FOR PAGE 2 LINK")
print("="*70)

page2_links = [link for link in page_links if '/page/2' in link.get('href', '')]
for link in page2_links:
    print(f"\nFound page 2 link:")
    print(f"  Classes: {link.get('class', [])}")
    print(f"  Text: '{link.get_text(strip=True)}'")
    print(f"  HTML: {link}")
    
# Check if there's a specific "next" link
print("\n" + "="*70)
print("CHECKING FOR SPECIFIC SELECTORS")
print("="*70)

selectors_to_test = [
    'a[href*="/page/2"]',
    '.page-numbers',
    'a.page-numbers',
    'span.page-numbers + a',
]

for selector in selectors_to_test:
    elements = soup.select(selector)
    if elements:
        print(f"\n{selector}: {len(elements)} found")
        for elem in elements[:3]:
            print(f"  - {elem.get_text(strip=True)}: {elem.get('href', 'N/A')}")
