import requests
from bs4 import BeautifulSoup
import json

print("="*80)
print("Detailed Investigation of 5 News Sites")
print("="*80)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# 1. GAGANA.LK
print("\n\n### 1. GAGANA.LK ###")
try:
    resp = requests.get("https://gagana.lk/", headers=headers, timeout=10)
    soup = BeautifulSoup(resp.content, 'lxml')
    
    # Find article containers
    posts = soup.select('[class*="post"]')
    print(f"Posts: {len(posts)}")
    
    if posts:
        first = posts[0]
        print(f"First post classes: {first.get('class')}")
        
        # Find title
        title = first.select_one('h1, h2, h3, h4, a')
        if title:
            print(f"Title: {title.get_text(strip=True)[:80]}")
        
        # Find link
        link = first.select_one('a[href]')
        if link:
            article_url = link.get('href')
            print(f"Article URL: {article_url}")
            
            # Test article page
            if article_url.startswith('http'):
                print("\n  Testing article page...")
                art_resp = requests.get(article_url, headers=headers, timeout=10)
                art_soup = BeautifulSoup(art_resp.content, 'lxml')
                
                # Check content selectors
                for sel in ['.article-content', '.post-content', '.entry-content', 'article', '.content']:
                    content = art_soup.select_one(sel)
                    if content:
                        paras = content.select('p')
                        print(f"  Content found with '{sel}': {len(paras)} paragraphs")
                        if paras:
                            print(f"  Sample: {paras[0].get_text(strip=True)[:100]}")
                        break
    
    # Check categories
    cat_links = soup.select('a[href*="category"], a[href*="news"]')
    print(f"\nCategory links: {len(cat_links)}")
    for link in cat_links[:5]:
        text = link.get_text(strip=True)
        href = link.get('href')
        if text and len(text) > 2:
            print(f"  {text}: {href}")

except Exception as e:
    print(f"Error: {e}")

# 2. MAWRATA NEWS
print("\n\n### 2. MAWRATA NEWS ###")
try:
    resp = requests.get("https://sinhala.mawratanews.lk/", headers=headers, timeout=10)
    soup = BeautifulSoup(resp.content, 'lxml')
    
    posts = soup.select('article')[:5]
    print(f"Articles: {len(posts)}")
    
    if posts:
        first = posts[0]
        print(f"First article classes: {first.get('class')}")
        
        title = first.select_one('h1, h2, h3, .entry-title, a')
        if title:
            print(f"Title: {title.get_text(strip=True)[:80]}")
        
        link = first.select_one('a[href]')
        if link:
            print(f"Link: {link.get('href')[:100]}")
    
    # Check categories
    nav = soup.select('.menu a, nav a, .category a')
    print(f"\nNavigation links: {len(nav)}")
    for link in nav[:8]:
        text = link.get_text(strip=True)
        href = link.get('href')
        if text and 'category' in href:
            print(f"  {text}: {href}")
    
    # Check pagination
    pag = soup.select('.pagination a, .page-numbers')
    if pag:
        print(f"\nPagination elements: {len(pag)}")
        for p in pag[:3]:
            print(f"  {p.get_text(strip=True)}: {p.get('href', 'N/A')[:50]}")

except Exception as e:
    print(f"Error: {e}")

# 3. LANKAPUVATH
print("\n\n### 3. LANKAPUVATH ###")
try:
    resp = requests.get("https://sinhala.lankapuvath.lk/", headers=headers, timeout=10)
    soup = BeautifulSoup(resp.content, 'lxml')
    
    posts = soup.select('[class*="post"]')[:5]
    print(f"Posts: {len(posts)}")
    
    if posts:
        first = posts[0]
        print(f"First post classes: {first.get('class')}")
        
        title = first.select_one('h1, h2, h3, a')
        if title:
            print(f"Title: {title.get_text(strip=True)[:80]}")
        
        link = first.select_one('a[href*="/202"]')
        if link:
            print(f"Link: {link.get('href')[:100]}")
    
    # Categories
    cats = soup.select('a[href*="category"]')
    print(f"\nCategories: {len(cats)}")
    for cat in cats[:8]:
        text = cat.get_text(strip=True)
        href = cat.get('href')
        if text and len(text) > 2:
            print(f"  {text}: {href}")

except Exception as e:
    print(f"Error: {e}")

# 4. SARASAVIYA
print("\n\n### 4. SARASAVIYA ###")
try:
    resp = requests.get("https://sarasaviya.lk/", headers=headers, timeout=10)
    soup = BeautifulSoup(resp.content, 'lxml')
    
    posts = soup.select('[class*="post"]')[:5]
    print(f"Posts: {len(posts)}")
    
    if posts:
        first = posts[0]
        title = first.select_one('h1, h2, h3, a')
        if title:
            print(f"Title: {title.get_text(strip=True)[:80]}")
        
        link = first.select_one('a[href]')
        if link:
            print(f"Link: {link.get('href')[:100]}")
    
    # Categories from earlier scan
    cats = soup.select('a[href*="category"]')
    print(f"\nCategories: {len(cats)}")
    seen = set()
    for cat in cats:
        href = cat.get('href')
        text = cat.get_text(strip=True)
        if href and href not in seen and 'category' in href:
            seen.add(href)
            if text and len(text) > 2:
                print(f"  {text}: {href}")

except Exception as e:
    print(f"Error: {e}")

# 5. LANKA C NEWS
print("\n\n### 5. LANKA C NEWS ###")
try:
    resp = requests.get("https://www.lankacnews.com/", headers=headers, timeout=10)
    soup = BeautifulSoup(resp.content, 'lxml')
    
    posts = soup.select('.post')[:5]
    print(f"Posts: {len(posts)}")
    
    if posts:
        first = posts[0]
        print(f"First post classes: {first.get('class')}")
        
        title = first.select_one('h1, h2, h3, .entry-title, a')
        if title:
            print(f"Title: {title.get_text(strip=True)[:80]}")
        
        link = first.select_one('a[href*="/202"]')
        if link:
            article_url = link.get('href')
            print(f"Link: {article_url[:100]}")
            
            # Test article
            if article_url.startswith('http'):
                print("\n  Testing article page...")
                art_resp = requests.get(article_url, headers=headers, timeout=10)
                art_soup = BeautifulSoup(art_resp.content, 'lxml')
                
                for sel in ['.post-body', '.entry-content', '.post-content', 'article']:
                    content = art_soup.select_one(sel)
                    if content:
                        paras = content.select('p')
                        text_len = len(content.get_text(strip=True))
                        print(f"  Content with '{sel}': {len(paras)} paras, {text_len} chars")
                        break
    
    # Check for labels/categories
    labels = soup.select('a[href*="label"], a[href*="search"]')
    print(f"\nLabels/Categories: {len(labels)}")
    seen = set()
    for label in labels[:10]:
        href = label.get('href')
        text = label.get_text(strip=True)
        if href and href not in seen and ('label' in href or 'category' in href):
            seen.add(href)
            if text and len(text) > 2:
                print(f"  {text}: {href[:80]}")

except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*80)
print("Detailed investigation complete")
