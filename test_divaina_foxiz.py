import requests
from bs4 import BeautifulSoup

# Test Divaina for Foxiz theme structure
url = 'https://www.divaina.lk/category/main-news'

print("Testing Divaina (Foxiz  theme) structure...")
print(f"URL: {url}\n")

response = requests.get(url, timeout=10, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

soup = BeautifulSoup(response.content, 'lxml')

# Save HTML for inspection
with open('divaina_page.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
print("HTML saved to divaina_page.html")

# Check for various article/post structures
selectors = [
    'article',
    '.post',
    '[class*="post-"]',
    '.p-wrap',
    '.block-inner',
    '.rb-block-inner',
    '.is-ajax-loaded article',
    '#foxiz_loop_1 article',
    '[id*="foxiz"] article',
    '[data-id]'
]

print("\nSearching for article containers:")
for selector in selectors:
    elements = soup.select(selector)
    if elements:
        print(f"  ✓ {selector}: {len(elements)} elements")
        
        first = elements[0]
        print(f"    Tag: {first.name}, Classes: {first.get('class', [])[:3]}")
        print(f"    ID: {first.get('id')}")
        print(f"    Data attrs: {[k for k in first.attrs if k.startswith('data-')]}")
        
        # Find links
        links = first.select('a[href]')
        if links:
            print(f"    First link: {links[0].get('href')[:70]}")
        
        # Find headlines
        headlines = first.select('h1, h2, h3, h4, .entry-title, [class*="title"]')
        if headlines:
            print(f"    Headline: {headlines[0].get_text(strip=True)[:70]}")
        
        print()

# Check for AJAX/API indicators
scripts = soup.select('script')
print(f"\nTotal scripts: {len(scripts)}")

# Look for data embedded in page
data_elements = soup.select('[data-posts], [data-query], script[type="application/json"]')
print(f"Data elements: {len(data_elements)}")

for elem in data_elements[:2]:
    if elem.name == 'script':
        print(f"  JSON script: {elem.get_text()[:100]}")
    else:
        print(f"  {elem.name}: {elem.get('data-posts', elem.get('data-query', ''))[:100]}")

# Check for infinite scroll/lazy load
lazy_elements = soup.select('[data-page], [data-pagination], .pagination')
print(f"\nPagination/lazy load elements: {len(lazy_elements)}")
for elem in lazy_elements[:3]:
    print(f"  {elem.name}.{'.'.join(elem.get('class', []))}: {elem.get('data-page', '')} {elem.get('href', '')[:50]}")
