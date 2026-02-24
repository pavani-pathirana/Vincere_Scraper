"""Test if Aruna.lk has an API endpoint"""

import requests
import json

print("="*80)
print("ARUNA.LK API DISCOVERY")
print("="*80)

# Common Next.js API patterns
api_endpoints = [
    "https://www.aruna.lk/api/articles",
    "https://www.aruna.lk/api/categories/sports",
    "https://www.aruna.lk/api/news",
    "https://www.aruna.lk/_next/data",
    "https://api.aruna.lk/articles",
    "https://api.aruna.lk/categories/sports",
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
}

for endpoint in api_endpoints:
    try:
        response = requests.get(endpoint, headers=headers, timeout=10)
        print(f"\n{endpoint}")
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  Content-Type: {response.headers.get('Content-Type')}")
            print(f"  Length: {len(response.text)} bytes")
            
            # Try to parse as JSON
            try:
                data = json.loads(response.text)
                print(f"  ✓ Valid JSON")
                if isinstance(data, dict):
                    print(f"  Keys: {list(data.keys())[:10]}")
                elif isinstance(data, list):
                    print(f"  Array length: {len(data)}")
                    if data:
                        print(f"  First item keys: {list(data[0].keys()) if isinstance(data[0], dict) else 'Not a dict'}")
            except:
                print(f"  Not JSON")
                print(f"  Preview: {response.text[:200]}")
    except Exception as e:
        print(f"\n{endpoint}")
        print(f"  Error: {e}")

# Try to parse the Next.js data from the HTML
print("\n" + "="*80)
print("PARSING NEXT.JS DATA FROM HTML")
print("="*80)

url = "https://www.aruna.lk/categories/sports"
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)

from bs4 import BeautifulSoup
soup = BeautifulSoup(response.text, 'lxml')

next_data = soup.select_one('#__NEXT_DATA__')
if next_data:
    data = json.loads(next_data.string)
    print("Found __NEXT_DATA__")
    
    # Try to navigate to find article data
    build_id = data.get('buildId', 'unknown')
    print(f"Build ID: {build_id}")
    
    # Check if there's a patterns for data fetching
    if 'props' in data and 'pageProps' in data['props']:
        page_props = data['props']['pageProps']
        print(f"\npageProps keys: {list(page_props.keys())}")
        print(f"\nFull pageProps:")
        print(json.dumps(page_props, indent=2, ensure_ascii=False)[:1000])

print("\n⚠️  Aruna.lk appears to load articles dynamically via JavaScript.")
print("It requires browser automation (Selenium/Playwright) to scrape.")
print("Skipping Aruna.lk scraper for now.")
