import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def test_feed_api():
    base_url = "https://www.gossiplanka.com"
    
    print("=== Testing Blogger Feed API ===\n")
    
    # Test JSON feed
    feed_urls = [
        f"{base_url}/feeds/posts/default?alt=json&max-results=25",
        f"{base_url}/feeds/posts/default/-/news?alt=json&max-results=25",  # With label
        f"{base_url}/feeds/posts/default?alt=json&orderby=published&max-results=25",
    ]
    
    for feed_url in feed_urls:
        print(f"\nTesting: {feed_url}")
        try:
            response = requests.get(feed_url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }, timeout=15)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse feed structure
                if 'feed' in data:
                    feed = data['feed']
                    
                    # Get entries
                    entries = feed.get('entry', [])
                    print(f"Entries found: {len(entries)}")
                    
                    if entries:
                        print("\nFirst entry structure:")
                        first = entries[0]
                        
                        # Title
                        if 'title' in first:
                            title = first['title'].get('$t', 'N/A')
                            print(f"  Title: {title[:80]}")
                        
                        # Link
                        if 'link' in first:
                            for link in first['link']:
                                if link.get('rel') == 'alternate':
                                    print(f"  URL: {link.get('href', 'N/A')}")
                                    break
                        
                        # Published date
                        if 'published' in first:
                            published = first['published'].get('$t', 'N/A')
                            print(f"  Published: {published}")
                        
                        # Updated date  
                        if 'updated' in first:
                            updated = first['updated'].get('$t', 'N/A')
                            print(f"  Updated: {updated}")
                        
                        # Categories/Labels
                        if 'category' in first:
                            categories = [cat.get('term', '') for cat in first['category']]
                            print(f"  Categories: {categories}")
                        
                        # Content
                        if 'content' in first:
                            content = first['content'].get('$t', '')
                            # Parse HTML content
                            content_soup = BeautifulSoup(content, 'lxml')
                            text = content_soup.get_text(strip=True)
                            print(f"  Content length: {len(text)} chars")
                            print(f"  Content preview: {text[:100]}...")
                    
                    # Check for next page link
                    if 'link' in feed:
                        for link in feed['link']:
                            if link.get('rel') == 'next':
                                print(f"\nNext page URL: {link.get('href', 'N/A')[:150]}")
                                break
                
        except Exception as e:
            print(f"Error: {e}")
    
    # Test pagination with updated-max
    print("\n\n=== Testing Pagination with updated-max ===")
    
    # First, get the initial page
    first_page = f"{base_url}/feeds/posts/default?alt=json&max-results=5"
    response = requests.get(first_page, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    if response.status_code == 200:
        data = response.json()
        entries = data['feed'].get('entry', [])
        
        if entries:
            # Get the published date of the last entry
            last_entry = entries[-1]
            last_published = last_entry.get('published', {}).get('$t', '')
            print(f"Last entry published: {last_published}")
            
            # Request next page
            if last_published:
                next_url = f"{base_url}/feeds/posts/default?alt=json&max-results=5&published-max={last_published}"
                print(f"\nRequesting next page: {next_url}")
                
                next_response = requests.get(next_url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                if next_response.status_code == 200:
                    next_data = next_response.json()
                    next_entries = next_data['feed'].get('entry', [])
                    print(f"Next page entries: {len(next_entries)}")
                    
                    if next_entries:
                        print(f"First entry on page 2: {next_entries[0]['title']['$t'][:80]}")

if __name__ == "__main__":
    test_feed_api()
