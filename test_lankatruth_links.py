"""Extract article links from LankaTruth"""
import requests
from bs4 import BeautifulSoup

url = 'https://lankatruth.com/si/?cat=3'

resp = requests.get(url, timeout=15, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

soup = BeautifulSoup(resp.content, 'lxml')
articles = soup.select('article')

print(f"Found {len(articles)} articles\n")

for i, article in enumerate(articles[:5], 1):
    # Find link
    link = article.select_one('a[href*="/si/"]') or article.select_one('a')
    
    if link:
        href = link.get('href', '')
        
        # Find title
        title_elem = (
            article.select_one('h2') or 
            article.select_one('h3') or 
            article.select_one('.elementor-post__title') or
            link
        )
        title = title_elem.get_text().strip() if title_elem else 'No title'
        
        print(f"{i}. {title[:60]}")
        print(f"   URL: {href}")
        print()
