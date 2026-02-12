"""
Test actual Lankadeepa article structure
"""
import requests
from bs4 import BeautifulSoup
import re

# Test real article URLs from homepage
test_urls = [
    'https://www.lankadeepa.lk/business/සළ-හ-මධය-වයපර-කඩ-වටණත-රටම-කඩ-වටව/9-688100',
    'https://www.lankadeepa.lk/business/CWEIC-සභපත-ජනපත-හමවය/9-688099',
]

for url in test_urls:
    print("\n" + "=" * 70)
    print(f"Testing: {url}")
    print("=" * 70)
    
    try:
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Test headline selectors
            print("\nHeadline:")
            headline_selectors = ['h1', 'h2', '.article-title', '.title', '.headline']
            for selector in headline_selectors:
                elem = soup.select_one(selector)
                if elem:
                    text = elem.get_text(strip=True)
                    if len(text) > 10:
                        print(f"  {selector}: {text[:80]}")
                        break
            
            # Test body selectors
            print("\nBody content containers:")
            body_selectors = [
                'article',
                '.article-content',
                '.article-body',
                'div.content',
                'div[itemprop="articleBody"]',
                '.entry-content',
                '#content',
            ]
            
            for selector in body_selectors:
                elem = soup.select_one(selector)
                if elem:
                    text = elem.get_text(strip=True)
                    p_count = len(elem.select('p'))
                    if len(text) > 100:
                        print(f"  ✓ {selector}: {len(text)} chars, {p_count} paragraphs")
                        print(f"    Preview: {text[:150]}...")
            
            # Check for pagination/categories
            print("\nPage structure:")
            print(f"  Total paragraphs: {len(soup.select('p'))}")
            print(f"  Total images: {len(soup.select('img'))}")
            
            # Look for article metadata
            date_selectors = ['time', '.date', '.published', 'span[class*="date"]']
            for selector in date_selectors:
                elem = soup.select_one(selector)
                if elem:
                    print(f"  Date ({selector}): {elem.get_text(strip=True)}")
                    break
    
    except Exception as e:
        print(f"ERROR: {e}")

# Check homepage for article list structure
print("\n" + "=" * 70)
print("CHECKING HOMEPAGE ARTICLE LIST")
print("=" * 70)

homepage_url = 'https://www.lankadeepa.lk/'
response = requests.get(homepage_url, timeout=30, headers={
    'User-Agent': 'Mozilla/5.0'
})

soup = BeautifulSoup(response.content, 'lxml')

# Find article links with the pattern /category/title/id-number
pattern = re.compile(r'/[a-z-]+/[^/]+/\d+-\d+')
article_links = []

for link in soup.select('a[href]'):
    href = link.get('href', '')
    text = link.get_text(strip=True)
    
    if pattern.search(href) and text and len(text) > 15:
        # Check if Sinhala
        if any('\u0d80' <= char <= '\u0dff' for char in text):
            article_links.append((text[:60], href))

print(f"Found {len(article_links)} article links")
print("\nSample articles:")
for text, href in article_links[:10]:
    print(f"  {text}")
    print(f"    {href}\n")

# Check ifpagination exists
next_link = soup.select_one('a[rel="next"]') or soup.select_one('.next') or soup.select_one('a[href*="page="]')
if next_link:
    print(f"✓ Pagination found: {next_link.get('href', '')}")
else:
    print("✗ No pagination found on homepage")
