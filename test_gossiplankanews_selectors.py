import requests
from bs4 import BeautifulSoup

base_url = "https://www.gossiplankanews.com"

response = requests.get(base_url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

print(f"Status: {response.status_code}\n")

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'lxml')
    
    # Try different selectors
    selectors = [
        'article',
        '.post',
        '.blog-post',
        '[class*="post"]',
        '.item-post',
        '.post-outer',
        '.news-item'
    ]
    
    print("=== Testing Post Selectors ===\n")
    for selector in selectors:
        posts = soup.select(selector)
        if posts:
            print(f"'{selector}': Found {len(posts)} elements")
            
            # Check first element
            first = posts[0]
            print(f"  First element tag: {first.name}")
            print(f"  Classes: {first.get('class', [])}")
            
            # Try to find title
            title = first.select_one('h1, h2, h3, .title, .post-title, a')
            if title:
                print(f"  Title: {title.get_text(strip=True)[:80]}")
            
            # Try to find link
            link = first.select_one('a[href]')
            if link:
                print(f"  Link: {link.get('href')[:100]}")
            
            print()
    
    # Check the actual HTML structure
    print("\n=== Checking HTML Structure ===")
    
    # Look for main content area
    main_content = soup.select('#main, .main, #content, .content, .main-wrapper')
    if main_content:
        print(f"Main content area found: {len(main_content)} elements")
        print(f"  Tag: {main_content[0].name}")
        print(f"  Classes: {main_content[0].get('class', [])}")
        
        # Look for children
        children = main_content[0].find_all(recursive=False)
        print(f"  Direct children: {len(children)}")
        for child in children[:5]:
            print(f"    - {child.name}: {child.get('class', [])}")
