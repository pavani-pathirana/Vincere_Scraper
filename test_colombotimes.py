"""Deep dive analysis for Colombo Times"""

import requests
from bs4 import BeautifulSoup

print("="*70)
print("COLOMBO TIMES SINHALA - Article Structure Analysis")
print("="*70)

# Test category page
category_url = "https://colombotimes.lk/sinhala/local"
print(f"\n1. Category Page: {category_url}")
r = requests.get(category_url)
soup = BeautifulSoup(r.text, 'lxml')

# Find article links
articles = soup.select('.post')
print(f"Found {len(articles)} article containers")

if articles:
    first = articles[0]
    link = first.select_one('a')
    print(f"\nFirst article:")
    print(f"  Title: {link.get_text(strip=True) if link else 'N/A'}")
    print(f"  URL: {link.get('href') if link else 'N/A'}")
    print(f"  Classes: {first.get('class')}")

# Test pagination
pagination = soup.select('.pagination a, .nav-links a, a[rel="next"]')
print(f"\nPagination links: {len(pagination)}")
for p in pagination[:3]:
    print(f"  {p.get_text(strip=True)}: {p.get('href')}")

# Test individual article page
if articles and articles[0].select_one('a'):
    article_url = articles[0].select_one('a').get('href')
    print(f"\n2. Article Page: {article_url}")
    r2 = requests.get(article_url)
    soup2 = BeautifulSoup(r2.text, 'lxml')
    
    # Find content
    title = soup2.select_one('h1, .entry-title, .post-title')
    print(f"  Title: {title.get_text(strip=True)[:80] if title else 'N/A'}")
    
    content_selectors = [
        '.entry-content',
        '.post-content',
        'article .content',
        '.article-content',
        '[class*="content"]'
    ]
    
    for sel in content_selectors:
        content = soup2.select_one(sel)
        if content:
            paras = content.select('p')
            print(f"  Content selector: {sel}")
            print(f"  Paragraphs: {len(paras)}")
            if paras:
                print(f"  First para: {paras[0].get_text(strip=True)[:100]}")
            break
    
    # Find date
    date = soup2.select_one('time, .date, .post-date, [class*="date"]')
    if date:
        print(f"  Date element: {date.get_text(strip=True)}")
        print(f"  Date attrs: {date.attrs}")
    
    # Find author
    author = soup2.select_one('.author, .by, [rel="author"]')
    if author:
        print(f"  Author: {author.get_text(strip=True)}")
