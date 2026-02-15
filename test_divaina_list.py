import requests
from bs4 import BeautifulSoup

# Test Divaina category page
url = 'https://www.divaina.lk/category/main-news'

print("Testing Divaina category page structure...")
print(f"URL: {url}\n")

response = requests.get(url, timeout=10, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

soup = BeautifulSoup(response.content, 'lxml')

# Find articles
articles = soup.select('article')
print(f"Found {len(articles)} article elements\n")

# Analyze first few articles
for i, article in enumerate(articles[:3], 1):
    print(f"Article {i}:")
    print(f"  Classes: {article.get('class')}")
    
    # Find link
    link = article.select_one('a')
    if link:
        print(f"  Link: {link.get('href')}")
    
    # Find headline
    headline = article.select_one('h2, h3, .jeg_post_title')
    if headline:
        print(f"  Headline: {headline.get_text(strip=True)[:80]}")
    
    # Find date
    date_elem = article.select_one('time, .jeg_meta_date')
    if date_elem:
        print(f"  Date: {date_elem.get_text(strip=True)}")
    
    print()

# Check pagination
pagination = soup.select('.pagination a, .jeg_navigation a, .page-numbers, [class*="page"]')
print(f"\nPagination elements: {len(pagination)}")
if pagination:
    for elem in pagination[:5]:
        print(f"  {elem.name}: {elem.get_text(strip=True)} → {elem.get('href')}")
