"""Test NewsFirst selector"""
import re
import requests
from bs4 import BeautifulSoup

url = "https://www.newsfirst.lk/sinhala/sports/"
print(f"Fetching: {url}")

response = requests.get(url, timeout=10)
soup = BeautifulSoup(response.content, 'lxml')

print(f"\nPage loaded: {len(response.content)} bytes")
print("="*70)

# Test the selector
all_links = soup.select('a[href*="sinhala/"]')  # NO leading slash
print(f"\nAll links with sinhala/: {len(all_links)}")

# Check hrefs
date_pattern_links = []
for link in all_links[:20]:  # Check first 20
    href = link.get('href', '')
    print(f"\nHref: {href}")
    print(f"  Type: {type(href)}")
    print(f"  Has 'sinhala/': {'sinhala/' in href}")
    
    # Check if it matches date pattern (without leading slash)
    match = re.search(r'sinhala/\d{4}/\d{2}/\d{2}/', href)
    if match:
        print(f"  [OK] Matches date pattern!")
        date_pattern_links.append(href)
    else:
        print(f"  [SKIP] Does NOT match date pattern")

print(f"\n{'='*70}")
print(f"Total links with date pattern: {len(date_pattern_links)}")
print("\nFirst 5 article URLs:")
for i, href in enumerate(date_pattern_links[:5], 1):
    print(f"  {i}. {href}")
