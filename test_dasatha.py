"""Test script for analyzing dasathalankanews.com structure"""

import requests
from bs4 import BeautifulSoup

def test_dasatha():
    print("\n" + "="*80)
    print("Testing dasathalankanews.com")
    print("="*80)
    
    # Test local-news category
    url = "https://dasathalankanews.com/local-news/"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"\nStatus: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Find page title
        title = soup.select_one('title')
        print(f"Page title: {title.get_text(strip=True) if title else 'N/A'}")
        
        # Look for article containers
        article_containers = soup.select('article')
        print(f"\nArticle containers: {len(article_containers)}")
        
        # Try different selectors
        selectors = [
            '.post',
            '.entry',
            '.article',
            'article',
            '.post-item',
            '.news-item'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                print(f"  {selector}: {len(elements)} found")
        
        # Find article links
        print("\nArticle links (first 5):")
        for i, article in enumerate(article_containers[:5], 1):
            link = article.select_one('a')
            if link:
                title_elem = article.select_one('h2, h3, .entry-title, .post-title')
                title_text = title_elem.get_text(strip=True) if title_elem else link.get_text(strip=True)[:50]
                print(f"  {i}. {title_text}")
                print(f"     URL: {link.get('href')}")
        
        # Look for pagination
        print("\nPagination:")
        pagination_links = soup.select('a[href*="page"]')
        for link in pagination_links[:5]:
            print(f"  {link.get_text(strip=True)}: {link.get('href')}")
        
        # Test an article page
        if article_containers:
            first_link = article_containers[0].select_one('a')
            if first_link and first_link.get('href'):
                article_url = first_link.get('href')
                print(f"\n\nTesting article page: {article_url}")
                print("="*80)
                
                article_response = requests.get(article_url, timeout=10)
                article_soup = BeautifulSoup(article_response.text, 'lxml')
                
                # Find title
                title = article_soup.select_one('h1, .entry-title')
                print(f"Title: {title.get_text(strip=True) if title else 'N/A'}")
                
                # Find content
                content_selectors = [
                    '.entry-content',
                    '.post-content',
                    '.article-content',
                    'article .content',
                    '.single-content'
                ]
                
                print("\nContent selectors:")
                for selector in content_selectors:
                    elem = article_soup.select_one(selector)
                    if elem:
                        text = elem.get_text(strip=True)
                        print(f"  {selector}: {len(text)} chars")
                        print(f"    Preview: {text[:150]}...")
                
                # Find date
                date_elem = article_soup.select_one('time, .post-date, .entry-date')
                print(f"\nDate: {date_elem.get_text(strip=True) if date_elem else 'N/A'}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_dasatha()
