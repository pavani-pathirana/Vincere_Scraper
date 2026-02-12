"""
Debug AdaDerana HTML structure
"""
import requests
from bs4 import BeautifulSoup
import re

url = "https://sinhala.adaderana.lk/news.php?id=5"
print(f"Fetching: {url}\n")

response = requests.get(url, timeout=30, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

print(f"Status: {response.status_code}")
print(f"Content-Length: {len(response.content)} bytes\n")

soup = BeautifulSoup(response.content, 'lxml')

# Look for article containers
print("=" * 70)
print("SEARCHING FOR ARTICLE CONTAINERS")
print("=" * 70)

containers = [
    'article',
    '.news-item',
    '.article-item',
    '.post',
    'div[class*="news"]',
    'div[class*="article"]',
]

for selector in containers:
    elems = soup.select(selector)
    if elems:
        print(f"✓ {selector}: {len(elems)} found")

# Look for links with date patterns
print("\n" + "=" * 70)
print("SEARCHING FOR ARTICLE LINKS")
print("=" * 70)

all_links = soup.select('a[href]')
print(f"Total links: {len(all_links)}")

# Try different patterns
patterns = {
    'news.php?nid=': re.compile(r'news\.php\?nid=\d+'),
    'news-article/': re.compile(r'news-article/\d+'),
    'article/': re.compile(r'article/\d+'),
    'nid=': re.compile(r'nid=\d+'),
}

for name, pattern in patterns.items():
    matches = [link for link in all_links if pattern.search(link.get('href', ''))]
    if matches:
        print(f"\n✓ Pattern '{name}': {len(matches)} matches")
        print(f"Sample URLs:")
        for link in matches[:5]:
            href = link.get('href', '')
            text = link.get_text(strip=True)[:50]
            print(f"  {href} - {text}")

# Look at overall structure
print("\n" + "=" * 70)
print("PAGE STRUCTURE")
print("=" * 70)

# Find main content area
main_areas = soup.select('main, #main, #content, .content, .main-content')
if main_areas:
    print(f"Main content areas: {len(main_areas)}")
    for area in main_areas[:2]:
        print(f"  Tag: {area.name}, Class: {area.get('class', [])}, ID: {area.get('id', '')}")

# Look for divs with many links
divs_with_links = []
for div in soup.find_all('div'):
    links = div.find_all('a', href=True, recursive=False)
    if len(links) >= 3:
        div_class = ' '.join(div.get('class', []))
        div_id = div.get('id', '')
        divs_with_links.append((len(links), div_class, div_id))

divs_with_links.sort(reverse=True)
print(f"\nDivs with most direct child links:")
for count, cls, id in divs_with_links[:5]:
    print(f"  {count} links - class='{cls}', id='{id}'")

# Look for headlines in Sinhala
print("\n" + "=" * 70)
print("SINHALA TEXT CONTENT")
print("=" * 70)

sinhala_links = []
for link in all_links[:30]:
    text = link.get_text(strip=True)
    if text and any('\u0d80' <= char <= '\u0dff' for char in text):
        sinhala_links.append((text[:50], link.get('href', '')))

if sinhala_links:
    print(f"Found {len(sinhala_links)} links with Sinhala text:")
    for text, href in sinhala_links[:10]:
        print(f"  {text} -> {href}")
