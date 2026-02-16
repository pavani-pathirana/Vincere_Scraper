import requests
from bs4 import BeautifulSoup

def detailed_investigation():
    base_url = "https://www.gossiplanka.com"
    
    print("=== Detailed Gossip Lanka Investigation ===\n")
    
    response = requests.get(base_url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Find all links in the page
        print("=== All Menu/Header Links ===")
        header = soup.select('header a, .header a, nav a, .navbar a, #header a')
        if not header:
            # Try other common patterns
            all_links = soup.select('a[href]')
            # Filter for category-like links
            for link in all_links[:50]:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                parent_class = link.parent.get('class', []) if link.parent else []
                
                if ('category' in href or 'label' in href or 'search' in href) and text:
                    print(f"{text}: {href}")
                    print(f"  Parent classes: {parent_class}\n")
        
        # Look for posts more carefully
        print("\n=== Post Structure Analysis ===")
        posts = soup.select('.post')
        print(f"Found {len(posts)} posts\n")
        
        if posts:
            post = posts[0]
            print("First post structure:")
            print(f"  Classes: {post.get('class', [])}")
            
            # Find all child elements
            for child in post.find_all(recursive=False)[:10]:
                print(f"  > {child.name}: {child.get('class', [])} - {child.get_text(strip=True)[:50]}")
            
            # Find title
            title = post.select_one('h2, h3, .title, .entry-title')
            if title:
                print(f"\n  Title: {title.get_text(strip=True)}")
                title_link = title.select_one('a')
                if title_link:
                    print(f"  Title URL: {title_link.get('href')}")
            
            # Find image
            img = post.select_one('img')
            if img:
                print(f"  Image src: {img.get('src', 'N/A')[:80]}")
            
            # Find categories/labels
            labels = post.select('.post-labels a, [rel="tag"], .label a')
            if labels:
                print(f"\n  Labels/Categories found: {len(labels)}")
                for label in labels:
                    print(f"    {label.get_text(strip=True)}: {label.get('href')}")
        
        # Check for search/label pages
        print("\n\n=== Testing Label/Category Page ===")
        # Common Blogger platform patterns
        test_urls = [
            f"{base_url}/search/label/news",
            f"{base_url}/search/label/සිනමා",
            f"{base_url}/search/label/sports",
            f"{base_url}/search?updated-max=2025-07-01T00:00:00Z&max-results=20"
        ]
        
        for test_url in test_urls:
            print(f"\nTesting: {test_url}")
            try:
                resp = requests.get(test_url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }, timeout=10)
                print(f"  Status: {resp.status_code}")
                if resp.status_code == 200:
                    test_soup = BeautifulSoup(resp.content, 'lxml')
                    test_posts = test_soup.select('.post')
                    print(f"  Posts found: {len(test_posts)}")
            except Exception as e:
                print(f"  Error: {e}")
        
        # Check pagination patterns
        print("\n\n=== Pagination Investigation ===")
        # Look for older posts link
        older_link = soup.select_one('a.blog-pager-older-link')
        if older_link:
            print(f"Older posts link: {older_link.get('href')}")
        
        # Check for page numbers
        page_links = soup.select('.blog-pager a, .pagination a, a[href*="page"]')
        print(f"\nPage links found: {len(page_links)}")
        for link in page_links[:5]:
            print(f"  {link.get_text(strip=True)}: {link.get('href')}")

if __name__ == "__main__":
    detailed_investigation()
