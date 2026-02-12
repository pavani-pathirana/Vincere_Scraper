"""
Test Lankadeepa homepage pagination
"""
import requests
from bs4 import BeautifulSoup
import re

# Test different homepage pagination patterns
test_urls = [
    'https://www.lankadeepa.lk/',
    'https://www.lankadeepa.lk/101/',  # News category might be 101
    'https://www.lankadeepa.lk/101/30',
    'https://www.lankadeepa.lk/latest-news/101/',
    'https://www.lankadeepa.lk/latest-news/101/30',
]

pattern = re.compile(r'/[a-z-]+/[^/]+/\d+-\d+')

for url in test_urls:
    try:
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Count article links
        article_count = 0
        for link in soup.select('a[href]'):
            href = link.get('href', '')
            if pattern.search(href) and 'lankadeepa.lk' in (href if 'http' in href else url + href):
                article_count += 1
        
        print(f"{url}")
        print(f"  Status: {response.status_code}")
        print(f"  Articles: {article_count}")
        print()
    except Exception as e:
        print(f"{url}")
        print(f"  Error: {e}")
        print()
