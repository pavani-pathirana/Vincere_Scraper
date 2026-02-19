"""
Check Ada.lk saaravita article links more carefully
"""

import requests
from bs4 import BeautifulSoup

url = "https://www.ada.lk/saaravita/8"

response = requests.get(url, timeout=10)
soup = BeautifulSoup(response.text, 'lxml')

print("All href patterns in Ada saaravita:")
print("=" * 70)

all_links = soup.find_all('a', href=True)
href_patterns = {}

for link in all_links:
    href = link.get('href', '')
    if href and not href.startswith('http') and href != '#':
        # Get the first part of the path
        parts = href.strip('/').split('/')
        if parts:
            pattern = '/' + parts[0] + '/'
            if pattern not in href_patterns:
                href_patterns[pattern] = []
            if len(href_patterns[pattern]) < 3:  # Keep max 3 examples
                href_patterns[pattern].append(href)

print("\nUnique URL patterns:")
for pattern, examples in sorted(href_patterns.items()):
    print(f"\n{pattern}  ({len(examples)} examples)")
    for ex in examples:
        print(f"  {ex}")

# Check .cat-detail-1 containers
print("\n" + "=" * 70)
print("Checking .cat-detail-1 containers:")
print("=" * 70)

cat_details = soup.find_all(class_='cat-detail-1')
print(f"Found {len(cat_details)} .cat-detail-1 containers")

if cat_details:
    for i, container in enumerate(cat_details[:3], 1):
        print(f"\nContainer {i}:")
        # Find link in this container
        link = container.find('a', href=True)
        if link:
            print(f"  Link: {link.get('href')}")
            print(f"  Text: {link.get_text(strip=True)[:60]}")
