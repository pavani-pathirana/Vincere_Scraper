"""
Test AdaDerana pagination starting point
"""
import requests
from bs4 import BeautifulSoup
import re

category_id = '2'  # sports

for page in range(0, 5):
    url = f'https://sinhala.adaderana.lk/news.php?id={category_id}' if page == 0 else f'https://sinhala.adaderana.lk/news.php?id={category_id}&page={page}'
    
    print(f"\nPage {page}: {url}")
    
    try:
        response = requests.get(url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'lxml')
        all_links = soup.select('a[href]')
        
        # Find article links
        article_links = []
        for link in all_links:
            href = link.get('href', '')
            if re.search(r'/news/\d+|news/\d+', href):
                article_links.append(href)
        
        # Dedupe
        article_links = list(set(article_links))
        
        print(f"  Status: {response.status_code}")
        print(f"  Articles found: {len(article_links)}")
        
        if article_links:
            print(f"  Sample:")
            for href in article_links[:3]:
                print(f"    {href}")
    
    except Exception as e:
        print(f"  ERROR: {e}")
