import requests
from bs4 import BeautifulSoup
import time

base_url = 'https://www.dinamina.lk'

print("="*70)
print("INVESTIGATING DINAMINA (403 Forbidden Issue)")
print("="*70)

# Test various User-Agent and header combinations
test_configs = [
    {
        'name': 'Default (No headers)',
        'headers': {}
    },
    {
        'name': 'Chrome Windows',
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    },
    {
        'name': 'Chrome Windows + Accept',
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    },
    {
        'name': 'Firefox Windows',
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0'
        }
    },
    {
        'name': 'Chrome Windows + Referer',
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.google.com/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
    }
]

successful_config = None

for config in test_configs:
    print(f"\n{config['name']}:")
    try:
        response = requests.get(base_url, timeout=10, headers=config['headers'])
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"  ✓ SUCCESS! Content length: {len(response.content)} bytes")
            successful_config = config
            
            soup = BeautifulSoup(response.content, 'lxml')
            articles = soup.select('article')
            print(f"  Articles found: {len(articles)}")
            
            # Find navigation
            nav_links = soup.select('nav a, .menu a, header a')
            categories = [a.get_text(strip=True) for a in nav_links if a.get_text(strip=True)]
            print(f"  Navigation items: {len(categories)}")
            if categories:
                print(f"  Sample categories: {', '.join(categories[:5])}")
            
            break
        else:
            print(f"  ✗ Failed with status {response.status_code}")
            
    except Exception as e:
        print(f"  ✗ Error: {str(e)[:60]}")
    
    time.sleep(1)

if successful_config:
    print("\n" + "="*70)
    print("SUCCESS! Testing category pages...")
    print("="*70)
    
    # Test category URLs
    test_categories = [
        '/category/local/',
        '/category/world/',
        '/category/sports/',
        '/category/business/',
        '/category/entertainment/',
        '/sinhala/',
        '/sinhala/local/',
        '/sinhala/world/'
    ]
    
    for cat in test_categories:
        try:
            url = base_url + cat
            response = requests.get(url, timeout=10, headers=successful_config['headers'])
            print(f"\n{cat}:")
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'lxml')
                articles = soup.select('article')
                links = soup.select('a[href*="/20"]')
                
                print(f"  ✓ Articles: {len(articles)}")
                print(f"  ✓ Article links: {len(links)}")
                
                if links:
                    print(f"  Sample link: {links[0].get('href')}")
                    
        except Exception as e:
            print(f"  ✗ Error: {str(e)[:50]}")
        
        time.sleep(1)
    
    # Test article page
    print("\n" + "="*70)
    print("Testing article page structure...")
    print("="*70)
    
    try:
        homepage = requests.get(base_url, timeout=10, headers=successful_config['headers'])
        soup = BeautifulSoup(homepage.content, 'lxml')
        
        article_links = [a.get('href') for a in soup.select('a[href]') 
                        if a.get('href') and '/20' in a.get('href')]
        
        if article_links:
            test_url = article_links[0] if article_links[0].startswith('http') else base_url + article_links[0]
            print(f"\nTesting: {test_url}")
            
            article_response = requests.get(test_url, timeout=10, headers=successful_config['headers'])
            article_soup = BeautifulSoup(article_response.content, 'lxml')
            
            # Test content selectors
            content_selectors = [
                '.entry-content',
                '.post-content',
                'article .content',
                '.article-content',
                '[class*="content"]'
            ]
            
            for selector in content_selectors:
                elements = article_soup.select(selector)
                if elements:
                    text = elements[0].get_text(strip=True)
                    print(f"  ✓ {selector}: {len(text)} chars")
                    if len(text) > 100:
                        print(f"    Preview: {text[:100]}...")
                        
    except Exception as e:
        print(f"Error: {e}")
        
else:
    print("\n" + "="*70)
    print("FAILED: All header configurations returned 403")
    print("May require:")
    print("  - Session management with cookies")
    print("  - JavaScript rendering (Selenium/Playwright)")
    print("  - Proxy/VPN")
    print("="*70)
