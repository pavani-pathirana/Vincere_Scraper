"""
Test Ada.lk saaravita (entertainment) category
"""

import requests
from bs4 import BeautifulSoup

# Test Ada.lk entertainment category
url = "https://www.ada.lk/saaravita/8"

print(f"Testing Ada.lk Saaravita (Entertainment)")
print(f"URL: {url}")
print("=" * 70)

try:
    response = requests.get(url, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Check for articles
        articles = soup.select('article, .article, [class*="post"]')
        print(f"✓ Found {len(articles)} article containers")
        
        # Try to find some article links
        links = soup.select('a[href*="/news-details/"]')
        print(f"✓ Found {len(links)} article links")
        
        if links:
            print("\nSample articles:")
            for link in links[:5]:
                title = link.get_text(strip=True)
                href = link.get('href')
                print(f"  - {title[:60]}...")
                print(f"    {href}")
    else:
        print(f"✗ Error: Status {response.status_code}")
        
except Exception as e:
    print(f"✗ Error: {e}")
