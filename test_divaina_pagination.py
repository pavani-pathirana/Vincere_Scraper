import requests
from bs4 import BeautifulSoup

# Test Divaina pagination
url = 'https://www.divaina.lk/category/sports-news'

print("Testing Divaina pagination...\n")

response = requests.get(url, timeout=10, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

soup = BeautifulSoup(response.content, 'lxml')

# Look for pagination elements
pagination_selectors = [
    '.pagination',
    '.pager',
    '.page-numbers',
    '[class*="pag"]',
    'a[rel="next"]',
    'a[href*="page"]',
    '.next',
    'nav[class*="pag"]'
]

print("Searching for pagination elements:")
for selector in pagination_selectors:
    elements = soup.select(selector)
    if elements:
        print(f"\n{selector}: Found {len(elements)} elements")
        for elem in elements[:5]:
            classes = elem.get('class', [])
            print(f"  {elem.name}.{'.'.join(classes)}: {elem.get_text(strip=True)[:50]}")
            if elem.get('href'):
                print(f"    href: {elem.get('href')}")

# Check for "Load More" or AJAX pagination
load_more = soup.select('[class*="load"], [class*="more"], button')
if load_more:
    print(f"\nLoad more buttons: {len(load_more)}")
    for btn in load_more[:3]:
        print(f"  {btn.name}: {btn.get('class')} - {btn.get_text(strip=True)[:50]}")
        print(f"    data attrs: {[k for k in btn.attrs if k.startswith('data-')]}")

print("\n" + "="*70)
print("Testing page 2 URL patterns...")
print("="*70)

test_urls = [
    'https://www.divaina.lk/category/sports-news/page/2/',
    'https://www.divaina.lk/category/sports-news?page=2',
    'https://www.divaina.lk/category/sports-news/page/2',
    'https://www.divaina.lk/category/sports-news/2/'
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
            articles = test_soup.select('.p-wrap')
            print(f"  ✓ Article containers: {len(articles)}")
            
            # Compare with page 1
            if len(articles) > 0:
                first_link = test_soup.select_one('.p-wrap a')
                if first_link:
                    print(f"  First article: {first_link.get('href')}")
            
    except Exception as e:
        print(f"\n{test_url}")
        print(f"  Error: {str(e)[:50]}")
