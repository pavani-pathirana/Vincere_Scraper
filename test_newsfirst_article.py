"""
Debug script to inspect NewsFirst article page structure
"""
import requests
from bs4 import BeautifulSoup

# Test URL - one of the failed articles
test_url = "https://www.newsfirst.lk/sinhala/2026/02/10/%e0%b6%a2%e0%b6%b1%e0%b6%b4%e0%b6%ad%e0%b7%92-%e0%b6%85%e0%b6%b1%e0%b7%94%e0%b6%bb-%e0%b6%b4%e0%b7%8f%e0%b6%9a%e0%b7%92%e0%b7%83%e0%b7%8a%e0%b6%ae%e0%b7%8f%e0%b6%b1"

print(f"Fetching URL: {test_url}\n")

try:
    response = requests.get(test_url, timeout=30, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    print(f"Status: {response.status_code}")
    print(f"Content-Length: {len(response.content)} bytes")
    print(f"Encoding: {response.encoding}\n")
    
    soup = BeautifulSoup(response.content, 'lxml')
    
    # Extract title
    print("=" * 70)
    print("TITLE")
    print("=" * 70)
    title = soup.select_one('title')
    if title:
        print(title.get_text())
    print()
    
    # Test headline selectors
    print("=" * 70)
    print("HEADLINE SELECTORS")
    print("=" * 70)
    headline_selectors = [
        'h1.entry-title',
        'h1.post-title',
        'h1.article-title',
        'article h1',
        '.article-header h1',
        'h1'
    ]
    
    for selector in headline_selectors:
        elem = soup.select_one(selector)
        if elem:
            print(f"✓ {selector}: {elem.get_text()[:80]}")
    print()
    
    # Test body selectors
    print("=" * 70)
    print("BODY SELECTORS")
    print("=" * 70)
    body_selectors = [
        'div.entry-content',
        'div.article-content',
        'div.post-content',
        'div.content-body',
        'article .content',
        '.single-post-content',
        '#article-body',
        'article',
        '.article-body',
        '.post-body'
    ]
    
    for selector in body_selectors:
        elem = soup.select_one(selector)
        if elem:
            text = elem.get_text(strip=True)
            print(f"✓ {selector}: {len(text)} chars, {len(elem.select('p'))} paragraphs")
            print(f"   First 150 chars: {text[:150]}...")
    print()
    
    # Analyze main content area
    print("=" * 70)
    print("MAIN CONTENT STRUCTURE")
    print("=" * 70)
    
    # Look for main article container
    article_tag = soup.select_one('article')
    if article_tag:
        print(f"<article> tag found")
        print(f"  Classes: {article_tag.get('class', [])}")
        print(f"  ID: {article_tag.get('id', 'none')}")
        print(f"  Direct child divs:")
        for div in article_tag.find_all('div', recursive=False):
            div_class = ' '.join(div.get('class', []))
            div_id = div.get('id', '')
            print(f"    <div class='{div_class}' id='{div_id}'> - {len(div.get_text(strip=True))} chars")
    
    # Look for paragraphs
    all_paragraphs = soup.select('p')
    print(f"\nTotal <p> tags: {len(all_paragraphs)}")
    if all_paragraphs:
        print(f"First paragraph: {all_paragraphs[0].get_text()[:150]}...")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
