import requests
from bs4 import BeautifulSoup
import time

base_url = 'https://www.divaina.lk'

print("="*70)
print("INVESTIGATING DIVAINA (Jegtheme-based site)")
print("="*70)

# Step 1: Check homepage for categories
print("\n1. Checking homepage for navigation...")
try:
    response = requests.get(base_url, timeout=10, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    print(f"Status: {response.status_code}")
    
    soup = BeautifulSoup(response.content, 'lxml')
    
    # Find navigation links
    nav_links = soup.select('nav a, .menu a, header a, .jeg_menu a')
    
    print(f"\nFound {len(nav_links)} navigation links")
    
    categories = {}
    for link in nav_links:
        href = link.get('href', '')
        text = link.get_text(strip=True)
        
        if base_url in href or href.startswith('/'):
            if any(keyword in href for keyword in ['category', 'cat', 'tag']):
                categories[text] = href
                print(f"  Category: {text[:50]} → {href}")
    
except Exception as e:
    print(f"Error: {e}")

time.sleep(2)

# Step 2: Test specific category URLs
print("\n2. Testing potential category URLs...")
test_slugs = ['local-news', 'politics', 'sports', 'world', 'business', 
              'sinhala', 'news', 'entertainment', 'opinion']

for slug in test_slugs:
    try:
        url = f"{base_url}/category/{slug}/"
        response = requests.get(url, timeout=5, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Look for Jegtheme specific selectors
            jeg_posts = soup.select('.jeg_post, article.jeg_post')
            regular_articles = soup.select('article')
            
            print(f"\n  ✓ {slug}:")
            print(f"    .jeg_post elements: {len(jeg_posts)}")
            print(f"    <article> elements: {len(regular_articles)}")
            
            # Check for article links
            links = soup.select('a[href*="/20"]')  # Year-based URLs
            print(f"    Article links found: {len(links)}")
            
            if jeg_posts:
                first_post = jeg_posts[0]
                print(f"    First post classes: {first_post.get('class')}")
                
                # Find headline
                headline = first_post.select_one('h3, h2, .jeg_post_title')
                if headline:
                    print(f"    Sample headline: {headline.get_text(strip=True)[:60]}")
                
                # Find link
                link = first_post.select_one('a')
                if link:
                    print(f"    Sample link: {link.get('href')}")
                    
        else:
            print(f"  ✗ {slug}: {response.status_code}")
            
    except Exception as e:
        print(f"  ✗ {slug}: Error - {str(e)[:50]}")
    
    time.sleep(1)

# Step 3: Test article page structure
print("\n3. Testing article page structure...")
try:
    # Try to find an article from homepage
    homepage_soup = BeautifulSoup(requests.get(base_url, timeout=10, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }).content, 'lxml')
    
    article_links = []
    for a in homepage_soup.select('a[href]'):
        href = a.get('href')
        if href and base_url in href and '/20' in href:  # Year in URL
            article_links.append(href)
    
    if article_links:
        test_url = article_links[0]
        print(f"\nTesting article: {test_url}")
        
        article_response = requests.get(test_url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        if article_response.status_code == 200:
            article_soup = BeautifulSoup(article_response.content, 'lxml')
            
            # Check various content selectors
            content_selectors = [
                '.jeg_post_content',
                '.content-inner',
                '.entry-content',
                'article .content',
                '.post-content',
                '[class*="content"]'
            ]
            
            print("\nContent selector analysis:")
            for selector in content_selectors:
                elements = article_soup.select(selector)
                if elements:
                    text = elements[0].get_text(strip=True)
                    print(f"  ✓ {selector}: Found {len(elements)} - Text length: {len(text)}")
                    if len(text) > 100:
                        print(f"    Preview: {text[:100]}...")
            
            # Check headline selectors
            headline_selectors = [
                'h1.jeg_post_title',
                'h1.entry-title',
                'h1',
                '.jeg_post_title'
            ]
            
            print("\nHeadline selector analysis:")
            for selector in headline_selectors:
                elements = article_soup.select(selector)
                if elements:
                    print(f"  ✓ {selector}: {elements[0].get_text(strip=True)[:80]}")
                    
except Exception as e:
    print(f"Error testing article: {e}")

print("\n" + "="*70)
print("INVESTIGATION COMPLETE")
print("="*70)
