"""Test Lankapuvath category page structure"""
import requests
from bs4 import BeautifulSoup

url = "https://sinhala.lankapuvath.lk/category/local/"

response = requests.get(url, timeout=15)
print(f"Status: {response.status_code}\n")

soup = BeautifulSoup(response.text, 'lxml')

# Try multiple selectors
print("=== Testing different selectors ===")
print(f".random-post: {len(soup.select('.random-post'))}")
print(f"[class*='post']: {len(soup.select('[class*=\"post\"]'))}")
print(f"article: {len(soup.select('article'))}")
print(f".entry: {len(soup.select('.entry'))}")
print(f".item: {len(soup.select('.item'))}")

# Find any container that might hold articles
print("\n=== Sample container classes ===")
all_divs = soup.find_all('div', class_=True, limit=20)
for div in all_divs:
    classes = ' '.join(div.get('class', []))
    # Look for article-related classes
    if any(keyword in classes.lower() for keyword in ['post', 'article', 'news', 'entry', 'item', 'content']):
        print(f"  {classes}")

# Look for links to articles
print("\n=== Article links (first 10) ===")
links = soup.find_all('a', href=True, limit=30)
article_links = []
for link in links:
    href = link.get('href', '')
    if '/202' in href and 'category' not in href:
        article_links.append(href)
        if len(article_links) <= 10:
            title = link.get_text(strip=True)
            print(f"  {title[:50]}")
            print(f"  → {href}\n")
