"""
Find the exact selector for Asian Mirror article links
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

url = 'https://sinhala.asianmirror.lk/news/local/'

print(f"Testing: {url}\n")

r = requests.get(url, timeout=10)
r.encoding = 'utf-8'
soup = BeautifulSoup(r.text, 'lxml')

# Function to check if URL is an article
def is_article_url(href):
    """Check if URL is an article (not category/navigation)"""
    if not href:
        return False
    
    # Must contain /news/
    if '/news/' not in href:
        return False
    
    # Should not end with /local/, /political/, etc (category pages)
    if href.rstrip('/').endswith(('/local', '/political', '/sports', '/international', '/business', '/crime', '/special', '/technological')):
        return False
    
    # Should have a slug after category
    parts = href.rstrip('/').split('/')
    # Expected: ['https:', '', 'sinhala.asianmirror.lk', 'news', 'category', 'slug']
    if len(parts) >= 6:  # Has category and slug
        return True
    
    return False

# Test various selectors
test_selectors = [
    ('article a', soup.select('article a')),
    ('.post a', soup.select('.post a')),
    ('[class*="post"] a', soup.select('[class*="post"] a')),
    ('h3 a', soup.select('h3 a')),
    ('.entry-title a', soup.select('.entry-title a')),
    ('a[href*="/news/"]', soup.select('a[href*="/news/"]')),
]

print("="*70)
print("SELECTOR TEST RESULTS")
print("="*70)

for selector_name, links in test_selectors:
    article_links = [link for link in links if is_article_url(link.get('href', ''))]
    
    print(f"\n{selector_name}: {len(article_links)} article links found")
    
    if article_links:
        print("Sample articles:")
        for i, link in enumerate(article_links[:5], 1):
            title = link.get_text(strip=True)
            href = link.get('href')
            parent_class = link.parent.get('class', []) if link.parent else []
            print(f"  {i}. {title[:50]}")
            print(f"     URL: {href}")
            print(f"     Parent: {link.parent.name} {parent_class}")

# Find the best selector by checking parent structure
print("\n" + "="*70)
print("EXAMINING ARTICLE LINK PARENTS")
print("="*70)

all_links = soup.select('a[href]')
article_links = [link for link in all_links if is_article_url(link.get('href', ''))]

print(f"\nFound {len(article_links)} total article links\n")

parent_patterns = {}
for link in article_links:
    # Build parent chain
    parent = link.parent
    while parent and parent.name != 'body':
        classes = ' '.join(parent.get('class', []))
        if classes:
            key = f"{parent.name}.{classes}"
            if key not in parent_patterns:
                parent_patterns[key] = 0
            parent_patterns[key] += 1
        parent = parent.parent

print("Most common parent patterns:")
for pattern, count in sorted(parent_patterns.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {pattern}: {count} links")

# Sample article link HTML
print("\n" + "="*70)
print("SAMPLE ARTICLE LINK HTML")
print("="*70)
if article_links:
    sample = article_links[0]
    print(f"\nTitle: {sample.get_text(strip=True)}")
    print(f"URL: {sample.get('href')}")
    print(f"Classes: {sample.get('class', [])}")
    print(f"\nParent HTML:")
    print(sample.parent.prettify()[:500] if sample.parent else "No parent")
