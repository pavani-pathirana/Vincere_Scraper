"""
Check AdaDerana actual structure
"""
import requests
from bs4 import BeautifulSoup
import re

# Try the main homepage first
urls_to_test = [
    "https://sinhala.adaderana.lk/",
    "https://sinhala.adaderana.lk/hot-news.php",
    "https://sinhala.adaderana.lk/sinhala-hot-news.php",
]

for url in urls_to_test:
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
            
            # Look for article links
            all_links = soup.select('a[href]')
            
            # Try different article URL patterns
            patterns = {
                'news.php?nid=': r'news\.php\?nid=\d+',
                'news-article.php': r'news-article\.php',
                'article/': r'article/\d+',
                '/\d{4}/\d{2}/': r'/\d{4}/\d{2}/',
            }
            
            for name, pattern in patterns.items():
                matches = [link.get('href', '') for link in all_links if re.search(pattern, link.get('href', ''))]
                matches = list(set(matches))  # Dedupe
                if matches:
                    print(f"\n✓ Pattern '{name}': {len(matches)} unique matches")
                    print(f"Sample URLs:")
                    for href in matches[:5]:
                        print(f"  {href}")
            
            # Look for Sinhala headlines
            sinhala_links = []
            for link in all_links:
                text = link.get_text(strip=True)
                href = link.get('href', '')
                if text and len(text) > 10 and any('\u0d80' <= char <= '\u0dff' for char in text):
                    if 'news' in href.lower() or 'nid=' in href:
                        sinhala_links.append((text[:60], href))
            
            if sinhala_links:
                print(f"\nSinhala article links found: {len(sinhala_links)}")
                for text, href in sinhala_links[:10]:
                    print(f"  {text}")
                    print(f"    -> {href}\n")
    
    except Exception as e:
        print(f"ERROR: {e}")
