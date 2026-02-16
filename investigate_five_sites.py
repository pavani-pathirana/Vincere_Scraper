import requests
from bs4 import BeautifulSoup

sites = [
    ("Gagana", "https://gagana.lk/"),
    ("Mawrata News", "https://sinhala.mawratanews.lk/"),
    ("Lankapuvath", "https://sinhala.lankapuvath.lk/"),
    ("Sarasaviya", "https://sarasaviya.lk/"),
    ("Lanka C News", "https://www.lankacnews.com/")
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

for name, url in sites:
    print(f"\n{'='*80}")
    print(f"Testing: {name} ({url})")
    print('='*80)
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Test common post selectors
            post_selectors = [
                '.post',
                'article',
                '.blog-post',
                '.news-item',
                '[class*="post"]',
                '.item',
                '.entry'
            ]
            
            posts_found = False
            for selector in post_selectors:
                posts = soup.select(selector)
                if len(posts) >= 3:
                    print(f"  Posts found with '{selector}': {len(posts)}")
                    
                    # Get first post details
                    first = posts[0]
                    title = first.select_one('h1, h2, h3, .title, a')
                    if title:
                        print(f"    Sample title: {title.get_text(strip=True)[:80]}")
                    
                    link = first.select_one('a[href]')
                    if link:
                        print(f"    Sample URL: {link.get('href')[:100]}")
                    
                    posts_found = True
                    break
            
            if not posts_found:
                print("  No posts found with common selectors")
            
            # Check for navigation/categories
            nav_links = soup.select('nav a, .menu a, #menu a, .navbar a')
            if nav_links:
                print(f"\n  Navigation links found: {len(nav_links)}")
                for link in nav_links[:5]:
                    text = link.get_text(strip=True)
                    href = link.get('href', '')
                    if text and len(text) > 2 and 'categor' in href.lower() or 'news' in text.lower():
                        print(f"    {text}: {href[:50]}")
            
            # Check pagination
            pag_selectors = ['.pagination', '[class*="pag"]', '.next', 'a[rel="next"]']
            for sel in pag_selectors:
                pag = soup.select(sel)
                if pag:
                    print(f"\n  Pagination found with '{sel}': {len(pag)} elements")
                    break
        
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "="*80)
print("Investigation complete")
