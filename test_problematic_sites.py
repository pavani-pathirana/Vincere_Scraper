"""Deep dive into problematic sites"""

import requests
from bs4 import BeautifulSoup

print("="*70)
print("LAKVAHINI - Finding content selector")
print("="*70)

url = "https://lakvahini.lk/archives/17825/"
r = requests.get(url)
soup = BeautifulSoup(r.text, 'lxml')

# Try to find content container
print("\nSearching for content...")
candidates = [
    'article',
    '.post',
    '.content',
    '[class*="post"]',
    '[class*="content"]',
    '[class*="entry"]'
]

for selector in candidates:
    elem = soup.select_one(selector)
    if elem:
        paras = elem.select('p')
        print(f"\n✓ {selector}:")
        print(f"  Paragraphs: {len(paras)}")
        if paras:
            for i, p in enumerate(paras[:3], 1):
                text = p.get_text(strip=True)
                if len(text) > 30:
                    print(f"  {i}. {text[:120]}")

print("\n" + "="*70)
print("ASIAN MIRROR - Finding article selector on category page")
print("="*70)

url2 = "https://sinhala.asianmirror.lk/news/local/"
r2 = requests.get(url2)
soup2 = BeautifulSoup(r2.text, 'lxml')

print(f"\nTrying different selectors...")
selectors = [
    'article',
    '.post',
    '[class*="post"]',
    '[class*="entry"]',
    'h2 a',
    'h3 a',
    '.entry-title a'
]

for sel in selectors:
    elems = soup2.select(sel)
    if len(elems) > 5:
        print(f"\n✓ {sel}: {len(elems)} elements")
        for i, elem in enumerate(elems[:3], 1):
            if elem.name == 'a':
                print(f"  {i}. {elem.get_text(strip=True)[:60]}")
                print(f"     → {elem.get('href')}")
            else:
                link = elem.select_one('a')
                if link:
                    print(f"  {i}. {link.get_text(strip=True)[:60]}")
                    print(f"     → {link.get('href')}")

print("\n" + "="*70)
print("SIYATHA NEWS - Finding content selector")
print("="*70)

url3 = "https://siyathanews.lk/archives/167174"
r3 = requests.get(url3)
soup3 = BeautifulSoup(r3.text, 'lxml')

for selector in candidates:
    elem = soup3.select_one(selector)
    if elem:
        paras = elem.select('p')
        print(f"\n✓ {selector}:")
        print(f"  Paragraphs: {len(paras)}")
        if paras:
            for i, p in enumerate(paras[:3], 1):
                text = p.get_text(strip=True)
                if len(text) > 30:
                    print(f"  {i}. {text[:120]}")
