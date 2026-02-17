"""
Test Mawrata News with proper headers
"""

import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

categories = ['exclusive', 'politics', 'sports']

base_url = "https://sinhala.mawratanews.lk"

for category in categories:
    url = f"{base_url}/{category}/"
    
    print(f"\n{'=' * 70}")
    print(f"Testing: {category}")
    print('=' * 70)
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            posts = soup.select('article')
            print(f"✓ Found {len(posts)} posts")
            
            # Check pagination
            nav = soup.select('.jeg_navigation, .jeg_page_navigation, .wp-pagenavi')
            if nav:
                print(f"✓ Found navigation: {nav[0].get('class')}")
                links = nav[0].select('a')
                print(f"  {len(links)} page links")
                if links:
                    for link in links[:3]:
                        print(f"  - {link.get_text(strip=True)}: {link.get('href')}")
            
            next_link = soup.select_one('a.page_nav.next, a[rel="next"]')
            if next_link:
                print(f"✓ Next page: {next_link.get('href')}")
        else:
            print(f"✗ Error: {response.status_code}")
            if response.status_code == 403:
                print("  Cloudflare or IP blocking detected")
            elif response.status_code == 526:
                print("  Invalid SSL certificate error")
                
    except Exception as e:
        print(f"✗ Exception: {e}")
