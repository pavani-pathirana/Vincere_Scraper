"""Test script for analyzing aruna.lk structure"""

import requests
from bs4 import BeautifulSoup

def test_aruna():
    print("\n" + "="*80)
    print("Testing aruna.lk")
    print("="*80)
    
    # Test sports category
    url = "https://www.aruna.lk/categories/sports"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"\nStatus: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Find page title
        title = soup.select_one('title')
        print(f"Page title: {title.get_text(strip=True) if title else 'N/A'}")
        
        # Look for article containers
        selectors = [
            'article',
            '.post',
            '.news-item',
            '.article-item',
            '.card',
            'a[href*="/article/"]',
            'a[href*="/news/"]'
        ]
        
        print("\nTrying different selectors:")
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                print(f"  {selector}: {len(elements)} found")
        
        # Find all links
        all_links = soup.select('a[href]')
        article_links = [link for link in all_links if '/article/' in link.get('href', '') or '/news/' in link.get('href', '')]
        
        print(f"\nArticle-like links: {len(article_links)}")
        
        print("\nFirst 5 article links:")
        for i, link in enumerate(article_links[:5], 1):
            print(f"  {i}. {link.get_text(strip=True)[:60]}")
            print(f"     URL: {link.get('href')}")
        
        # Look for pagination
        print("\nPagination links:")
        page_links = soup.select('a[href*="page"], a[href*="Page"]')
        for link in page_links[:5]:
            print(f"  {link.get_text(strip=True)}: {link.get('href')}")
        
        # Test an article page if available
        if article_links:
            article_url = article_links[0].get('href')
            if not article_url.startswith('http'):
                article_url = f"https://www.aruna.lk{article_url}"
            
            print(f"\n\nTesting article page: {article_url}")
            print("="*80)
            
            article_response = requests.get(article_url, timeout=10)
            article_soup = BeautifulSoup(article_response.text, 'lxml')
            
            # Find title
            title = article_soup.select_one('h1, .title, .article-title')
            print(f"Title: {title.get_text(strip=True) if title else 'N/A'}")
            
            # Find content
            content_selectors = [
                '.article-content',
                '.content',
                '.post-content',
                'article .body',
                '.entry-content'
            ]
            
            print("\nContent selectors:")
            for selector in content_selectors:
                elem = article_soup.select_one(selector)
                if elem:
                    text = elem.get_text(strip=True)
                    print(f"  {selector}: {len(text)} chars")
                    print(f"    Preview: {text[:150]}...")
            
            # Find date
            date_elem = article_soup.select_one('time, .date, .publish-date')
            print(f"\nDate: {date_elem.get_text(strip=True) if date_elem else 'N/A'}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_aruna()
