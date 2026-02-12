"""
Test if NewsFirst pagination returns unique articles per page
"""
import requests
from bs4 import BeautifulSoup
import re

def get_article_urls(page_num):
    url = f"https://www.newsfirst.lk/sinhala/sports/?page={page_num}"
    print(f"\nFetching: {url}")
    
    response = requests.get(url, timeout=30, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    soup = BeautifulSoup(response.content, 'lxml')
    
    # Extract article URLs using date pattern
    all_links = soup.select('a[href]')
    date_pattern = re.compile(r'sinhala/\d{4}/\d{2}/\d{2}/')
    
    article_urls = []
    for link in all_links:
        href = link.get('href', '')
        if date_pattern.search(href):
            # Make absolute URL
            if not href.startswith('http'):
                href = f"https://www.newsfirst.lk/{href}" if not href.startswith('/') else f"https://www.newsfirst.lk{href}"
            article_urls.append(href)
    
    # Deduplicate
    unique_urls = list(dict.fromkeys(article_urls))
    
    print(f"Found {len(unique_urls)} unique article URLs")
    return unique_urls

# Test first 5 pages
all_urls = []
for page in range(1, 6):
    urls = get_article_urls(page)
    print(f"Sample URLs from page {page}:")
    for url in urls[:3]:
        print(f"  - {url}")
    all_urls.extend(urls)

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Total URLs collected: {len(all_urls)}")
print(f"Unique URLs: {len(set(all_urls))}")
print(f"Duplicates: {len(all_urls) - len(set(all_urls))}")

# Check if pages are returning same URLs
page_1_urls = set(get_article_urls(1))
page_2_urls = set(get_article_urls(2))
page_3_urls = set(get_article_urls(3))

print(f"\nPage 1 URLs: {len(page_1_urls)}")
print(f"Page 2 URLs: {len(page_2_urls)}")
print(f"Page 3 URLs: {len(page_3_urls)}")
print(f"Page 1 ∩ Page 2: {len(page_1_urls & page_2_urls)} overlapping")
print(f"Page 2 ∩ Page 3: {len(page_2_urls & page_3_urls)} overlapping")
print(f"Page 1 ∩ Page 3: {len(page_1_urls & page_3_urls)} overlapping")
