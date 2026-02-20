"""
Check Asian Mirror article page structure
"""

import requests
from bs4 import BeautifulSoup

url = 'https://sinhala.asianmirror.lk/news/breaking/breaking-news-198/'

print(f"Testing article: {url}\n")

r = requests.get(url, timeout=10)
r.encoding = 'utf-8'
soup = BeautifulSoup(r.text, 'lxml')

print("="*70)
print("PAGE STRUCTURE")
print("="*70)

# Check for content containers
selectors = {
    'article': soup.select('article'),
    '.entry-content': soup.select('.entry-content'),
    '.post-content': soup.select('.post-content'),
    '.content': soup.select('.content'),
    'main': soup.select('main'),
    '#main': soup.select('#main'),
    '.main-content': soup.select('.main-content'),
    '.article-content': soup.select('.article-content'),
    '[class*="content"]': soup.select('[class*="content"]'),
}

for selector, elements in selectors.items():
    print(f"\n{selector}: {len(elements)} found")
    if elements:
        elem = elements[0]
        # Count paragraphs
        paras = elem.select('p')
        print(f"  Paragraphs: {len(paras)}")
        if paras:
            print(f"  First para: {paras[0].get_text(strip=True)[:80]}...")

# Check for title
print("\n" + "="*70)
print("TITLE/HEADLINE")
print("="*70)

title_selectors = ['h1.entry-title', 'h1', '.entry-title', '.post-title', 'h1.title']
for selector in title_selectors:
    elem = soup.select_one(selector)
    if elem:
        print(f"{selector}: {elem.get_text(strip=True)}")
        break

# Show main content area HTML
print("\n" + "="*70)
print("MAIN CONTENT AREA HTML")
print("="*70)

main_content = soup.select_one('article, .post, .entry, [class*="post"]')
if main_content:
    print(main_content.prettify()[:1000])
else:
    print("No main content found")

# Check all classes on page
print("\n" + "="*70)
print("ALL UNIQUE CLASSES")
print("="*70)
all_classes = set()
for elem in soup.select('[class]'):
    classes = elem.get('class', [])
    all_classes.update(classes)

print(' '.join(sorted(all_classes)[:30]))
