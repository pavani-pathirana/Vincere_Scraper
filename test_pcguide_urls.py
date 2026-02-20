import requests
from bs4 import BeautifulSoup

r = requests.get('https://www.pcguide.lk/category/tech-news/')
soup = BeautifulSoup(r.text, 'lxml')

# Check h2/h3 article links and their parents
links = soup.select('h2 a, h3 a')
print(f"Found {len(links)} article links via h2/h3")

for i, link in enumerate(links[:5]):
    url = link.get('href', '')
    title = link.get_text(strip=True)[:80]
    parent = link.parent.parent
    parent_classes = parent.get('class', [])
    print(f"\n{i+1}. {title}")
    print(f"   URL: {url}")
    print(f"   Parent: {parent.name}, classes: {parent_classes}")
