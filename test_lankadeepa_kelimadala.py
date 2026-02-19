"""
Test Lankadeepa kelimadala (sports) category
"""

import requests
from bs4 import BeautifulSoup

# Test Lankadeepa sports category
urls = [
    "https://www.lankadeepa.lk/sports/3/",
    "https://www.lankadeepa.lk/kelimadala/",
    "https://www.lankadeepa.lk/kelimadala/3/",
]

for url in urls:
    print(f"\nTesting: {url}")
    print("=" * 70)
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Check for articles
            articles = soup.select('article, .article, [class*="post"]')
            print(f"✓ Found {len(articles)} article containers")
            
            # Try to find article links
            links = soup.select('a[href]')
            news_links = [l for l in links if '/news/' in l.get('href', '')]
            print(f"✓ Found {len(news_links)} news links")
            
            if news_links:
                print("\nSample articles:")
                for link in news_links[:3]:
                    title = link.get_text(strip=True)
                    href = link.get('href')
                    if title:
                        print(f"  - {title[:50]}...")
        else:
            print(f"✗ Status {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
