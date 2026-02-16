import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

def test_pagination():
    base_url = "https://www.gossiplanka.com"
    
    print("=== Testing Gossip Lanka Pagination ===\n")
    
    # Test different pagination patterns on homepage
    test_urls = [
        (f"{base_url}/", "Homepage"),
        (f"{base_url}/?max-results=20", "Homepage with max-results=20"),
        (f"{base_url}/?start=5&max-results=5", "Homepage with start=5"),
        (f"{base_url}/search?max-results=20", "Search with max-results"),
    ]
    
    for url, desc in test_urls:
        print(f"\n{desc}:")
        print(f"URL: {url}")
        
        try:
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }, timeout=10)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'lxml')
                posts = soup.select('.post')
                print(f"Posts found: {len(posts)}")
                
                # Check for pagination links in the page source
                older_links = soup.select('a[href*="?"]')
                for link in older_links[:5]:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    if 'max-results' in href or 'start' in href or 'updated' in href:
                        print(f"  Found link: {text} -> {href[:100]}")
                
                # Look for actual older posts link (not javascript)
                blog_pager = soup.select('.blog-pager a[href]:not([href^="javascript"])')
                for link in blog_pager:
                    print(f"  Blog pager: {link.get_text(strip=True)} -> {link.get('href')[:100]}")
                
        except Exception as e:
            print(f"Error: {e}")
    
    # Test category pages with pagination
    print("\n\n=== Testing Category Pagination ===")
    category_tests = [
        f"{base_url}/search/label/news",
        f"{base_url}/search/label/news?max-results=20",
        f"{base_url}/search/label/සිනමා?max-results=10",
    ]
    
    for url in category_tests:
        print(f"\nURL: {url}")
        try:
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }, timeout=10)
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'lxml')
                posts = soup.select('.post')
                print(f"Posts: {len(posts)}")
                
                # Look for actual pagination in source (might be hidden in HTML)
                all_links = soup.find_all('a', href=True)
                for link in all_links:
                    href = link.get('href', '')
                    if 'updated-max' in href and 'label' in href:
                        print(f"  Found pagination link: {href[:150]}")
                        break
        except Exception as e:
            print(f"Error: {e}")
    
    # Try to find what the Load More button actually does
    print("\n\n=== Analyzing Page Source for AJAX URLs ===")
    response = requests.get(base_url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    if response.status_code == 200:
        # Search for API endpoints or feed URLs in the HTML
        content = response.text
        
        # Look for Blogger feed API
        if '/feeds/posts/default' in content:
            print("Found Blogger feed API reference")
            # Extract context
            start = content.find('/feeds/posts/default')
            print(content[max(0, start-50):start+150])
        
        # Check for data attributes
        soup = BeautifulSoup(response.content, 'lxml')
        load_more_btn = soup.select_one('.load-more, [class*="load"]')
        if load_more_btn:
            print(f"\nLoad more button attributes:")
            for attr, value in load_more_btn.attrs.items():
                print(f"  {attr}: {value}")

if __name__ == "__main__":
    test_pagination()
