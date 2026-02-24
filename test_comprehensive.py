"""Comprehensive test for both Dasatha and Aruna"""

import requests
from bs4 import BeautifulSoup
import json

def test_dasatha():
    print("="*80)
    print("DASATHALANKANEWS.COM - COMPREHENSIVE TEST")
    print("="*80)
    
    url = "https://dasathalankanews.com/local-news/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    
    response = requests.get(url, headers=headers, timeout=20)
    print(f"\nStatus: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    
    soup = BeautifulSoup(response.text, 'lxml')
    
    # Try WordPress article selectors
    selectors = [
        ('.td_module_wrap', 'tagDiv module'),
        ('.td-module-container', 'tagDiv container'),
        ('article', 'article tag'),
        ('.post', 'post class'),
        ('.td-block-row', 'tagDiv block row'),
    ]
    
    print("\nArticle Container Search:")
    for selector, name in selectors:
        elements = soup.select(selector)
        if elements:
            print(f"  ✓ {name} ({selector}): {len(elements)} found")
            
            # Show first article details
            first = elements[0]
            link = first.select_one('a[href*="dasathalankanews"]')
            if link:
                print(f"    First article URL: {link.get('href')[:80]}...")
                title = first.select_one('h3, .entry-title, .td-module-title')
                if title:
                    print(f"    Title: {title.get_text(strip=True)[:60]}...")
    
    # Test article page
    print("\n" + "="*80)
    print("TESTING ARTICLE PAGE")
    print("="*80)
    
    # Use the first article URL from detailed test
    article_url = "https://dasathalankanews.com/%e0%b7%80%e0%b7%92%e0%b7%82-%e0%b6%b8%e0%b6%ad%e0%b7%8a%e0%b6%af-%e0%b7%8a%e0%b6%bb%e0%b7%80%e0%b7%8a%e0%b6%ba-%e0%b6%b1%e0%b7%92%e0%b7%80%e0%b7%8f%e0%b6%bb%e0%b6%ab-%e0%b7%83/"
    
    article_resp = requests.get(article_url, headers=headers, timeout=20)
    article_soup = BeautifulSoup(article_resp.text, 'lxml')
    
    print(f"Article status: {article_resp.status_code}")
    
    title = article_soup.select_one('h1, .entry-title')
    print(f"Title: {title.get_text(strip=True) if title else 'NOT FOUND'}")
    
    content_selectors = [
        '.td-post-content',
        '.entry-content',
        '.post-content',
        '.content',
    ]
    
    for selector in content_selectors:
        elem = article_soup.select_one(selector)
        if elem:
            text = elem.get_text(strip=True)
            paras = elem.select('p')
            print(f"\nContent ({selector}):")
            print(f"  Length: {len(text)} chars")
            print(f"  Paragraphs: {len(paras)}")
            print(f"  Preview: {text[:150]}...")
            break

def test_aruna():
    print("\n" + "="*80)
    print("ARUNA.LK - COMPREHENSIVE TEST")
    print("="*80)
    
    url = "https://www.aruna.lk/categories/sports"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    
    response = requests.get(url, headers=headers, timeout=20)
    print(f"\nStatus: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Content length: {len(response.text)} bytes")
    
    # Check for Next.js/React markers
    if '__NEXT_DATA__' in response.text:
        print("\n⚠️  Site uses Next.js - content is client-side rendered")
        print("Looking for __NEXT_DATA__ JSON...")
        
        soup = BeautifulSoup(response.text, 'lxml')
        next_data = soup.select_one('#__NEXT_DATA__')
        
        if next_data:
            try:
                data = json.loads(next_data.string)
                print(f"Found Next.js data structure")
                
                # Navigate the data structure
                if 'props' in data:
                    props = data['props']
                    if 'pageProps' in props:
                        page_props = props['pageProps']
                        print(f"pageProps keys: {list(page_props.keys())[:10]}")
                        
                        # Look for article data
                        for key in page_props:
                            if 'article' in key.lower() or 'post' in key.lower() or 'news' in key.lower():
                                print(f"\nFound potential article data in key: {key}")
                                items = page_props[key]
                                if isinstance(items, list):
                                    print(f"  Contains {len(items)} items")
                                    if items:
                                        print(f"  First item keys: {list(items[0].keys()) if isinstance(items[0], dict) else 'Not a dict'}")
            except Exception as e:
                print(f"Error parsing Next.js data: {e}")
    else:
        print("\n✓ Standard HTML (not Next.js)")
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Look for any article/news content
        all_links = soup.find_all('a', href=True)
        print(f"Total links: {len(all_links)}")
        
        # Filter for article-like URLs
        article_patterns = ['/article/', '/news/', '/post/', '/story/']
        article_links = []
        
        for link in all_links:
            href = link.get('href', '')
            if any(pattern in href for pattern in article_patterns):
                article_links.append((link.get_text(strip=True)[:50], href))
        
        print(f"Article-like links: {len(article_links)}")
        for text, href in article_links[:5]:
            print(f"  {text}: {href}")

if __name__ == "__main__":
    test_dasatha()
    test_aruna()
