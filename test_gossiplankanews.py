import requests
from bs4 import BeautifulSoup

base_url = "https://www.gossiplankanews.com"

print("=== Testing Gossip Lanka News (gossiplankanews.com) ===\n")

# Test homepage
response = requests.get(base_url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

print(f"Homepage Status: {response.status_code}\n")

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'lxml')
    
    # Check posts
    posts = soup.select('.post')
    print(f"Posts on homepage: {len(posts)}\n")
    
    if posts:
        print("Sample articles:")
        for i, post in enumerate(posts[:5], 1):
            title = post.select_one('h2, h3, .title, .post-title')
            if title:
                title_text = title.get_text(strip=True)
                link = post.select_one('a[href]')
                url = link.get('href') if link else 'N/A'
                print(f"  {i}. {title_text[:80]}")
                print(f"     URL: {url}")
        print()
    
    # Check for pagination
    print("=== Pagination Check ===")
    load_more = soup.select('.load-more[data-load], .blog-pager-older-link[data-load], #load-more-link[data-load]')
    if load_more:
        print(f"Load more button found: {len(load_more)}")
        for elem in load_more:
            print(f"  data-load: {elem.get('data-load')}")
    else:
        print("No load more button with data-load")
    
    # Check blog pager
    pagers = soup.select('.blog-pager')
    if pagers:
        print(f"\nBlog pager text: {pagers[0].get_text(strip=True)[:100]}")

# Test a category page
print("\n\n=== Testing Political Category ===")
category_url = f"{base_url}/search/label/Political?&max-results=15"
print(f"URL: {category_url}\n")

cat_response = requests.get(category_url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

print(f"Status: {cat_response.status_code}")

if cat_response.status_code == 200:
    cat_soup = BeautifulSoup(cat_response.content, 'lxml')
    cat_posts = cat_soup.select('.post')
    print(f"Posts in Political category: {len(cat_posts)}\n")
    
    if cat_posts:
        print("Sample articles:")
        for i, post in enumerate(cat_posts[:5], 1):
            title = post.select_one('h2, h3, .title, .post-title')
            if title:
                print(f"  {i}. {title.get_text(strip=True)[:80]}")
        print()
    
    # Check pagination
    cat_load_more = cat_soup.select('.load-more[data-load], .blog-pager-older-link[data-load], #load-more-link[data-load]')
    if cat_load_more:
        print(f"Pagination found: data-load = {cat_load_more[0].get('data-load')[:100]}")
    else:
        print("No pagination found")

# Test Cricket category
print("\n\n=== Testing Cricket Category ===")
cricket_url = f"{base_url}/search/label/Cricket?&max-results=15"
print(f"URL: {cricket_url}\n")

cricket_response = requests.get(cricket_url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

print(f"Status: {cricket_response.status_code}")

if cricket_response.status_code == 200:
    cricket_soup = BeautifulSoup(cricket_response.content, 'lxml')
    cricket_posts = cricket_soup.select('.post')
    print(f"Posts in Cricket category: {len(cricket_posts)}")
