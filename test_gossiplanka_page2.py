import requests
from bs4 import BeautifulSoup

# Test the data-load URL from homepage
url = "https://www.gossiplanka.com/search?updated-max=2025-05-17T11:03:00%2B05:30&max-results=25"

response = requests.get(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

print(f"Status: {response.status_code}\n")

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'lxml')
    
    # Check posts
    posts = soup.select('.post')
    print(f"Posts on page 2: {len(posts)}\n")
    
    if posts:
        print("Sample titles from page 2:")
        for i, post in enumerate(posts[:5], 1):
            title = post.select_one('h2, h3, .title')
            if title:
                print(f"  {i}. {title.get_text(strip=True)[:80]}")
        print()
    
    # Check for next page
    load_more_with_data = soup.select('.load-more[data-load], .blog-pager-older-link[data-load], #load-more-link[data-load]')
    print(f"Next pagination found: {len(load_more_with_data)}")
    for elem in load_more_with_data:
        print(f"  data-load: {elem.get('data-load')}")
        print()
    
    # Check blog pager
    pagers = soup.select('.blog-pager')
    if pagers:
        print(f"Blog pager text: {pagers[0].get_text(strip=True)}")
