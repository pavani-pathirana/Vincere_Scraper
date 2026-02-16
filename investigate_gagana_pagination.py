"""Investigate Gagana's pagination mechanism"""
import requests
from bs4 import BeautifulSoup
import json

url = "https://gagana.lk/news/politics"

print("=== Testing Category Page ===")
response = requests.get(url, timeout=15)
print(f"Status: {response.status_code}\n")

soup = BeautifulSoup(response.text, 'lxml')

# Look for pagination elements
print("=== Pagination Elements ===")
pagination = soup.select('.pagination, [class*="pag"], .load-more, [class*="load"]')
for elem in pagination:
    print(f"Element: <{elem.name}> class='{elem.get('class')}'")
    print(f"  Text: {elem.get_text(strip=True)[:100]}")
    if elem.find('a'):
        links = elem.find_all('a', href=True)
        for link in links[:3]:
            print(f"  Link: {link.get('href')} - {link.get_text(strip=True)}")

# Look for AJAX/API endpoints in scripts
print("\n=== Checking for API endpoints in scripts ===")
scripts = soup.find_all('script')
for i, script in enumerate(scripts):
    script_text = script.string or ''
    if 'api' in script_text.lower() or 'ajax' in script_text.lower() or 'fetch' in script_text.lower():
        print(f"\nScript {i+1} contains API/AJAX references:")
        # Look for URLs
        import re
        urls = re.findall(r'["\']https?://[^"\']+["\']', script_text)
        for url_match in urls[:5]:
            print(f"  {url_match}")
        
        # Look for endpoint patterns
        endpoints = re.findall(r'["\']/?api/[^"\']+["\']', script_text)
        for endpoint in endpoints[:5]:
            print(f"  Endpoint: {endpoint}")

# Check for data attributes that might indicate infinite scroll
print("\n=== Checking for infinite scroll attributes ===")
scrollable = soup.select('[data-page], [data-next], [data-load], [class*="infinite"]')
for elem in scrollable[:5]:
    print(f"<{elem.name}> {elem.attrs}")

# Look for the container that holds articles
print("\n=== Article Container ===")
container = soup.select_one('.lsb-sec-items, [class*="items"]')
if container:
    print(f"Container: <{container.name}> class='{container.get('class')}'")
    print(f"Attributes: {container.attrs}")
    
# Check if there's a "next page" URL pattern we can construct
print("\n=== Testing constructed page URLs ===")
test_urls = [
    "https://gagana.lk/news/politics/page/2",
    "https://gagana.lk/news/politics?page=2",
    "https://gagana.lk/news/politics?offset=36",
    "https://gagana.lk/api/articles?category=politics&page=2",
]

for test_url in test_urls:
    try:
        response = requests.get(test_url, timeout=10)
        print(f"\n{test_url}")
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            posts = soup.select('.a-item')
            print(f"  Posts found: {len(posts)}")
            if len(posts) > 0:
                print(f"  ✓ THIS WORKS!")
                # Check if articles are different from page 1
                first_title = posts[0].get_text(strip=True)[:50]
                print(f"  First article: {first_title}")
    except Exception as e:
        print(f"\n{test_url}")
        print(f"  Error: {e}")
