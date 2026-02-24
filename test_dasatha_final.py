"""Better test for dasathalankanews.com structure"""

import requests
from bs4 import BeautifulSoup

url = "https://dasathalankanews.com/local-news/"

response = requests.get(url, timeout=15, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

soup = BeautifulSoup(response.text, 'lxml')

print("="*80)
print("DASATHALANKANEWS.COM STRUCTURE ANALYSIS")
print("="*80)

# Try to find main content container
print("\n1. Looking for main content container:")
main_containers = [
    ('main', soup.select_one('main')),
    ('#td-outer-wrap', soup.select_one('#td-outer-wrap')),
    ('.td-main-content-wrap', soup.select_one('.td-main-content-wrap')),
    ('.td-container', soup.select_one('.td-container')),
]

for name, elem in main_containers:
    if elem:
        print(f"  ✓ Found {name}")

# Look for article/post containers
print("\n2. Looking for article containers:")
selectors_to_try = [
    '.td-module-container',
    '.td-block-span12',
    '.td-module-thumb',
    '.td_module_wrap',
    '.td-post-card',
    '.entry',
    '.post'
]

for selector in selectors_to_try:
    elements = soup.select(selector)
    if elements:
        print(f"  ✓ {selector}: {len(elements)} found")

# Get the most promising selector
articles = soup.select('.td-module-container')
if not articles:
    articles = soup.select('.td_module_wrap')

print(f"\n3. Analyzing {len(articles)} article containers:")
for i, article in enumerate(articles[:5], 1):
    # Find title link
    title_link = article.select_one('h3 a, .entry-title a, .td-module-title a')
    if title_link:
        print(f"\n  Article {i}:")
        print(f"    Title: {title_link.get_text(strip=True)[:60]}")
        print(f"    URL: {title_link.get('href')}")
        
        # Find excerpt
        excerpt = article.select_one('.td-excerpt, .entry-summary')
        if excerpt:
            print(f"    Excerpt: {excerpt.get_text(strip=True)[:50]}...")

# Test pagination
print("\n4. Pagination analysis:")
pagination = soup.select('.page-nav a, .pagination a')
print(f"  Found {len(pagination)} pagination links")
for link in pagination[:3]:
    print(f"    {link.get_text(strip=True)}: {link.get('href')}")

# Test article page
if articles:
    first_link = articles[0].select_one('h3 a, .entry-title a, .td-module-title a')
    if first_link:
        article_url = first_link.get('href')
        print(f"\n5. Testing article page: {article_url[:70]}...")
        
        article_resp = requests.get(article_url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        article_soup = BeautifulSoup(article_resp.text, 'lxml')
        
        # Find title
        title = article_soup.select_one('h1.entry-title, h1')
        print(f"  Title: {title.get_text(strip=True) if title else 'NOT FOUND'}")
        
        # Find content
        content_selectors = [
            '.td-post-content',
            '.entry-content',
            '.post-content',
            'article .content'
        ]
        
        for selector in content_selectors:
            content = article_soup.select_one(selector)
            if content:
                paragraphs = content.select('p')
                text = content.get_text(strip=True)
                print(f"  Content ({selector}): {len(text)} chars, {len(paragraphs)} paragraphs")
                break
        
        # Find date
        date = article_soup.select_one('time, .entry-date, .td-post-date')
        if date:
            print(f"  Date: {date.get_text(strip=True)}")
            if date.get('datetime'):
                print(f"  Datetime attr: {date.get('datetime')}")
