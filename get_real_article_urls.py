import requests
from bs4 import BeautifulSoup

# Get actual article URLs from homepage
base_url = "https://www.gossiplankanews.com"
response = requests.get(base_url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

print(f"Homepage Status: {response.status_code}\n")

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'lxml')
    
    # Get first 5 article URLs
    posts = soup.select('.blog-post')
    print(f"Found {len(posts)} posts\n")
    
    article_urls = []
    for i, post in enumerate(posts[:5], 1):
        link = post.select_one('a[href*="/202"]')
        if link:
            url = link.get('href')
            title = link.get_text(strip=True)
            article_urls.append(url)
            print(f"{i}. {title[:80]}")
            print(f"   URL: {url}")
    
    # Test first actual article
    if article_urls:
        print(f"\n\n{'='*80}")
        print("Testing First Article")
        print('='*80 + "\n")
        
        test_url = article_urls[0]
        article_response = requests.get(test_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        print(f"URL: {test_url}")
        print(f"Status: {article_response.status_code}\n")
        
        if article_response.status_code == 200:
            article_soup = BeautifulSoup(article_response.content, 'lxml')
            
            # Check post-body
            post_body = article_soup.select_one('.post-body')
            if post_body:
                print("✓ Found .post-body")
                
                # Get paragraphs
                paragraphs = post_body.select('p')
                print(f"  <p> tags: {len(paragraphs)}")
                
                # Get all text
                full_text = post_body.get_text(strip=True)
                print(f"  Full text length: {len(full_text)} chars")
                
                if paragraphs:
                    print(f"\n  Paragraph samples:")
                    for i, p in enumerate(paragraphs[:5], 1):
                        text = p.get_text(strip=True)
                        if len(text) > 30:  # Only show meaningful paragraphs
                            print(f"    {i}. ({len(text)} chars) {text[:100]}")
                
                # If no meaningful paragraphs but has text, show where it is
                if len(paragraphs) == 0 and len(full_text) > 100:
                    print("\n  No <p> tags but has text. Checking structure:")
                    print(f"  Children: {[child.name for child in post_body.children if hasattr(child, 'name')]}")
                    
                    # Try getting text from direct children
                    for child in post_body.children:
                        if hasattr(child, 'get_text'):
                            text = child.get_text(strip=True)
                            if len(text) > 50:
                                print(f"    {child.name}: {text[:150]}")
