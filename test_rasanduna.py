import requests
from bs4 import BeautifulSoup

url = 'https://www.silumina.lk/category/rasanduna/'
r = requests.get(url, timeout=10)
soup = BeautifulSoup(r.content, 'lxml')
articles = soup.select('article')

print(f'rasanduna: {r.status_code} - {len(articles)} articles')
title = soup.select_one('h1, .page-title, title')
if title:
    print(f'Title: {title.get_text(strip=True)}')
