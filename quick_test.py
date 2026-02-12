import requests
from bs4 import BeautifulSoup
import re

# Test specific category IDs
tests = [
    ('politics', 54),
    ('sunday/politics', 54),
    ('technology', 1),
    ('tech', 1),
]

for cat, cat_id in tests:
    url = f'https://www.lankadeepa.lk/{cat}/{cat_id}/'
    resp = requests.get(url, timeout=10)
    soup = BeautifulSoup(resp.content, 'lxml')
    pattern = re.compile(rf'/{cat}/[^/]+/\d+-\d+')
    count = len([a for a in soup.select('a[href]') if pattern.search(a.get('href', ''))])
    print(f'{cat:20s} ID:{cat_id:3d} | Status:{resp.status_code} | Articles:{count:3d}')
