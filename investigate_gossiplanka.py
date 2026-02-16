import requests
from bs4 import BeautifulSoup
import json

def investigate_gossiplanka():
    base_url = "https://www.gossiplanka.com"
    
    print("Investigating Gossip Lanka News structure...\n")
    
    # Test main page
    print("=== Testing Main Page ===")
    response = requests.get(base_url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Look for navigation/category links
        print("\n=== Looking for Categories ===")
        nav_links = soup.select('nav a, .menu a, #menu a')
        print(f"Found {len(nav_links)} navigation links")
        
        categories = {}
        for link in nav_links[:20]:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            if href and base_url in href and text and len(text) > 2:
                print(f"  {text}: {href}")
                categories[text] = href
        
        # Look for article containers
        print("\n=== Looking for Article Containers ===")
        possible_selectors = [
            'article',
            '.post',
            '.entry',
            '[class*="post"]',
            '[class*="item"]',
            '.news-item',
            '.article-item'
        ]
        
        for selector in possible_selectors:
            containers = soup.select(selector)
            if containers:
                print(f"\n'{selector}': Found {len(containers)} elements")
                if containers:
                    first = containers[0]
                    print(f"  Classes: {first.get('class', [])}")
                    
                    # Look for title/headline
                    title_selectors = ['h1', 'h2', 'h3', '.title', '.entry-title', 'a']
                    for ts in title_selectors:
                        title_elem = first.select_one(ts)
                        if title_elem:
                            print(f"  Title found with '{ts}': {title_elem.get_text(strip=True)[:80]}")
                            break
                    
                    # Look for link
                    link = first.select_one('a')
                    if link:
                        print(f"  Link: {link.get('href', 'N/A')}")
        
        # Test a category page if found
        if categories:
            print("\n=== Testing Category Page ===")
            first_cat = list(categories.values())[0]
            print(f"Testing: {first_cat}")
            
            cat_response = requests.get(first_cat, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            print(f"Status: {cat_response.status_code}")
            
            if cat_response.status_code == 200:
                cat_soup = BeautifulSoup(cat_response.content, 'lxml')
                
                # Count articles
                for selector in possible_selectors:
                    containers = cat_soup.select(selector)
                    if len(containers) > 5:  # Likely article containers
                        print(f"  '{selector}': {len(containers)} articles")
                        
                        # Get a few article links
                        print("\n  Sample articles:")
                        for container in containers[:5]:
                            link = container.select_one('a')
                            if link:
                                href = link.get('href', '')
                                title = link.get_text(strip=True)[:80]
                                print(f"    {title}")
                                print(f"      URL: {href}")
        
        # Test pagination
        print("\n=== Looking for Pagination ===")
        pagination_selectors = [
            '.pagination',
            '[class*="pag"]',
            '.nav-links',
            'a[rel="next"]',
            '.next',
            '[class*="next"]'
        ]
        
        for selector in pagination_selectors:
            pag_elems = soup.select(selector)
            if pag_elems:
                print(f"'{selector}': Found {len(pag_elems)} elements")
                for elem in pag_elems[:3]:
                    print(f"  {elem.name}: {elem.get('class', [])} - {elem.get_text(strip=True)[:50]}")
                    if elem.get('href'):
                        print(f"    href: {elem.get('href')}")
        
        # Test an article page
        print("\n=== Testing Article Page ===")
        # Try to find an article link
        article_links = soup.select('a[href*="/20"]')  # Common pattern for dated articles
        if not article_links:
            article_links = soup.select('article a, .post a')
        
        if article_links:
            test_url = article_links[0].get('href', '')
            if test_url and base_url in test_url:
                print(f"Testing: {test_url}")
                
                article_response = requests.get(test_url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                print(f"Status: {article_response.status_code}")
                
                if article_response.status_code == 200:
                    article_soup = BeautifulSoup(article_response.content, 'lxml')
                    
                    # Look for content containers
                    print("\n  Content selectors:")
                    content_selectors = [
                        '.entry-content',
                        '.post-content',
                        '.article-content',
                        '[class*="content"]',
                        'article .content',
                        '.post-body'
                    ]
                    
                    for selector in content_selectors:
                        content = article_soup.select_one(selector)
                        if content:
                            paragraphs = content.select('p')
                            text_length = len(content.get_text(strip=True))
                            print(f"    '{selector}': {len(paragraphs)} paragraphs, {text_length} chars")
                            if paragraphs:
                                print(f"      First para: {paragraphs[0].get_text(strip=True)[:100]}...")

if __name__ == "__main__":
    investigate_gossiplanka()
