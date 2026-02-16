"""Test Gagana category page structure"""
import requests
from bs4 import BeautifulSoup

url = "https://gagana.lk/news/srilanka"

response = requests.get(url, timeout=15)
print(f"Status: {response.status_code}\n")

soup = BeautifulSoup(response.text, 'lxml')

# Try multiple selectors
print("=== Testing different selectors ===")
print(f".post-item: {len(soup.select('.post-item'))}")
print(f"[class*='post']: {len(soup.select('[class*=\"post\"]'))}")
print(f"article: {len(soup.select('article'))}")
print(f".card: {len(soup.select('.card'))}")

# Find container classes
print("\n=== Sample container classes (first 20 divs) ===")
all_divs = soup.find_all('div', class_=True, limit=30)
for div in all_divs:
    classes = ' '.join(div.get('class', []))
    if any(keyword in classes.lower() for keyword in ['post', 'article', 'news', 'card', 'item', 'content']):
        print(f"  {classes}")

# Look for article links
print("\n=== Article links (first 5) ===")
links = soup.find_all('a', href=True, limit=50)
article_links = []
for link in links:
    href = link.get('href', '')
    if '/article/' in href:
        article_links.append(href)
        if len(article_links) <= 5:
            title = link.get_text(strip=True)
            print(f"  {title[:60]}")
            print(f"  → {href}\n")

print(f"\nTotal article links found: {len(article_links)}")
