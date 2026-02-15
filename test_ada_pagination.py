import requests
from bs4 import BeautifulSoup

# Test Ada.lk pagination
url = 'https://www.ada.lk/sports/9'

print("Testing Ada.lk pagination...\n")

response = requests.get(url, timeout=10, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

soup = BeautifulSoup(response.content, 'lxml')

# Look for pagination elements
pagination_selectors = [
    '.pagination',
    '.pager',
    '[class*="page"]',
    'a[rel="next"]',
    'a[href*="page"]',
    '.next',
    '.previous',
    'nav'
]

print("Searching for pagination elements:")
for selector in pagination_selectors:
    elements = soup.select(selector)
    if elements:
        print(f"\n{selector}: Found {len(elements)} elements")
        for elem in elements[:3]:
            print(f"  {elem.name}: {elem.get('class')} - {elem.get_text(strip=True)[:50]}")
            if elem.get('href'):
                print(f"    href: {elem.get('href')}")

# Check for numeric page links
page_links = soup.select('a[href]')
page_urls = []
for link in page_links:
    href = link.get('href', '')
    text = link.get_text(strip=True)
    
    # Look for numeric pagination or "next" links
    if text.isdigit() or 'next' in text.lower() or 'පළමු' in text or 'ඊළඟ' in text:
        page_urls.append((text, href))

if page_urls:
    print(f"\nPotential page links found: {len(page_urls)}")
    for text, href in page_urls[:10]:
        print(f"  {text}: {href}")

# Test page 2 directly
print("\n" + "="*70)
print("Testing page 2 URL patterns...")
print("="*70)

test_urls = [
    'https://www.ada.lk/sports/9?page=2',
    'https://www.ada.lk/sports/9/page/2',
    'https://www.ada.lk/sports/page/2/9',
    'https://www.ada.lk/sports/9/2'
]

for test_url in test_urls:
    try:
        r = requests.get(test_url, timeout=5, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        print(f"\n{test_url}")
        print(f"  Status: {r.status_code}")
        
        if r.status_code == 200:
            test_soup = BeautifulSoup(r.content, 'lxml')
            links = test_soup.select('a[href]')
            article_links = [a.get('href') for a in links if '/sports/' in a.get('href', '') and '-' in a.get('href', '')]
            print(f"  ✓ Article links: {len(article_links)}")
            
    except Exception as e:
        print(f"\n{test_url}")
        print(f"  Error: {str(e)[:50]}")
