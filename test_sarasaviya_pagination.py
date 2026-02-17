"""
Test Sarasaviya pagination structure
"""

import requests
from bs4 import BeautifulSoup

# Test URL - drama category
url = "https://sarasaviya.lk/category/drama/"

print(f"Testing: {url}")
print("=" * 70)

response = requests.get(url, timeout=10)
print(f"Status: {response.status_code}")

soup = BeautifulSoup(response.text, 'lxml')

# Check for posts
posts = soup.select('[class*="post"]')
print(f"\nFound {len(posts)} post containers")

# Look for pagination elements
print("\n=== Searching for pagination elements ===")

# Common WordPress pagination selectors
selectors = [
    '.next',
    '.next-page', 
    'a[rel="next"]',
    '.pagination .next',
    '.nav-links .next',
    '.nav-previous',
    '.wp-pagenavi a',
    '.pagination a',
    'a.next',
    'link[rel="next"]'
]

for selector in selectors:
    elements = soup.select(selector)
    if elements:
        print(f"\n✓ Found with '{selector}':")
        for elem in elements[:3]:  # Show first 3
            print(f"  Tag: {elem.name}")
            print(f"  Classes: {elem.get('class')}")
            print(f"  Href: {elem.get('href')}")
            print(f"  Text: {elem.get_text(strip=True)[:50]}")

# Look for any navigation
print("\n=== All navigation elements ===")
nav_elements = soup.select('.nav-links, .pagination, .wp-pagenavi, [class*="paginat"]')
if nav_elements:
    for nav in nav_elements:
        print(f"\nNav element: {nav.name}")
        print(f"Classes: {nav.get('class')}")
        print(f"HTML: {str(nav)[:300]}")
else:
    print("No navigation elements found")

# Check page numbers
print("\n=== Looking for page numbers ===")
page_links = soup.select('a[href*="/page/"]')
if page_links:
    print(f"Found {len(page_links)} page links:")
    for link in page_links[:5]:
        print(f"  {link.get('href')} - {link.get_text(strip=True)}")
else:
    print("No /page/ links found")

# Alternative: Look for numbered pagination
numbered = soup.select('a[href*="paged="], a[href*="page="]')
if numbered:
    print(f"\nFound {len(numbered)} query-param page links:")
    for link in numbered[:5]:
        print(f"  {link.get('href')} - {link.get_text(strip=True)}")
