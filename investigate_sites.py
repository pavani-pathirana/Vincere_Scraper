"""Investigate structure of new Sinhala news sites"""
import requests
from bs4 import BeautifulSoup
import time

sites = [
    {
        'name': 'AdaDerana',
        'url': 'https://sinhala.adaderana.lk/',
        'category_test': 'https://sinhala.adaderana.lk/politics.php'
    },
    {
        'name': 'BBC Sinhala',
        'url': 'https://www.bbc.com/sinhala',
        'category_test': None
    },
    {
        'name': 'Divaina',
        'url': 'https://www.divaina.lk/',
        'category_test': None
    },
    {
        'name': 'Dinamina',
        'url': 'https://www.dinamina.lk/',
        'category_test': None
    },
    {
        'name': 'Silumina',
        'url': 'https://www.silumina.lk/',
        'category_test': None
    },
    {
        'name': 'Ada',
        'url': 'https://www.ada.lk/',
        'category_test': None
    },
    {
        'name': 'Gossip Lanka',
        'url': 'https://www.gossiplankanews.com/',
        'category_test': None
    }
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

for site in sites:
    print(f"\n{'='*70}")
    print(f"INVESTIGATING: {site['name']}")
    print(f"URL: {site['url']}")
    print('='*70)
    
    try:
        resp = requests.get(site['url'], timeout=15, headers=headers)
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, 'lxml')
            
            # Look for navigation/category links
            nav_links = soup.select('nav a') or soup.select('.menu a') or soup.select('#menu a')
            print(f"Navigation links: {len(nav_links)}")
            
            # Look for article containers
            article_selectors = ['article', '.post', '.news-item', '.article']
            for selector in article_selectors:
                articles = soup.select(selector)
                if articles:
                    print(f"  {selector}: {len(articles)} found")
            
            # Sample category links
            category_links = []
            for link in nav_links[:15]:
                href = link.get('href', '')
                text = link.get_text().strip()
                if href and text and len(text) > 2:
                    category_links.append((text[:40], href[:80]))
            
            if category_links:
                print("\nSample category links:")
                for text, href in category_links[:8]:
                    print(f"  {text:40s} | {href}")
        
        time.sleep(2)  # Rate limit
        
    except Exception as e:
        print(f"ERROR: {e}")

print(f"\n{'='*70}")
print("Investigation complete")
