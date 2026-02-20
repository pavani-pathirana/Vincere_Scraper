"""Comprehensive test for all 4 new sites"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def test_site(name, base_url, category_url, article_selectors, content_selectors):
    print(f"\n{'='*70}")
    print(f"{name}")
    print(f"{'='*70}")
    
    try:
        # Test category page
        print(f"\n1. Category/Main Page: {category_url}")
        r = requests.get(category_url, timeout=15)
        soup = BeautifulSoup(r.text, 'lxml')
        
        # Find articles
        found_selector = None
        articles = []
        for selector in article_selectors:
            articles = soup.select(selector)
            if len(articles) > 5:
                found_selector = selector
                print(f"✓ Found {len(articles)} articles using: {selector}")
                break        
        
        if not articles:
            print("❌ No articles found")
            return
        
        # Show first 3 articles
        print("\nFirst 3 articles:")
        for i, elem in enumerate(articles[:3], 1):
            link = elem if elem.name == 'a' else elem.select_one('a')
            if link:
                title = link.get_text(strip=True)
                href = link.get('href', '')
                full_url = urljoin(category_url, href)
                print(f"  {i}. {title[:70]}")
                print(f"     → {full_url}")
        
        # Check pagination
        pagination = soup.select('.pagination a, .nav-links a, a[rel="next"], .page-numbers a')
        if pagination:
            print(f"\n✓ Pagination found: {len(pagination)} links")
            for p in pagination[:3]:
                print(f"  - {p.get_text(strip=True)}: {urljoin(category_url, p.get('href', ''))}")
        
        # Test first article page
        first_link = articles[0] if articles[0].name == 'a' else articles[0].select_one('a')
        if first_link and first_link.get('href'):
            article_url = urljoin(category_url, first_link.get('href'))
            print(f"\n2. Testing Article Page: {article_url}")
            
            r2 = requests.get(article_url, timeout=15)
            soup2 = BeautifulSoup(r2.text, 'lxml')
            
            # Find title
            title = soup2.select_one('h1, .entry-title, .post-title, article h1')
            if title:
                print(f"  Title: {title.get_text(strip=True)[:80]}")
            
            # Find content
            found_content = False
            for selector in content_selectors:
                content = soup2.select_one(selector)
                if content:
                    paras = content.select('p')
                    if len(paras) > 0:
                        print(f"  Content: {selector} ({len(paras)} paragraphs)")
                        print(f"  Sample: {paras[0].get_text(strip=True)[:120]}")
                        found_content = True
                        break
            
            if not found_content:
                print("  ⚠️ No content found with standard selectors")
            
            # Find date
            date = soup2.select_one('time, .date, .post-date, .published, .entry-date')
            if date:
                print(f"  Date: {date.get_text(strip=True)}")
            
            # Find author
            author = soup2.select_one('.author, .by-author, [rel="author"], .entry-author')
            if author:
                print(f"  Author: {author.get_text(strip=True)}")
        
        print(f"\n✓ {name} analysis complete")
        
    except Exception as e:
        print(f"❌ Error: {e}")

# Test all 4 sites
sites = [
    {
        'name': 'COLOMBO TIMES SINHALA',
        'base': 'https://colombotimes.lk/sinhala/',
        'category': 'https://colombotimes.lk/sinhala/local',
        'article_selectors': ['.post a', 'article a', '.post h2 a'],
        'content_selectors': ['.entry-content', '.post-content', 'article .content']
    },
    {
        'name': 'LAKVAHINI',
        'base': 'https://lakvahini.lk/',
        'category': 'https://lakvahini.lk/',
        'article_selectors': ['h3 a', 'article h3 a', '.post h3 a'],
        'content_selectors': ['.entry-content', 'article .content', '.post-content', '.article-content']
    },
    {
        'name': 'ASIAN MIRROR SINHALA',
        'base': 'https://sinhala.asianmirror.lk/',
        'category': 'https://sinhala.asianmirror.lk/news/local/',
        'article_selectors': ['[class*="post"] h2 a', 'article h2 a', '.post-title a', 'h2 a'],
        'content_selectors': ['.entry-content', '.post-content', 'article .content', '.content']
    },
    {
        'name': 'SIYATHA NEWS',
        'base': 'https://siyathanews.lk/',
        'category': 'https://siyathanews.lk/archives/category/local-news',
        'article_selectors': ['h3 a', 'article h3 a', '.entry-title a'],
        'content_selectors': ['.entry-content', '.post-content', 'article .content']
    }
]

for site in sites:
    test_site(
        site['name'],
        site['base'],
        site['category'],
        site['article_selectors'],
        site['content_selectors']
    )

print(f"\n{'='*70}")
print("ALL TESTS COMPLETE")
print(f"{'='*70}")
