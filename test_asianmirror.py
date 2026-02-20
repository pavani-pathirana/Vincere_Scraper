"""Deep dive into Asian Mirror"""

import requests
from bs4 import BeautifulSoup

url = "https://sinhala.asianmirror.lk/news/local/"
print(f"Testing: {url}\n")

r = requests.get(url)
soup = BeautifulSoup(r.text, 'lxml')

# Check main content area
print("Looking for main content area...")
main = soup.select_one('main, #main, .main-content, #content')
if main:
    print(f"Found main area: {main.name} {main.get('class')} {main.get('id')}")
    
    # Look for article containers within main
    articles = main.select('article, .post, [class*="post-item"]')
    print(f"Articles in main: {len(articles)}")
    
    if articles:
        print("\nFirst article structure:")
        first = articles[0]
        print(f"Tag: {first.name}")
        print(f"Classes: {first.get('class')}")
        
        # Find link
        link = first.select_one('a')
        if link:
            print(f"Link text: {link.get_text(strip=True)[:60]}")
            print(f"Link href: {link.get('href')}")
        
        # Find all links in first article
        all_links = first.select('a')
        print(f"\nAll links in first article: {len(all_links)}")
        for i, a in enumerate(all_links[:3], 1):
            text = a.get_text(strip=True)
            href = a.get('href')
            if text and href and 'news' in href:
                print(f"  {i}. {text[:60]}")
                print(f"     → {href}")

# Also try direct h2/h3 search in main content
print("\n" + "="*60)
print("Direct h2/h3 search:")
print("="*60)

for selector in ['main h2 a', 'main h3 a', '#main h2 a', '#content h2 a']:
    links = soup.select(selector)
    if len(links) > 5:
        print(f"\n✓ {selector}: {len(links)} links")
        for i, link in enumerate(links[:3], 1):
            text = link.get_text(strip=True)
            href = link.get('href', '')
            if text and href:
                print(f"  {i}. {text[:60]}")
                print(f"     → {href}")
        break

# Test an article page
print("\n" + "="*60)
print("Testing article page:")
print("="*60)

# Get first article URL from page
potential_links = soup.select('a[href*="/news/local/"]')
if potential_links:
    article_url = potential_links[0].get('href')
    if not article_url.startswith('http'):
        article_url = f"https://sinhala.asianmirror.lk{article_url}"
    
    print(f"URL: {article_url}")
    r2 = requests.get(article_url)
    soup2 = BeautifulSoup(r2.text, 'lxml')
    
    title = soup2.select_one('h1')
    if title:
        print(f"Title: {title.get_text(strip=True)[:80]}")
    
    # Find content
    for sel in ['article p', '.post p', '.content p', 'main p']:
        paras = soup2.select(sel)
        if len(paras) > 3:
            print(f"\nContent selector: {sel} ({len(paras)} paragraphs)")
            print(f"Sample: {paras[0].get_text(strip=True)[:120]}")
            break
