"""Detailed test for aruna.lk"""

import requests
from bs4 import BeautifulSoup

url = "https://www.aruna.lk/categories/sports"

response = requests.get(url, timeout=10, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

print(f"Status: {response.status_code}")
print(f"Content length: {len(response.text)}")

soup = BeautifulSoup(response.text, 'lxml')

# Save a sample
with open('aruna_sample.html', 'w', encoding='utf-8') as f:
    f.write(response.text[:5000])
    print("Saved first 5000 chars to aruna_sample.html")

# Look for all divs with class
divs_with_class = soup.find_all('div', class_=True)
print(f"\nDivs with classes: {len(divs_with_class)}")
print("First 15 div classes:")
for div in divs_with_class[:15]:
    classes = ' '.join(div.get('class', []))
    print(f"  .{classes}")

# Look for links
all_links = soup.find_all('a', href=True)
print(f"\nTotal links: {len(all_links)}")

# Look for article/news links
article_links = []
for link in all_links:
    href = link.get('href', '')
    text = link.get_text(strip=True)
    # Look for news/article patterns in URL
    if ('aruna.lk' in href or href.startswith('/')) and len(text) > 15 and not any(x in href.lower() for x in ['facebook', 'twitter', 'youtube', 'instagram', 'category', 'categories']):
        article_links.append((text[:70], href))

print(f"\nPotential article links: {len(article_links)}")
for text, href in article_links[:15]:
    print(f"  {text}")
    print(f"    {href}")
