"""
Check what URLs are on Asian Mirror political page
"""

import requests
from bs4 import BeautifulSoup

url = 'https://sinhala.asianmirror.lk/news/political/'

print(f"Checking: {url}\n")

r = requests.get(url, timeout=10)
r.encoding = 'utf-8'
soup = BeautifulSoup(r.text, 'lxml')

# Find article links
article_links = soup.select('li.listitem a')

print(f"Found {len(article_links)} links\n")

for i, link in enumerate(article_links[:15], 1):
    href = link.get('href', '')
    text = link.get_text(strip=True)
    
    # Check if it's a real article URL
    if '/news/' in href and href.count('/') >= 6:
        print(f"{i}. {text}")
        print(f"   {href}\n")
