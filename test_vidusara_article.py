"""
Test Vidusara.lk article structure
"""

import requests
from bs4 import BeautifulSoup

# Test article page
article_url = "https://www.vidusara.lk/science-news/9177/"

print(f"Testing Vidusara.lk Article Page")
print(f"URL: {article_url}")
print("=" * 70)

response = requests.get(article_url, timeout=10)
print(f"Status: {response.status_code}\n")

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'lxml')
    
    # Check for headline
    h1 = soup.find('h1')
    if h1:
        print(f"Headline: {h1.get_text(strip=True)}\n")
    
    # Check for article/post containers
    article = soup.find('article')
    if article:
        print(f"✓ Found <article> tag with classes: {article.get('class')}")
        
        # Look for content
        content = article.find(class_=lambda x: x and ('content' in str(x).lower() or 'entry' in str(x).lower()))
        if content:
            print(f"✓ Content container: {content.get('class')}")
            paragraphs = content.find_all('p')
            print(f"✓ Found {len(paragraphs)} paragraphs")
            if paragraphs:
                print(f"\nFirst paragraph preview:")
                print(f"  {paragraphs[0].get_text(strip=True)[:100]}...")
    
    # Check for date/author
    time = soup.find('time')
    if time:
        print(f"\n✓ Date: {time.get('datetime', time.get_text(strip=True))}")
    
    # Look for category links
    print("\n" + "=" * 70)
    print("Category Links on Homepage:")
    print("=" * 70)
    
    home_response = requests.get("https://www.vidusara.lk", timeout=10)
    home_soup = BeautifulSoup(home_response.text, 'lxml')
    
    # Look for category menu
    menu_links = home_soup.find_all('a', href=lambda x: x and '/category/' in x)
    if menu_links:
        print(f"\nFound {len(menu_links)} category links:")
        seen = set()
        for link in menu_links:
            href = link.get('href')
            text = link.get_text(strip=True)
            if href not in seen and text:
                seen.add(href)
                print(f"  - {text}: {href}")
