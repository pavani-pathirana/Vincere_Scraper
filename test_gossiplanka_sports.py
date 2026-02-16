import requests
from bs4 import BeautifulSoup

url = "https://www.gossiplanka.com/search/label/sports"

response = requests.get(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

print(f"Status: {response.status_code}\n")

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'lxml')
    
    # Check posts
    posts = soup.select('.post')
    print(f"Posts found: {len(posts)}\n")
    
    # List first few post titles
    print("First 5 post titles:")
    for i, post in enumerate(posts[:5], 1):
        title = post.select_one('h2, h3, .title')
        if title:
            print(f"  {i}. {title.get_text(strip=True)[:80]}")
    print()
    
    # Check for load more button with all possible selectors
    print("=== Checking for pagination elements ===\n")
    
    # Check data-load attribute
    load_more_with_data = soup.select('.load-more[data-load], .blog-pager-older-link[data-load], #load-more-link[data-load]')
    print(f"Elements with data-load: {len(load_more_with_data)}")
    for elem in load_more_with_data:
        print(f"  Tag: {elem.name}")
        print(f"  Classes: {elem.get('class')}")
        print(f"  data-load: {elem.get('data-load')}")
        print(f"  href: {elem.get('href')}")
        print(f"  Text: {elem.get_text(strip=True)}")
        print()
    
    # Check for any load-more elements
    all_load_more = soup.select('.load-more, .blog-pager-older-link, #load-more-link')
    print(f"\nAll load-more elements: {len(all_load_more)}")
    for elem in all_load_more:
        print(f"  Tag: {elem.name}")
        print(f"  Classes: {elem.get('class')}")
        print(f"  data-load: {elem.get('data-load', 'N/A')}")
        print(f"  href: {elem.get('href', 'N/A')}")
        print(f"  Text: {elem.get_text(strip=True)[:50]}")
        print()
    
    # Check all blog-pager elements
    pagers = soup.select('.blog-pager')
    print(f"\nBlog pager elements: {len(pagers)}")
    for pager in pagers:
        print(f"  Classes: {pager.get('class')}")
        print(f"  Content:\n{pager.prettify()[:500]}")
        print()
    
    # Check for next/older links without javascript
    older_links = soup.select('a.blog-pager-older-link[href]:not([href^="javascript"])')
    print(f"\nNon-javascript older links: {len(older_links)}")
    for link in older_links:
        print(f"  href: {link.get('href')}")
        print(f"  Text: {link.get_text(strip=True)}")
        print()
