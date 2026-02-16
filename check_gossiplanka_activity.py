import requests
from bs4 import BeautifulSoup
from datetime import datetime

url = "https://www.gossiplanka.com/"

response = requests.get(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'lxml')
    
    posts = soup.select('.post')
    print(f"Total posts on homepage: {len(posts)}\n")
    
    print("Article details:")
    print("=" * 80)
    for i, post in enumerate(posts, 1):
        title_elem = post.select_one('h2, h3, .title')
        title = title_elem.get_text(strip=True) if title_elem else 'N/A'
        
        link = post.select_one('a[href]')
        url = link.get('href') if link else 'N/A'
        
        # Try to find date
        date_elem = post.select_one('time, .published, .date, [class*="date"]')
        date_text = 'N/A'
        if date_elem:
            date_text = date_elem.get('datetime') or date_elem.get_text(strip=True)
        
        # Check URL for date  
        if '/202' in url:
            import re
            date_match = re.search(r'/(\d{4})/(\d{2})/', url)
            if date_match:
                date_text = f"{date_match.group(1)}-{date_match.group(2)}"
        
        print(f"\n{i}. {title[:80]}")
        print(f"   URL: {url}")
        print(f"   Date: {date_text}")
    
    print("\n" + "=" * 80)
    print(f"\nCurrent date: {datetime.now().strftime('%Y-%m-%d')}")
    
    # Check if site looks abandoned
    print("\n=== Site Activity Analysis ===")
    if '/2025/' in str(posts):
        print("✓ Site has content from 2025 - appears active")
    elif '/2024/' in str(posts):
        print("⚠ Latest content from 2024 - may be inactive")
    else:
        print("✗ Site appears abandoned (old content)")
    
    # Try to access an actual article to verify it exists
    if posts:
        first_link = posts[0].select_one('a[href]')
        if first_link:
            article_url = first_link.get('href')
            print(f"\nTesting article page: {article_url}")
            article_response = requests.get(article_url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }, timeout=10)
            print(f"Article page status: {article_response.status_code}")
            
            if article_response.status_code == 200:
                article_soup = BeautifulSoup(article_response.content, 'lxml')
                content = article_soup.select_one('.post-body, .post-content')
                if content:
                    text_length = len(content.get_text(strip=True))
                    print(f"Article content length: {text_length} characters")
                    if text_length > 100:
                        print("✓ Article has substantial content")
                    else:
                        print("⚠ Article content seems thin")
