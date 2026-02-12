"""
Test if NewsFirst supports manual pagination URL construction
"""
import requests
from bs4 import BeautifulSoup

# Test different pagination URL patterns
test_patterns = [
    "https://www.newsfirst.lk/sinhala/sports/page/2/",
    "https://www.newsfirst.lk/sinhala/sports/?page=2",
    "https://www.newsfirst.lk/sinhala/sports/page/2",
]

for test_url in test_patterns:
    print(f"\nTesting: {test_url}")
    print("=" * 70)
    
    try:
        response = requests.get(test_url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Check if this is different from page 1
            # Look for article links with date patterns
            import re
            all_links = soup.find_all('a', href=True)
            date_pattern = re.compile(r'sinhala/\d{4}/\d{2}/\d{2}/')
            
            article_links = []
            for link in all_links:
                href = link.get('href', '')
                if date_pattern.search(href):
                    article_links.append(href)
            
            print(f"Found {len(set(article_links))} unique article links")
            
            if article_links:
                print("Sample articles:")
                for url in list(set(article_links))[:3]:
                    print(f"  - {url}")
        else:
            print(f"Failed with status {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "=" * 70)
print("TESTING API ENDPOINTS")
print("=" * 70)

# Check if there's an API we can use
api_patterns = [
    "https://www.newsfirst.lk/api/articles?category=sports&page=2",
    "https://www.newsfirst.lk/sinhala/api/posts?category=sports&page=2",
]

for api_url in api_patterns:
    print(f"\nTesting API: {api_url}")
    try:
        response = requests.get(api_url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json'
        })
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Content-Type: {response.headers.get('Content-Type')}")
            content = response.text[:500]
            print(f"Content preview: {content}...")
    except Exception as e:
        print(f"Error: {e}")
