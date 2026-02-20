"""
Test Asian Mirror with correct category URLs from menu
"""

import requests
from bs4 import BeautifulSoup

categories = {
    'local': 'https://sinhala.asianmirror.lk/news/local/',
    'political': 'https://sinhala.asianmirror.lk/news/political/',
    'international': 'https://sinhala.asianmirror.lk/news/international/',
    'sports': 'https://sinhala.asianmirror.lk/news/sports/',
    'business': 'https://sinhala.asianmirror.lk/news/business/',
    'crime': 'https://sinhala.asianmirror.lk/news/crime/',
}

print("Testing Asian Mirror category pages with correct URLs\n")

for cat_name, url in categories.items():
    print(f"\n{'='*70}")
    print(f"Category: {cat_name} - {url}")
    print('='*70)
    
    try:
        r = requests.get(url, timeout=10)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, 'lxml')
        
        # Try various selectors
        selectors = [
            'article a',
            'article h2 a',
            'article h3 a',
            '.post a',
            '.entry-title a',
            'h2.entry-title a',
            'h3.entry-title a',
            '.post-title a',
            '[class*="post"] a[href*="/news/"]',
            'a[href*="/news/"][href*="-"]',  # URLs with dashes (typical article URLs)
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            
            # Filter to only article URLs
            article_links = []
            for link in links:
                href = link.get('href', '')
                if href and '/news/' in href and href.count('/') > 4:  # Has category and slug
                    article_links.append(link)
            
            if article_links:
                print(f"\n✓ Selector '{selector}' found {len(article_links)} article links")
                print("Sample articles:")
                for i, link in enumerate(article_links[:3], 1):
                    title = link.get_text(strip=True)
                    url = link.get('href')
                    print(f"  {i}. {title[:60]}...")
                    print(f"     URL: {url}")
                break
        else:
            print("✗ No article links found with any selector")
            
            # Debug: show page structure
            print("\nPage structure:")
            articles = soup.select('article')
            print(f"  Articles: {len(articles)}")
            posts = soup.select('[class*="post"]')
            print(f"  Posts: {len(posts)}")
            
            # Show all links
            all_links = soup.select('a[href]')
            print(f"  Total links: {len(all_links)}")
            
            # Show sample link HREFs
            print("\n  Sample link hrefs:")
            for link in all_links[:10]:
                href = link.get('href', '')
                text = link.get_text(strip=True)[:40]
                print(f"    - {href} ({text})")
            
    except Exception as e:
        print(f"✗ Error: {e}")

print("\n" + "="*70)
print("Test complete")
