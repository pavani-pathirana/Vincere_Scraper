"""Detailed test for dasathalankanews.com"""

import requests
from bs4 import BeautifulSoup

url = "https://dasathalankanews.com/local-news/"

response = requests.get(url, timeout=10, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

print(f"Status: {response.status_code}")
print(f"Content length: {len(response.text)}")

soup = BeautifulSoup(response.text, 'lxml')

# Save a sample of the HTML
with open('dasatha_sample.html', 'w', encoding='utf-8') as f:
    f.write(response.text[:5000])
    print("Saved first 5000 chars to dasatha_sample.html")

# Look for all divs with class
divs_with_class = soup.find_all('div', class_=True)
print(f"\nDivs with classes: {len(divs_with_class)}")
print("First 10 div classes:")
for div in divs_with_class[:10]:
    classes = ' '.join(div.get('class', []))
    print(f"  .{classes}")

# Look for links
all_links = soup.find_all('a', href=True)
print(f"\nTotal links: {len(all_links)}")

# Filter for article-like links
article_links = []
for link in all_links:
    href = link.get('href', '')
    text = link.get_text(strip=True)
    if 'dasathalankanews.com' in href and len(text) > 20:
        article_links.append((text[:60], href))

print(f"\nArticle-like links: {len(article_links)}")
for text, href in article_links[:10]:
    print(f"  {text}")
    print(f"    {href}")

# Look for main content area
main_selectors = ['main', '#main', '.main', '#content', '.content', '#primary', '.primary']
for selector in main_selectors:
    elem = soup.select_one(selector)
    if elem:
        print(f"\nFound {selector}: {len(elem.get_text(strip=True))} chars")
