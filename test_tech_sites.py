"""
Test script to analyze structure of tech news websites
"""

import requests
from bs4 import BeautifulSoup
import time

sites = {
    'pcguide': 'https://www.pcguide.lk/category/tech-news/',
    'techcyclone': 'https://thetechcyclone.com/',
    'tecroom': 'https://tecroom.lk/',
    'androidwedakarayo': 'https://androidwedakarayo.com/',
    'aluthsl': 'https://aluthsl.com/category/tech-news',
    'techsayura': 'https://www.techsayura.com/'
}

def analyze_site(name, url):
    """Analyze a site's structure"""
    print(f"\n{'='*80}")
    print(f"Analyzing: {name}")
    print(f"URL: {url}")
    print(f"{'='*80}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Check for common article containers
            print("\nChecking for article containers:")
            selectors = [
                'article',
                '.post',
                '[class*="post"]',
                '.article',
                '[class*="article"]',
                '.entry',
                '[class*="entry"]'
            ]
            
            for selector in selectors:
                items = soup.select(selector)
                if items:
                    print(f"  {selector:30} → {len(items)} items")
                    if len(items) > 0:
                        # Show first item structure
                        first_item = items[0]
                        print(f"    First item classes: {first_item.get('class', [])}")
                        
                        # Check for title
                        title_selectors = ['h1', 'h2', 'h3', '.title', '[class*="title"]']
                        for ts in title_selectors:
                            title = first_item.select_one(ts)
                            if title:
                                print(f"    Title found in: {ts} → {title.get_text()[:60]}...")
                                break
                        
                        # Check for link
                        link = first_item.select_one('a')
                        if link:
                            print(f"    Link: {link.get('href', '')[:80]}")
            
            # Check for pagination
            print("\nChecking for pagination:")
            pagination_selectors = [
                '.pagination',
                '.nav-links',
                '[class*="pag"]',
                '.next',
                'a[rel="next"]'
            ]
            
            for selector in pagination_selectors:
                items = soup.select(selector)
                if items:
                    print(f"  {selector:30} → Found!")
                    if selector == 'a[rel="next"]' and items:
                        print(f"    Next URL: {items[0].get('href', '')}")
            
            # Detect platform
            print("\nPlatform detection:")
            if 'wp-content' in response.text or 'WordPress' in response.text:
                print("  ✓ WordPress detected")
            if 'jnews' in response.text.lower():
                print("  ✓ JNews theme detected")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    time.sleep(2)  # Be polite

# Analyze all sites
for name, url in sites.items():
    analyze_site(name, url)

print(f"\n{'='*80}")
print("Analysis complete!")
print(f"{'='*80}")
