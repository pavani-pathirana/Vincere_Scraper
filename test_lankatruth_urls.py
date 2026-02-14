"""Quick test of LankaTruth URLs"""
import requests
from bs4 import BeautifulSoup

urls = [
    'https://lankatruth.com/si/?cat=3',
    'https://lankatruth.com/si/?paged=2&cat=3',
]

for url in urls:
    resp = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
    print(f"\n{url}")
    print(f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.content, 'lxml')
        articles = soup.select('article')
        posts = soup.select('.post')
        title = soup.select_one('title')
        
        print(f"Articles: {len(articles)}")
        print(f"Posts: {len(posts)}")
        print(f"Title: {title.get_text()[:80] if title else 'None'}")
