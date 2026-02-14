"""Detailed investigation of each site"""
import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

print("="*70)
print("1. ADADERANA - Testing homepage")
print("="*70)
try:
    resp = requests.get('https://sinhala.adaderana.lk/', timeout=15, headers=headers)
    soup = BeautifulSoup(resp.content, 'lxml')
    
    # Find category links
    nav = soup.select('nav a') or soup.select('.main-menu a') or soup.select('header a')
    print(f"Found {len(nav)} navigation links")
    
    category_links = []
    for link in nav:
        href = link.get('href', '')
        text = link.get_text().strip()
        if '.php' in href or 'category' in href.lower():
            category_links.append((text[:30], href))
    
    print("\nCategory links:")
    for text, href in category_links[:8]:
        print(f"  {text:30s} | {href}")
        
    # Check for articles on homepage
    for selector in ['article', '.news-item', 'li.news-item', '.news-card', 'div[class*="article"]']:
        items = soup.select(selector)
        if items:
            print(f"\nHomepage articles: {selector} = {len(items)}")
            if items:
                first =items[0]
                print(f"  First item classes: {first.get('class')}")
                link = first.select_one('a')
                if link:
                    print(f"  Sample link: {link.get('href', '')[:80]}")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "="*70)
print("2. BBC SINHALA")
print("="*70)
try:
    resp = requests.get('https://www.bbc.com/sinhala', timeout=15, headers=headers)
    soup = BeautifulSoup(resp.content, 'lxml')
    
    for selector in ['article', '[data-testid="card"]', '.ssrcss-1f3bvyz', '.sc-8ea7699c-7', 'li[data-testid]']:
        items = soup.select(selector)
        if items and len(items) > 5:
            print(f"\nArticles: {selector} = {len(items)}")
            first = items[0]
            print(f"  Classes: {first.get('class')}")
            link = first.select_one('a')
            if link:
                href = link.get('href', '')
                print(f"  Link: {href[:80]}")
                # Try to get title
                title_elem = first.select_one('h2') or first.select_one('h3') or first.select_one('[data-testid="card-headline"]')
                if title_elem:
                    print(f"  Title: {title_elem.get_text()[:60]}")
            break
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "="*70)
print("3. DIVAINA")
print("="*70)
try:
    resp = requests.get('https://www.divaina.lk/category/main-news', timeout=15, headers=headers)
    soup = BeautifulSoup(resp.content, 'lxml')
    
    for selector in ['article', '.post', '.jeg_post', '.jeg_postblock', 'article.jeg_post']:
        items = soup.select(selector)
        if items and len(items) > 3:
            print(f"\nArticles: {selector} = {len(items)}")
            first = items[0]
            print(f"  Classes: {first.get('class')}")
            link = first.select_one('a')
            if link:
                print(f"  Link: {link.get('href', '')[:80]}")
            title = first.select_one('h3') or first.select_one('h2') or first.select_one('.jeg_post_title')
            if title:
                print(f"  Title: {title.get_text()[:60]}")
            break
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "="*70)
print("4. ADA.LK")
print("="*70)
try:
    resp = requests.get('https://www.ada.lk/latest-news/11', timeout=15, headers=headers)
    soup = BeautifulSoup(resp.content, 'lxml')
    
    for selector in ['article', '.post', '.news', 'div[class*="post"]', '.item']:
        items = soup.select(selector)
        if items and len(items) > 3:
            print(f"\nArticles: {selector} = {len(items)}")
            first = items[0]
            print(f"  Classes: {first.get('class')}")
            link = first.select_one('a')
            if link:
                print(f"  Link: {link.get('href', '')[:80]}")
            break
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "="*70)
print("5. GOSSIP LANKA")
print("="*70)
try:
    resp = requests.get('https://www.gossiplankanews.com/', timeout=15, headers=headers)
    soup = BeautifulSoup(resp.content, 'lxml')
    
    for selector in ['article', '.post', '.entry', 'div[class*="post"]']:
        items = soup.select(selector)
        if items and len(items) > 3:
            print(f"\nArticles: {selector} = {len(items)}")
            first = items[0]
            print(f"  Classes: {first.get('class')}")
            link = first.select_one('a')
            if link:
                print(f"  Link: {link.get('href', '')[:80]}")
            break
except Exception as e:
    print(f"ERROR: {e}")
