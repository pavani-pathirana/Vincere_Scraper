"""Test AdaDerana to see exact HTML structure"""
import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Test homepage
resp = requests.get('https://sinhala.adaderana.lk/', timeout=15, headers=headers)
soup = BeautifulSoup(resp.content, 'lxml')

# Find news-story divs
news_stories = soup.select('div.news-story')
print(f"Found {len(news_stories)} news-story divs\n")

# Analyze first 3
for i, story in enumerate(news_stories[:3], 1):
    print(f"--- Story {i} ---")
    
    #Find link
    link = story.select_one('a')
    if link:
        href = link.get('href', '')
        print(f"Link: {href}")
        
        # Make absolute
        if href.startswith('news/'):
            full_url = f"https://sinhala.adaderana.lk/{href}"
            print(f"Full URL: {full_url}")
    
    # Find title
    for selector in ['h2', 'h3', 'h4', '.title']:
        title_elem = story.select_one(selector)
        if title_elem:
            title = title_elem.get_text().strip()
            if len(title) > 10:
                print(f"Title ({selector}): {title[:60]}")
                break
    
    print()

# Now test an article page
print("\n" + "="*70)
print("TESTING ARTICLE PAGE")
print("="*70)

article_url = 'https://sinhala.adaderana.lk/news/221321'
resp = requests.get(article_url, timeout=15, headers=headers)
soup = BeautifulSoup(resp.content, 'lxml')

print(f"\nArticle URL: {article_url}")
print(f"Status: {resp.status_code}\n")

# Try content selectors
selectors = [
    '.article-content',
    '.news-content',
    '#news-content',
    'div[class*="content"]',
    '.story-content',
    'article',
]

for selector in selectors:
    elem = soup.select_one(selector)
    if elem:
        text = elem.get_text().strip()
        if len(text) > 100:
            print(f"✓ Content found: {selector} ({len(text)} chars)")
            print(f"  Sample: {text[:150]}...")
            break
else:
    # Show main tag
    main = soup.select_one('main')
    if main:
        text = main.get_text().strip()
        print(f"? Fallback main tag: {len(text)} chars")
        # Find largest div
        all_divs = main.select('div')
        if all_divs:
            largest = max(all_divs, key=lambda d: len(d.get_text()))
            print(f"  Largest div: {largest.get('class', [])} = {len(largest.get_text())} chars")
