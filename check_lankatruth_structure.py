"""Check LankaTruth HTML structure"""
import requests
from bs4 import BeautifulSoup

url = 'https://lankatruth.com/si/?cat=3'

resp = requests.get(url, timeout=15, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

print(f"Status: {resp.status_code}")
print(f"URL: {url}\n")

soup = BeautifulSoup(resp.content, 'lxml')

# Try different selectors
selectors = [
    'article',
    '.post', 
    'article.post',
    '.entry',
    'article.entry',
    '.entry-title a',
    'article h2 a',
    '.post-title a',
    'h2.entry-title a',
]

for selector in selectors:
    elements = soup.select(selector)
    print(f"{selector:30s} | Count: {len(elements)}")
    if len(elements) > 0 and len(elements) < 5:
        for elem in elements[:3]:
            if elem.name == 'a':
                print(f"  -> {elem.get('href', 'NO HREF')[:60]} | {elem.get_text()[:40]}")
            else:
                title_link = elem.select_one('h2 a') or elem.select_one('.entry-title a') or elem.select_one('a')
                if title_link:
                    print(f"  -> {title_link.get('href', 'NO HREF')[:60]}")

# Show a sample article structure
print("\n" + "="*70)
print("FIRST ARTICLE STRUCTURE:")
print("="*70)
first_article = soup.select_one('article')
if first_article:
    print(first_article.prettify()[:1000])
else:
    print("NO ARTICLE TAG FOUND")
    
# Try to find any links that look like article links
print("\n" + "="*70)
print("SAMPLE LINKS:")
print("="*70)
all_links = soup.select('a')
for link in all_links[:15]:
    href = link.get('href', '')
    text = link.get_text().strip()[:50]
    if text and 'lankatruth.com' in href:
        print(f"  {text:50s} | {href}")
