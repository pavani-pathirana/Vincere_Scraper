import requests
from bs4 import BeautifulSoup

base_url = "https://www.gossiplankanews.com"

response = requests.get(base_url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'lxml')
    
    posts = soup.select('.blog-post')
    print(f"Total posts: {len(posts)}\n")
    
    print("=== Analyzing Post Structure ===\n")
    if posts:
        for i, post in enumerate(posts[:3], 1):
            print(f"Post {i}:")
            print(f"  Classes: {post.get('class')}")
            
            # Find title
            title_selectors = ['h2', 'h3', '.entry-title', '.post-title', 'h2 a', 'h3 a']
            for sel in title_selectors:
                title = post.select_one(sel)
                if title:
                    print(f"  Title (via {sel}): {title.get_text(strip=True)[:80]}")
                    break
            
            # Find link
            link = post.select_one('a[href*="/202"]')
            if link:
                print(f"  URL: {link.get('href')}")
            
            # Find content/summary
            summary = post.select_one('.entry-summary, .post-summary, p')
            if summary:
                print(f"  Summary: {summary.get_text(strip=True)[:100]}")
            
            print()
    
    # Test pagination
    print("=== Pagination Test ===\n")
    load_more = soup.select_one('.load-more[data-load], #load-more-link[data-load]')
    if load_more:
        next_url = load_more.get('data-load')
        print(f"Next page URL: {next_url}\n")
        
        # Test page 2
        print("Testing page 2...")
        page2_response = requests.get(next_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        if page2_response.status_code == 200:
            page2_soup = BeautifulSoup(page2_response.content, 'lxml')
            page2_posts = page2_soup.select('.blog-post')
            print(f"Posts on page 2: {len(page2_posts)}")
            
            if page2_posts:
                first_title = page2_posts[0].select_one('h2, h3')
                if first_title:
                    print(f"First post on page 2: {first_title.get_text(strip=True)[:80]}")
            
            # Check for next page
            page2_load_more = page2_soup.select_one('.load-more[data-load], #load-more-link[data-load]')
            if page2_load_more:
                print(f"Page 3 URL found: {page2_load_more.get('data-load')[:100]}")

# Test category page
print("\n\n=== Testing Category Page ===")
category_url = f"{base_url}/search/label/Cricket?&max-results=15"
cat_response = requests.get(category_url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

if cat_response.status_code == 200:
    cat_soup = BeautifulSoup(cat_response.content, 'lxml')
    cat_posts = cat_soup.select('.blog-post')
    print(f"Cricket category posts: {len(cat_posts)}")
    
    if cat_posts:
        for i, post in enumerate(cat_posts[:3], 1):
            title = post.select_one('h2, h3')
            if title:
                print(f"  {i}. {title.get_text(strip=True)[:80]}")
