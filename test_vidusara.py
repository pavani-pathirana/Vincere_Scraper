"""
Test Vidusara.lk website structure
"""

import requests
from bs4 import BeautifulSoup

# Test Vidusara.lk homepage and categories
print("Testing Vidusara.lk")
print("=" * 70)

base_url = "https://www.vidusara.lk"

try:
    response = requests.get(base_url, timeout=10)
    print(f"Homepage Status: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        
        print("\n=== Finding Categories ===")
        # Look for navigation menu
        nav = soup.select('nav, .menu, .navigation, header')
        if nav:
            links = nav[0].select('a[href]')
            print(f"Found {len(links)} navigation links:")
            for link in links[:15]:
                text = link.get_text(strip=True)
                href = link.get('href')
                if text and href and href != '#':
                    print(f"  - {text}: {href}")
        
        print("\n=== Finding Articles ===")
        # Look for article containers
        articles = soup.select('article, .post, .entry, [class*="article"]')
        print(f"Found {len(articles)} article containers")
        
        # Look for article links
        article_links = soup.select('a[href*="/news/"], a[href*="/article/"], a[href*="202"]')
        print(f"Found {len(article_links)} article links")
        
        if article_links:
            print("\nSample article links:")
            for link in article_links[:5]:
                title = link.get_text(strip=True)
                href = link.get('href')
                if title:
                    print(f"  - {title[:60]}...")
                    print(f"    {href}")
        
        print("\n=== Checking Common Category URLs ===")
        test_categories = [
            '/news',
            '/category/news',
            '/local',
            '/world',
            '/sports',
            '/politics',
            '/business',
        ]
        
        for cat in test_categories:
            test_url = base_url + cat
            try:
                r = requests.head(test_url, timeout=5)
                if r.status_code == 200:
                    print(f"  ✓ {cat} - Status 200")
            except:
                pass
                
    else:
        print(f"✗ Error: Status {response.status_code}")
        
except Exception as e:
    print(f"✗ Error: {e}")
