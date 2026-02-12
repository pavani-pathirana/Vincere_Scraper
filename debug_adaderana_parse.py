"""
Debug AdaDerana article parsing
"""
import requests
from bs4 import BeautifulSoup
import re

url = "https://sinhala.adaderana.lk/"
print(f"Fetching: {url}\n")

response = requests.get(url, timeout=30, headers={
    'User-Agent': 'Mozilla/5.0'
})

soup = BeautifulSoup(response.content, 'lxml')

# Test the actual selector logic from the scraper
print("=" * 70)
print("TESTING ARTICLE CONTAINER SELECTORS")
print("=" * 70)

selectors_to_test = [
    'div.news-item',
    'div.news-story',
    'div.news-block',
    'article.news',
    'div[class*="news"]',
]

for selector in selectors_to_test:
    elements = soup.select(selector)
    print(f"{selector:30s}: {len(elements)} found")

# Test fallback logic
print("\n" + "=" * 70)
print("TESTING FALLBACK LOGIC")
print("=" * 70)

content_area = soup.select_one('#content') or soup.select_one('.content') or soup
all_links = content_area.select('a[href]')
print(f"Total links in content area: {len(all_links)}")

# Test regex pattern
pattern = re.compile(r'(^|/)news/\d+')
matching_links = []

for link in all_links:
    href = link.get('href', '')
    if pattern.search(href):
        text = link.get_text(strip=True)[:60]
        matching_links.append((href, text))

print(f"\nLinks matching pattern '(^|/)news/\\d+': {len(matching_links)}")
if matching_links:
    print("Sample:")
    for href, text in matching_links[:10]:
        print(f"  {href}")
        print(f"    Text: {text}\n")

# Test if links are in containers
print("=" * 70)
print("CHECKING LINK STRUCTURE")
print("=" * 70)

# Find first matching link and check its parents
if matching_links:
    first_href = matching_links[0][0]
    first_link = soup.find('a', href=first_href)
    
    if first_link:
        print(f"First matching link: {first_href}")
        print(f"Link tag: {first_link.name}")
        print(f"Link classes: {first_link.get('class', [])}")
        
        print("\nParent hierarchy:")
        parent = first_link.parent
        level = 0
        while parent and level < 5:
            print(f"  Level {level}: <{parent.name} class='{' '.join(parent.get('class', []))}'>")
            parent = parent.parent
            level += 1
