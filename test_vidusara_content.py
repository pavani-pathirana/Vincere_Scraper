"""
Find Vidusara content container
"""

import requests
from bs4 import BeautifulSoup

url = "https://www.vidusara.lk/science-news/9177/"

response = requests.get(url, timeout=10)
soup = BeautifulSoup(response.text, 'lxml')

print("Finding content container:")
print("=" * 70)

# Look for common content classes
article = soup.find('article')
if article:
    print("\n<article> contents:")
    
    # Find all divs with content-related classes
    content_divs = article.find_all(['div', 'section'], class_=True)
    
    for div in content_divs[:10]:
        classes = div.get('class', [])
        paragraphs = div.find_all('p')
        if paragraphs:
            print(f"\n  Classes: {classes}")
            print(f"  Paragraphs: {len(paragraphs)}")
            if paragraphs:
                print(f"  First para preview: {paragraphs[0].get_text(strip=True)[:80]}...")

# Try direct paragraph search
print("\n" + "=" * 70)
print("All paragraphs in article:")
print("=" * 70)

paragraphs = article.find_all('p') if article else soup.find_all('p')
print(f"Total paragraphs found: {len(paragraphs)}")

if paragraphs:
    for i, p in enumerate(paragraphs[:5], 1):
        text = p.get_text(strip=True)
        if len(text) > 20:
            parent_class = p.parent.get('class', []) if p.parent else []
            print(f"\n{i}. {text[:100]}...")
            print(f"   Parent: {p.parent.name if p.parent else 'None'} - {parent_class}")
