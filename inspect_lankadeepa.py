"""
Inspect Lankadeepa website structure
"""
import requests
from bs4 import BeautifulSoup
import re

# Lankadeepa URLs to test
urls = [
    'https://www.lankadeepa.lk/',
    'https://www.lankadeepa.lk/latest_news',
    'https://www.lankadeepa.lk/local-news',
    'https://www.lankadeepa.lk/sports',
]

for url in urls:
    print("\n" + "=" * 70)
    print(f"Testing: {url}")
    print("=" * 70)
    
    try:
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
            all_links = soup.select('a[href]')
            
            print(f"Total links: {len(all_links)}")
            
            # Look for article patterns
            patterns = {
                'article/': r'/article/\d+',
                'news/': r'/news/\d+',
                '/\d{4}/\d{2}/': r'/\d{4}/\d{2}/\d{2}/',
                'path with numbers': r'/[a-z-]+/\d+',
            }
            
            for name, pattern in patterns.items():
                matches = [link.get('href', '') for link in all_links if re.search(pattern, link.get('href', ''))]
                matches = list(set(matches))
                if matches:
                    print(f"\n✓ Pattern '{name}': {len(matches)} unique matches")
                    print(f"  Samples:")
                    for href in matches[:5]:
                        print(f"    {href}")
            
            # Look for Sinhala content
            sinhala_links = []
            for link in all_links:
                text = link.get_text(strip=True)
                href = link.get('href', '')
                if text and len(text) > 15 and any('\u0d80' <= char <= '\u0dff' for char in text):
                    # Check if it looks like an article link
                    if href and ('article' in href or 'news' in href or re.search(r'/\d+', href)):
                        sinhala_links.append((text[:70], href))
            
            if sinhala_links:
                print(f"\nSinhala article links: {len(sinhala_links)}")
                for text, href in sinhala_links[:5]:
                    print(f"  {text}")
                    print(f"    -> {href}\n")
    
    except Exception as e:
        print(f"ERROR: {e}")

# Test an article page if we found any
print("\n" + "=" * 70)
print("TESTING ARTICLE PAGE STRUCTURE")
print("=" * 70)

article_url = "https://www.lankadeepa.lk/latest_news/item/3015-test"
print(f"Testing: {article_url}")

try:
    response = requests.get(article_url, timeout=30, headers={
        'User-Agent': 'Mozilla/5.0'
    })
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Look for article content
        content_selectors = [
            'article',
            '.article-content',
            '.news-content',
            '#content',
            '.content',
            'div[class*="article"]',
            'div[class*="content"]',
        ]
        
        print("\nArticle content containers:")
        for selector in content_selectors:
            elem = soup.select_one(selector)
            if elem:
                text_len = len(elem.get_text(strip=True))
                p_count = len(elem.select('p'))
                print(f"  ✓ {selector}: {text_len} chars, {p_count} paragraphs")
        
        # Look for headline
        headline_selectors = ['h1', 'h2', '.title', '.headline']
        print("\nHeadline:")
        for selector in headline_selectors:
            elem = soup.select_one(selector)
            if elem:
                print(f"  {selector}: {elem.get_text(strip=True)[:70]}")
                break

except Exception as e:
    print(f"ERROR: {e}")
