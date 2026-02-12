"""
Debug Lankadeepa pagination
"""
import requests
from bs4 import BeautifulSoup

url = 'https://www.lankadeepa.lk/business'
response = requests.get(url, timeout=30, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

print(f"Status: {response.status_code}")
print(f"URL: {response.url}")

soup = BeautifulSoup(response.content, 'lxml')

# Look for pagination elements
print("\n" + "="*70)
print("PAGINATION SEARCH")
print("="*70)

# Common pagination selectors
pagination_selectors = [
    'nav[class*="pagination"]',
    'ul[class*="pagination"]',
    'div[class*="pagination"]',
    '.pagination',
    '.pager',
    '.page-numbers',
    'a[rel="next"]',
    'a[href*="page="]',
    'a[href*="/page/"]',
    'a[class*="next"]',
    'button[class*="next"]',
]

for selector in pagination_selectors:
    elements = soup.select(selector)
    if elements:
        print(f"\n✓ Found with selector: {selector}")
        for elem in elements[:5]:  # Show first 5
            text = elem.get_text(strip=True)
            href = elem.get('href', '')
            print(f"  Text: {text[:50]}")
            print(f"  Href: {href}")

# Look for "Load More" buttons
print("\n" + "="*70)
print("LOAD MORE / INFINITE SCROLL")
print("="*70)

load_more_selectors = [
    'button[class*="load"]',
    'a[class*="load"]',
    'div[class*="load"]',
    '[data-next-page]',
    '[data-load-more]',
]

for selector in load_more_selectors:
    elements = soup.select(selector)
    if elements:
        print(f"\n✓ Found with selector: {selector}")
        for elem in elements[:3]:
            print(f"  {elem}")

# Check for AJAX/JavaScript pagination
print("\n" + "="*70)
print("JAVASCRIPT/AJAX CLUES")
print("="*70)

scripts = soup.find_all('script', src=True)
print(f"Found {len(scripts)} script tags")
for script in scripts[:5]:
    src = script.get('src', '')
    if 'pagination' in src.lower() or 'infinite' in src.lower() or 'scroll' in src.lower():
        print(f"  Relevant script: {src}")

# Look for page numbers in links
print("\n" + "="*70)
print("ALL LINKS WITH NUMBERS")
print("="*70)

all_links = soup.select('a[href]')
page_links = []
for link in all_links:
    href = link.get('href', '')
    text = link.get_text(strip=True)
    # Look for page numbers
    if any(x in href.lower() for x in ['page', 'start', 'offset', 'limit']):
        page_links.append((text, href))
    # Look for numeric links (page numbers)
    if text.isdigit():
        page_links.append((text, href))

if page_links:
    print(f"Found {len(page_links)} potential pagination links:")
    for text, href in page_links[:10]:
        print(f"  [{text}] -> {href}")
else:
    print("No pagination links found")

# Check if there's a "start" parameter pattern
print("\n" + "="*70)
print("TRYING MANUAL PAGINATION PATTERNS")
print("="*70)

test_urls = [
    'https://www.lankadeepa.lk/business?page=2',
    'https://www.lankadeepa.lk/business/page/2',
    'https://www.lankadeepa.lk/business?start=20',
    'https://www.lankadeepa.lk/business?limit=20&start=20',
]

for test_url in test_urls:
    try:
        resp = requests.get(test_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        print(f"\n{test_url}")
        print(f"  Status: {resp.status_code}")
        print(f"  Redirected: {resp.url != test_url}")
        if resp.status_code == 200:
            test_soup = BeautifulSoup(resp.content, 'lxml')
            articles = len(test_soup.select('a[href*="/business/"]'))
            print(f"  Business article links: {articles}")
    except Exception as e:
        print(f"  Error: {e}")
