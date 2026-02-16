"""Find Gagana's Load More API endpoint"""
import requests
from bs4 import BeautifulSoup
import json

# The "Load More" button likely calls an API endpoint
# Common patterns: /api/articles, /load-more, /fetch-articles, etc.

category = "politics"
base_url = "https://gagana.lk"

# Get the first page to see what articles exist
response = requests.get(f"{base_url}/news/{category}", timeout=15)
soup = BeautifulSoup(response.text, 'lxml')
page1_posts = soup.select('.a-item')
print(f"Page 1 has {len(page1_posts)} articles")

# Get the last article's timestamp (might be used for pagination)
last_article = page1_posts[-1] if page1_posts else None
if last_article:
    link = last_article.select_one('a[href*="/article/"]')
    if link:
        href = link.get('href')
        print(f"Last article URL: {href}")
        # Extract timestamp from URL (format: article/slug-TIMESTAMP)
        import re
        match = re.search(r'-(\d+)$', href)
        if match:
            timestamp = match.group(1)
            print(f"Last article timestamp: {timestamp}")

# Test common API endpoint patterns
test_endpoints = [
    f"{base_url}/load-more?category={category}&page=2",
    f"{base_url}/api/load-more?category={category}&page=2",
    f"{base_url}/api/articles?category={category}&page=2",
    f"{base_url}/api/news/{category}?page=2",
    f"{base_url}/news/{category}/load-more?page=2",
    f"{base_url}/fetch-articles?category={category}&page=2",
]

print("\n=== Testing API endpoints ===")
for endpoint in test_endpoints:
    try:
        response = requests.get(endpoint, timeout=10)
        print(f"\n{endpoint}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            print(f"Content-Type: {content_type}")
            
            if 'json' in content_type:
                try:
                    data = response.json()
                    print(f"JSON response keys: {list(data.keys())}")
                    print(f"✓ Found JSON API endpoint!")
                except:
                    print("Not valid JSON")
            else:
                # Check if HTML has articles
                soup = BeautifulSoup(response.text, 'lxml')
                posts = soup.select('.a-item')
                print(f"Posts found: {len(posts)}")
    except Exception as e:
        print(f"\n{endpoint}")
        print(f"Error: {type(e).__name__}")

# Check if there's a timestamp-based approach
if last_article and timestamp:
    print(f"\n=== Testing timestamp-based loading ===")
    test_timestamp_urls = [
        f"{base_url}/news/{category}?before={timestamp}",
        f"{base_url}/news/{category}?offset={timestamp}",
        f"{base_url}/news/{category}?after={timestamp}",
        f"{base_url}/api/articles?category={category}&before={timestamp}",
    ]
    
    for url in test_timestamp_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                posts = soup.select('.a-item')
                if len(posts) > 0:
                    first_link = posts[0].select_one('a[href*="/article/"]')
                    if first_link:
                        first_href = first_link.get('href')
                        print(f"\n{url}")
                        print(f"Status: 200, Posts: {len(posts)}")
                        print(f"First article: {first_href}")
                        # Check if it's different from our original last article
                        if first_href != href:
                            print(f"✓ Different articles! This might work!")
        except:
            pass
