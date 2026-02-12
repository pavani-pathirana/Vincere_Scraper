"""
Debug script to inspect NewsFirst pagination structure
"""
import requests
from bs4 import BeautifulSoup

test_url = "https://www.newsfirst.lk/sinhala/sports/"

print(f"Fetching URL: {test_url}\n")

response = requests.get(test_url, timeout=30, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

soup = BeautifulSoup(response.content, 'lxml')

print("=" * 70)
print("PAGINATION SELECTORS")
print("=" * 70)

# Test various pagination selectors
pagination_selectors = [
    ('a.next', 'a.next'),
    ('a[rel="next"]', 'a[rel="next"]'),
    ('.pagination-next a', '.pagination-next a'),
    ('a.next-page', 'a.next-page'),
    ('.pagination a', '.pagination a (all)'),
    ('.page-numbers a', '.page-numbers a'),
    ('nav a', 'nav a (all)'),
    ('ul.pagination a', 'ul.pagination a'),
    ('.wp-pagenavi a', '.wp-pagenavi a'),
]

for selector, description in pagination_selectors:
    elems = soup.select(selector)
    if elems:
        print(f"✓ {description}: Found {len(elems)} elements")
        for i, elem in enumerate(elems[:5]):  # Show first 5
            href = elem.get('href', 'NO HREF')
            text = elem.get_text(strip=True)
            classes = ' '.join(elem.get('class', []))
            print(f"   [{i+1}] href='{href}' text='{text}' class='{classes}'")

print("\n" + "=" * 70)
print("SEARCHING FOR PAGINATION CONTAINERS")
print("=" * 70)

# Look for pagination containers
pagination_containers = [
    'nav.pagination',
    '.pagination',
    '.page-numbers',
    '.wp-pagenavi',
    'nav',
    'div.pagination',
]

for selector in pagination_containers:
    container = soup.select_one(selector)
    if container:
        print(f"✓ Found: {selector}")
        print(f"   HTML: {str(container)[:300]}...\n")

print("=" * 70)
print("SEARCHING FOR 'NEXT' TEXT")
print("=" * 70)

# Search for any link with "next" or Sinhala equivalent
all_links = soup.find_all('a')
for link in all_links:
    text = link.get_text(strip=True).lower()
    href = link.get('href', '')
    if 'next' in text or 'මීළඟ' in text or 'page/2' in href or '/page/2/' in href:
        print(f"✓ Found potential next link:")
        print(f"   Text: {link.get_text(strip=True)}")
        print(f"   Href: {href}")
        print(f"   Classes: {link.get('class', [])}\n")

print("=" * 70)
print("SEARCHING FOR PAGE NUMBERS")
print("=" * 70)

# Look for page 2 specifically
for link in all_links:
    href = link.get('href', '')
    text = link.get_text(strip=True)
    if '/page/2' in href or 'page=2' in href or text == '2':
        print(f"✓ Found page 2 link:")
        print(f"   Text: {text}")
        print(f"   Href: {href}")
        print(f"   Classes: {link.get('class', [])}\n")
