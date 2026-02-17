"""
Test Mawrata News pagination structure and categories
"""

import requests
from bs4 import BeautifulSoup
import time

# Test different categories
categories = [
    'exclusive',
    'politics', 
    'sports',
    'world',
    'entertainment'
]

base_url = "https://sinhala.mawratanews.lk"

for category in categories:
    url = f"{base_url}/{category}/"
    
    print(f"\n{'=' * 70}")
    print(f"Testing: {category}")
    print(f"URL: {url}")
    print('=' * 70)
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"✗ Failed with status {response.status_code}")
            continue
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Check for posts
        posts = soup.select('article.jeg_post, article[class*="jeg_"]')
        if not posts:
            posts = soup.select('article')
        print(f"Found {len(posts)} post containers")
        
        # Look for pagination
        next_link = soup.select_one('.next, .next-page, a[rel="next"], .jeg_navigation .next')
        if next_link:
            print(f"✓ Next page found: {next_link.get('href')}")
        else:
            # Check for any navigation
            nav = soup.select('.jeg_navigation, .pagination, [class*="paginat"]')
            if nav:
                print(f"Found {len(nav)} navigation elements")
                for n in nav[:2]:
                    print(f"  {n.get('class')}")
                    links = n.select('a')
                    print(f"  Contains {len(links)} links")
                    if links:
                        print(f"  First link: {links[0].get('href')}")
            else:
                print("No pagination found")
        
        time.sleep(1)  # Rate limiting
        
    except Exception as e:
        print(f"✗ Error: {e}")

# Also test page 2 of a working category
print(f"\n{'=' * 70}")
print("Testing exclusive category page 2")
print('=' * 70)

url = f"{base_url}/exclusive/page/2/"
try:
    response = requests.get(url, timeout=10)
    print(f"Status: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'lxml')
    posts = soup.select('article.jeg_post, article[class*="jeg_"]')
    print(f"Found {len(posts)} posts on page 2")
    
except Exception as e:
    print(f"✗ Error: {e}")
