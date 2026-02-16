import requests
from bs4 import BeautifulSoup

# Test homepage
url = "https://www.gossiplanka.com/"

response = requests.get(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

print(f"Homepage Status: {response.status_code}\n")

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'lxml')
    
    # Check posts
    posts = soup.select('.post')
    print(f"Posts on homepage: {len(posts)}\n")
    
    # List first few post titles
    print("Sample post titles:")
    for i, post in enumerate(posts[:10], 1):
        title = post.select_one('h2, h3, .title')
        if title:
            title_text = title.get_text(strip=True)
            link = post.select_one('a[href]')
            url = link.get('href') if link else 'N/A'
            print(f"  {i}. {title_text[:80]}")
            if url != 'N/A':
                print(f"     URL: {url}")
    print()
    
    # Check for load more button
    load_more_with_data = soup.select('.load-more[data-load], .blog-pager-older-link[data-load], #load-more-link[data-load]')
    print(f"Elements with data-load on homepage: {len(load_more_with_data)}")
    for elem in load_more_with_data:
        print(f"  data-load: {elem.get('data-load')}")
        print(f"  Text: {elem.get_text(strip=True)}")
        print()
    
    # Check all pagination
    pagers = soup.select('.blog-pager')
    print(f"Blog pager elements: {len(pagers)}")
    for pager in pagers:
        print(f"  Content: {pager.get_text(strip=True)[:100]}")
        # Check for links inside
        links = pager.select('a[href]')
        for link in links:
            print(f"    Link: {link.get('href')[:100]}")
            print(f"    Text: {link.get_text(strip=True)}")
        print()
    
    # Check if site might be using infinite scroll
    print("\n=== Checking for AJAX/API endpoints ===")
    scripts = soup.select('script')
    for script in scripts:
        content = script.string
        if content and ('feed' in content.lower() or 'posts' in content.lower() or 'ajax' in content.lower()):
            print(f"Found relevant script (first 200 chars):")
            print(content[:200])
            print()
