"""Deep investigation of BBC and Divaina"""
import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

print("="*70)
print("BBC SINHALA")
print("="*70)

resp = requests.get('https://www.bbc.com/sinhala', timeout=15, headers=headers)
soup = BeautifulSoup(resp.content, 'lxml')

# Find main content
main = soup.select_one('main')
print(f"Main tag found: {main is not None}")

# BBC uses data attributes - look for those
cards = main.select('[data-testid*="card"]') if main else []
print(f"Data-testid cards: {len(cards)}")

# Also try promo patterns
promos = main.select('[class*="promo"]') if main else []
print(f"Promo elements: {len(promos)}")

# Try to find actual article links
if main:
    all_links = main.select('a[href]')
    article_links = [l for l in all_links if '/sinhala/articles/' in l.get('href', '')]
    print(f"Article links (/sinhala/articles/): {len(article_links)}")
    
    if article_links:
        first = article_links[0]
        print(f"\nFirst article link:")
        print(f"  URL: {first.get('href')}")
        # Find parent container
        parent = first.parent
        while parent and parent.name not in ['article', 'li', 'div'] or not parent.get('class'):
            parent = parent.parent
        if parent:
            print(f"  Parent: {parent.name}")
            print(f"  Parent classes: {parent.get('class', [])}")
            # Try to find title in parent
            for selector in ['h2', 'h3', '[data-testid*="headline"]']:
                title = parent.select_one(selector)
                if title:
                    print(f"  Title ({selector}): {title.get_text()[:60]}")
                    break

print("\n" + "="*70)
print("DIVAINA")
print("="*70)

resp = requests.get('https://www.divaina.lk/category/main-news', timeout=15, headers=headers)
soup = BeautifulSoup(resp.content, 'lxml')

# Divaina likely uses Jegtheme
jeg_posts = soup.select('.jeg_post')
print(f"jeg_post elements: {len(jeg_posts)}")

if jeg_posts:
    first = jeg_posts[0]
    print(f"\nFirst jeg_post:")
    print(f"  Classes: {first.get('class')}")
    link = first.select_one('a')
    if link:
        print(f"  Link: {link.get('href', '')[:80]}")
    title = first.select_one('h3') or first.select_one('.jeg_post_title')
    if title:
        print(f"  Title: {title.get_text()[:60]}")

# Try jeg_postblock
postblocks = soup.select('.jeg_postblock')
print(f"\njeg_postblock elements: {len(postblocks)}")

# Try article.jeg_post
article_posts = soup.select('article.jeg_post')
print(f"article.jeg_post elements: {len(article_posts)}")

if article_posts:
    first = article_posts[0]
    print(f"\nFirst article.jeg_post:")
    link = first.select_one('a')
    if link:
        print(f"  Link: {link.get('href', '')[:80]}")
    title = first.select_one('h3.jeg_post_title') or first.select_one('h3')
    if title:
        print(f"  Title: {title.get_text()[:60]}")

print("\n" + "="*70)
print("Testing Divaina article page")
print("="*70)

if article_posts and article_posts[0].select_one('a'):
    article_url = article_posts[0].select_one('a').get('href')
    print(f"URL: {article_url}")
    
    resp = requests.get(article_url, timeout=15, headers=headers)
    soup = BeautifulSoup(resp.content, 'lxml')
    
    # Try content selectors
    for selector in ['.entry-content', '.jeg_content', 'div[class*="content"]', '.article-content']:
        elem = soup.select_one(selector)
        if elem:
            text = elem.get_text().strip()
            if len(text) > 100:
                print(f"✓ Content: {selector} ({len(text)} chars)")
                break
