import requests
from bs4 import BeautifulSoup

# Test Divaina category page with more selectors
url = 'https://www.divaina.lk/category/main-news'

print("Testing Divaina category page structure (detailed)...")
print(f"URL: {url}\n")

response = requests.get(url, timeout=10, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

soup = BeautifulSoup(response.content, 'lxml')

#Try multiple selectors
selectors = [
    ('article', 'article tag'),
    ('.jeg_post', '.jeg_post class'),
    ('[class*="jeg_post"]', 'class containing jeg_post'),
    ('.post', '.post class'),    ('.jeg_posts .jeg_block_container', 'jeg block container'),
    ('.jeg_postblock', '.jeg_postblock class'),
    ('.jeg_block_container > *', 'jeg_block_container children')
]

for selector, description in selectors:
    elements = soup.select(selector)
    if elements:
        print(f"\n{description}: Found {len(elements)} elements")
        
        first = elements[0]
        print(f"  First element tag: {first.name}")
        print(f"  Classes: {first.get('class')}")
        
        # Find link
        link = first.select_one('a')
        if link:
            print(f"  Link: {link.get('href')[:80] if link.get('href') else 'None'}")
        
        # Find headline
        headline = first.select_one('h2, h3, .jeg_post_title')
        if headline:
            print(f"  Headline: {headline.get_text(strip=True)[:80]}")
        else:
            # Try to find any text
            text = first.get_text(strip=True)[:100]
            print(f"  Text preview: {text}")
        
        break  # Stop after finding first match

# Also check raw HTML structure
print("\n" + "="*70)
print("Checking page body classes:")
body = soup.select_one('body')
if body:
    print(f"Body classes: {body.get('class')}")

# Find main content area
main_areas = soup.select('.jeg_main, #main, .main-content, [role="main"]')
print(f"\nMain content areas: {len(main_areas)}")
for area in main_areas:
    print(f"  {area.name}.{' '.join(area.get('class', []))}")
