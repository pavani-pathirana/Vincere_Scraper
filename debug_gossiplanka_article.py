import requests
from bs4 import BeautifulSoup

# Test a failing article URL
url = "https://www.gossiplankanews.com/2026/01/father-film-premiere.html"

response = requests.get(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

print(f"Status: {response.status_code}\n")

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'lxml')
    
    # Check different content selectors
    print("=== Testing Content Selectors ===\n")
    
    selectors = [
        '.post-body',
        '.post-content',
        'article .content',
        '.entry-content',
        '.article-content',
        '[class*="content"]'
    ]
    
    for selector in selectors:
        content = soup.select_one(selector)
        if content:
            print(f"✓ Found with '{selector}'")
            paragraphs = content.select('p')
            print(f"  Paragraphs: {len(paragraphs)}")
            
            # Check text length
            text = content.get_text(strip=True)
            print(f"  Text length: {len(text)} chars")
            
            # Show first paragraph
            if paragraphs:
                print(f"  First para: {paragraphs[0].get_text(strip=True)[:100]}")
            else:
                # Check for divs or other content
                print(f"  Text preview: {text[:200]}")
            print()
    
    # Check for image galleries (photo articles might be different)
    print("\n=== Checking for Image Content ===")
    images = soup.select('.post-body img, .entry-content img, article img')
    print(f"Images found: {len(images)}")
    
    # Check if this is a photo gallery post
    if 'photos' in url or 'photo' in url:
        print("\n⚠ This appears to be a photo gallery article")
        print("  Such articles might have minimal text content")
        
        # Look for image captions
        captions = soup.select('.caption, figcaption, .photo-caption')
        print(f"  Captions found: {len(captions)}")
        
        if captions:
            for i, cap in enumerate(captions[:3], 1):
                print(f"    {i}. {cap.get_text(strip=True)[:80]}")
    
    # Check the actual post-body structure
    print("\n=== Detailed Post Body Analysis ===")
    post_body = soup.select_one('.post-body')
    if post_body:
        print("Post body found!")
        
        # Check all direct children
        children = list(post_body.children)
        print(f"Direct children: {len(children)}")
        
        # Count different element types
        for child in children:
            if hasattr(child, 'name'):
                print(f"  {child.name}: {child.get('class', [])} - {str(child)[:100]}")
