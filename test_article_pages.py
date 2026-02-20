"""
Test individual article pages from tech sites
"""

import requests
from bs4 import BeautifulSoup
import time

# Sample article URLs (I'll get these from the list pages first)
test_articles = {
    'tecroom': 'https://tecroom.lk/',
    'androidwedakarayo': 'https://androidwedakarayo.com/',
    'aluthsl': 'https://aluthsl.com/category/tech-news',
    'techsayura': 'https://www.techsayura.com/',
}

def get_first_article_url(list_url, site_name):
    """Extract first article URL from a list page"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(list_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Different selectors for different sites
            if site_name == 'tecroom':
                article = soup.select_one('article')
                if article:
                    link = article.select_one('a[href*="/202"]')
                    return link.get('href') if link else None
            
            elif site_name == 'androidwedakarayo':
                article = soup.select_one('article')
                if article:
                    link = article.select_one('a')
                    href = link.get('href') if link else None
                    if href and not href.startswith('http'):
                        href = 'https://androidwedakarayo.com' + href
                    return href
            
            elif site_name == 'aluthsl':
                post = soup.select_one('.post')
                if post:
                    link = post.select_one('a[href*="aluthsl.com"]')
                    return link.get('href') if link else None
            
            elif site_name == 'techsayura':
                article = soup.select_one('article.blog-post')
                if article:
                    link = article.select_one('a')
                    return link.get('href') if link else None
    
    except Exception as e:
        print(f"Error getting article URL for {site_name}: {e}")
    
    return None

def analyze_article(name, url):
    """Analyze article page structure"""
    print(f"\n{'='*80}")
    print(f"Analyzing article: {name}")
    print(f"URL: {url}")
    print(f"{'='*80}")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Try common title selectors
            print("\nTitle:")
            title_selectors = [
                'h1.entry-title',
                'h1[class*="title"]',
                'h1',
                '.entry-title',
                '[class*="post-title"]'
            ]
            for sel in title_selectors:
                title = soup.select_one(sel)
                if title:
                    print(f"  Found in {sel}: {title.get_text()[:60]}...")
                    break
            
            # Try common content selectors
            print("\nContent containers:")
            content_selectors = [
                '.entry-content',
                '.post-content',
                '.article-content',
                '[class*="content"]',
                'article .content',
                '.post-body',
                '[itemprop="articleBody"]'
            ]
            for sel in content_selectors:
                content = soup.select_one(sel)
                if content:
                    paragraphs = content.select('p')
                    if paragraphs:
                        text = ' '.join([p.get_text() for p in paragraphs[:2]])
                        print(f"  {sel:30} → {len(paragraphs)} paragraphs")
                        print(f"    Sample: {text[:80]}...")
                        break
            
            # Check for date
            print("\nDate:")
            date_selectors = [
                'time',
                '.entry-date',
                '[class*="date"]',
                'span.published',
                '.post-date'
            ]
            for sel in date_selectors:
                date_elem = soup.select_one(sel)
                if date_elem:
                    print(f"  Found in {sel}: {date_elem.get_text()[:40]}")
                    break
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    time.sleep(2)

# Get and analyze articles
for name, list_url in test_articles.items():
    print(f"\nGetting article URL for {name}...")
    article_url = get_first_article_url(list_url, name)
    
    if article_url:
        print(f"Found: {article_url}")
        analyze_article(name, article_url)
    else:
        print(f"❌ Could not find article URL for {name}")

print(f"\n{'='*80}")
print("Article analysis complete!")
