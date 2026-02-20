"""
Deep investigation of Asian Mirror page structure
"""

import requests
from bs4 import BeautifulSoup

url = 'https://sinhala.asianmirror.lk/news/local/'

print(f"Testing: {url}\n")

r = requests.get(url, timeout=10)
r.encoding = 'utf-8'
soup = BeautifulSoup(r.text, 'lxml')

print("="*70)
print("FULL LINK ANALYSIS")
print("="*70)

all_links = soup.select('a[href]')
print(f"\nTotal links on page: {len(all_links)}\n")

# Categorize links
categories = []
articles = []
navigation = []
other = []

for link in all_links:
    href = link.get('href', '')
    text = link.get_text(strip=True)
    
    # Skip empty/short
    if not href or not text or len(text) < 3:
        continue
    
    # Categorize
    if href.endswith('/local/') or href.endswith('/political/') or href.endswith('/sports/'):
        categories.append((text, href))
    elif '/news/' in href and href.count('/') >= 5:  # Has category + slug
        articles.append((text, href))
    elif '#' in href or 'page/' in href:
        navigation.append((text, href))
    else:
        other.append((text, href))

print(f"Category links: {len(categories)}")
print(f"Article links: {len(articles)}")
print(f"Navigation links: {len(navigation)}")
print(f"Other links: {len(other)}")

if articles:
    print("\n" + "="*70)
    print("ARTICLE LINKS FOUND")
    print("="*70)
    for i, (text, href) in enumerate(articles[:10], 1):
        print(f"{i}. {text[:60]}")
        print(f"   {href}\n")
else:
    print("\n" + "="*70)
    print("NO ARTICLE LINKS - Showing 'other' links:")
    print("="*70)
    for i, (text, href) in enumerate(other[:15], 1):
        print(f"{i}. {text[:50]}")
        print(f"   {href}\n")

# Check for specific HTML patterns
print("\n" + "="*70)
print("HTML STRUCTURE ANALYSIS")
print("="*70)

# Check for common WordPress/article structures
patterns = {
    'article tags': soup.select('article'),
    'posts (class)': soup.select('[class*="post"]'),
    'entry-title': soup.select('.entry-title'),
    'h2': soup.select('h2'),
    'h3': soup.select('h3'),
    'main content': soup.select('main, #main, .main, #content, .content'),
}

for name, elements in patterns.items():
    print(f"{name}: {len(elements)} found")
    if elements and len(elements) < 5:
        for elem in elements:
            print(f"  - {elem.name} {elem.get('class', [])} {elem.get('id', '')}")

# Check page title
print(f"\nPage title: {soup.title.text if soup.title else 'None'}")

# Check for JavaScript indicators
scripts = soup.select('script[src]')
print(f"\nExternal scripts: {len(scripts)}")
for script in scripts[:5]:
    src = script.get('src', '')
    if 'react' in src.lower() or 'vue' in src.lower() or 'angular' in src.lower():
        print(f"  ⚠️  Found JS framework: {src}")
