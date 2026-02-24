"""Test script for analyzing subha.lk structure"""

import requests
from bs4 import BeautifulSoup

def test_subha():
    print("\n" + "="*80)
    print("Testing subha.lk")
    print("="*80)
    
    # Test blogs page
    url = "https://subha.lk/blogs?page=1"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"\nStatus: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Find page title
        title = soup.select_one('title')
        print(f"Page title: {title.get_text(strip=True) if title else 'N/A'}")
        
        # Look for blog/article containers
        selectors = [
            'article',
            '.blog',
            '.post',
            '.card',
            '.blog-item',
            '.blog-card',
            'a[href*="/blog/"]',
            'a[href*="/blogs/"]'
        ]
        
        print("\nTrying different selectors:")
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                print(f"  {selector}: {len(elements)} found")
        
        # Find all links
        all_links = soup.select('a[href]')
        blog_links = [link for link in all_links if '/blog' in link.get('href', '')]
        
        print(f"\nBlog-like links: {len(blog_links)}")
        
        print("\nFirst 5 blog links:")
        for i, link in enumerate(blog_links[:5], 1):
            print(f"  {i}. {link.get_text(strip=True)[:60]}")
            print(f"     URL: {link.get('href')}")
        
        # Look for pagination
        print("\nPagination:")
        page_links = soup.select('a[href*="page="]')
        for link in page_links[:5]:
            print(f"  {link.get_text(strip=True)}: {link.get('href')}")
        
        # Test page 2
        print("\n\nTesting page 2:")
        page2_url = "https://subha.lk/blogs?page=2"
        page2_response = requests.get(page2_url, timeout=10)
        print(f"Page 2 status: {page2_response.status_code}")
        page2_soup = BeautifulSoup(page2_response.text, 'lxml')
        page2_blogs = [link for link in page2_soup.select('a[href]') if '/blog' in link.get('href', '')]
        print(f"Page 2 blog links: {len(page2_blogs)}")
        
        # Test a blog page if available
        if blog_links:
            blog_url = blog_links[0].get('href')
            if not blog_url.startswith('http'):
                blog_url = f"https://subha.lk{blog_url}"
            
            print(f"\n\nTesting blog page: {blog_url}")
            print("="*80)
            
            blog_response = requests.get(blog_url, timeout=10)
            blog_soup = BeautifulSoup(blog_response.text, 'lxml')
            
            # Find title
            title = blog_soup.select_one('h1, .title, .blog-title')
            print(f"Title: {title.get_text(strip=True) if title else 'N/A'}")
            
            # Find content
            content_selectors = [
                '.blog-content',
                '.content',
                '.post-content',
                'article',
                '.entry-content'
            ]
            
            print("\nContent selectors:")
            for selector in content_selectors:
                elem = blog_soup.select_one(selector)
                if elem:
                    text = elem.get_text(strip=True)
                    print(f"  {selector}: {len(text)} chars")
                    print(f"    Preview: {text[:150]}...")
            
            # Find date
            date_elem = blog_soup.select_one('time, .date, .publish-date')
            print(f"\nDate: {date_elem.get_text(strip=True) if date_elem else 'N/A'}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_subha()
