"""
Debug Vidusara category page structure
"""

import requests
from bs4 import BeautifulSoup

url = "https://www.vidusara.lk/category/science-news/"

print(f"Debugging: {url}")
print("=" * 70)

response = requests.get(url, timeout=10)
print(f"Status: {response.status_code}\n")

soup = BeautifulSoup(response.text, 'lxml')

# Try current selectors
print("Testing current selectors:")
print("-" * 70)

selectors = [
    'article.post',
    'article[class*="post"]',
    'article',
    '.post',
    '[class*="post"]'
]

for selector in selectors:
    items = soup.select(selector)
    print(f"{selector:30} → {len(items)} items")

# Find actual article links
print("\n" + "=" * 70)
print("Finding actual article links:")
print("=" * 70)

all_links = soup.find_all('a', href=True)
science_links = [l for l in all_links if ('/science-news/' in l.get('href', '') 
                                          and '/category/' not in l.get('href', '')
                                          and l.get_text(strip=True))]

print(f"\nFound {len(science_links)} article links")

if science_links:
    print("\nFirst 5 articles:")
    for i, link in enumerate(science_links[:5], 1):
        print(f"\n{i}. {link.get_text(strip=True)[:60]}")
        print(f"   URL: {link.get('href')}")
        
        # Check parent structure
        parent = link.find_parent()
        print(f"   Parent: <{parent.name}> - {parent.get('class', [])}")
        
        # Go up more levels
        article_parent = link.find_parent('article')
        if article_parent:
            print(f"   Article parent: {article_parent.get('class', [])}")
        
        # Check for div.post
        post_parent = link.find_parent(class_=lambda x: x and 'post' in ' '.join(x).lower())
        if post_parent:
            print(f"   Post parent: <{post_parent.name}> - {post_parent.get('class', [])}")
