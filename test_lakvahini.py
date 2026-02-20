"""Deep dive analysis for Lakvahini"""

import requests
from bs4 import BeautifulSoup

print("="*70)
print("LAKVAHINI - Article Structure Analysis")
print("="*70)

# Test main page
main_url = "https://lakvahini.lk/"
print(f"\n1. Main Page: {main_url}")
r = requests.get(main_url)
soup = BeautifulSoup(r.text, 'lxml')

# Find article links
articles = soup.select('h3 a')
print(f"Found {len(articles)} article links (h3 a)")

if articles:
    for i, link in enumerate(articles[:3], 1):
        print(f"  {i}. {link.get_text(strip=True)[:60]}")
        print(f"     {link.get('href')}")

# Check for categories in menu
nav = soup.select('nav a, .menu a')
print(f"\nNavigation links: {len(nav)}")
for n in nav[:10]:
    text = n.get_text(strip=True)
    href = n.get('href', '')
    if text and len(text) < 40:
        print(f"  - {text}: {href}")

# Test individual article
if articles:
    article_url = articles[0].get('href')
    print(f"\n2. Article Page: {article_url}")
    r2 = requests.get(article_url)
    soup2 = BeautifulSoup(r2.text, 'lxml')
    
    title = soup2.select_one('h1, .entry-title')
    print(f"  Title: {title.get_text(strip=True)[:80] if title else 'N/A'}")
    
    for sel in ['.entry-content', 'article .content', '.content']:
        content = soup2.select_one(sel)
        if content:
            paras = content.select('p')
            print(f"  Content: {sel} ({len(paras)} paragraphs)")
            if paras:
                print(f"  Sample: {paras[0].get_text(strip=True)[:100]}")
            break
    
    date = soup2.select_one('time, .date, .posted-on')
    if date:
        print(f"  Date: {date.get_text(strip=True)}")
