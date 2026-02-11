"""Test CSS selector for ITN links"""
import requests
from bs4 import BeautifulSoup

url = "https://www.itnnews.lk/local/"
print(f"Fetching: {url}")

response = requests.get(url, timeout=10)
soup = BeautifulSoup(response.content, 'lxml')

print(f"\nPage loaded: {len(response.content)} bytes")
print("="*70)

# Try the selector that's failing
selector1 = 'a[href*="itnnews.lk/2026/"]'
links1 = soup.select(selector1)
print(f"\nSelector: {selector1}")
print(f"Found: {len(links1)} links")

# Try simpler selectors
selector2 = 'a[href*="/2026/"]'
links2 = soup.select(selector2)
print(f"\nSelector: {selector2}")
print(f"Found: {len(links2)} links")

# Try to find ANY link with 2026
selector3 = 'a'
all_links = soup.select(selector3)
print(f"\nTotal <a> tags: {len(all_links)}")

# Check how many have 2026 in them
links_with_2026 = [a for a in all_links if '2026' in str(a.get('href', ''))]
print(f"Links with '2026' in href: {len(links_with_2026)}")

if links_with_2026:
    print("\nFirst 5 hrefs with 2026:")
    for i, link in enumerate(links_with_2026[:5], 1):
        href = link.get('href', '')
        print(f"  {i}. {href}")
        print(f"     Type: {type(href)}")
        print(f"     Contains 'itnnews.lk': {'itnnews.lk' in href}")
