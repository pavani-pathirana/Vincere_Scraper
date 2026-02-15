import requests
from bs4 import BeautifulSoup

# Test Ada.lk article and list pages
print("Testing Ada.lk structure...\n")

# Test list page
list_url = 'https://www.ada.lk/sports/9'
print(f"Testing list page: {list_url}")

response = requests.get(list_url, timeout=10, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

soup = BeautifulSoup(response.content, 'lxml')

# Find article links
links = soup.select('a[href]')
article_links = []

for link in links:
    href = link.get('href', '')
    if 'ada.lk' in href and any(cat in href for cat in ['/sports/', '/business/', '/latest-news/', '/international/']):
        article_links.append(href)
        text = link.get_text(strip=True)
        if text and len(text) > 10:
            print(f"  Link: {href}")
            print(f"    Text: {text[:80]}")

if article_links:
    test_article = article_links[0]
    print(f"\n\nTesting article page: {test_article}")
    
    article_response = requests.get(test_article, timeout=10, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    article_soup = BeautifulSoup(article_response.content, 'lxml')
    
    # Save for inspection
    with open('ada_article.html', 'w', encoding='utf-8') as f:
        f.write(article_response.text)
    print("HTML saved to ada_article.html")
    
    # Find headline
    h1 = article_soup.select_one('h1')
    if h1:
        print(f"\nHeadline (h1): {h1.get_text(strip=True)}")
    
    # Test various content selectors
    print("\nContent selector tests:")
    selectors = [
        ('.article-content', 'article-content class'),
        ('.news-content', 'news-content class'),
        ('.post-content', 'post-content class'),
        ('.entry-content', 'entry-content class'),
        ('article .content', 'article content'),
        ('.main-content p', 'main-content paragraphs'),
        ('#content', 'content ID'),
        ('.description', 'description class'),
        ('[class*="body"]', 'class containing body')
    ]
    
    for selector, desc in selectors:
        elements = article_soup.select(selector)
        if elements:
            text = elements[0].get_text(strip=True)
            print(f"  {desc}: {len(text)} chars")
            if len(text) > 100:
                print(f"    Preview: {text[:150]}...")
