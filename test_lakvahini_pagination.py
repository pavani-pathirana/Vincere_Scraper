"""Test lakvahini pagination"""
import requests
from bs4 import BeautifulSoup

url = 'https://lakvahini.lk/archives/category/entertainment/'
print(f"Testing: {url}")
r = requests.get(url, timeout=10)
soup = BeautifulSoup(r.text, 'lxml')

# Find articles
articles = soup.select('h3 a')
print(f"Articles: {len(articles)}")

# Find pagination
print("\nPagination elements:")
print("Looking for a.next.page-numbers:")
next1 = soup.select_one('a.next.page-numbers')
print(f"  a.next.page-numbers: {next1}")

print("\nAll links with 'page' in href:")
page_links = soup.select('a[href*="page"]')
for link in page_links[:5]:
    print(f"  {link.get_text(strip=True)}: {link.get('href')}")
    print(f"    Classes: {link.get('class')}")

print("\nAll .page-numbers links:")
page_nums = soup.select('.page-numbers')
for link in page_nums:
    print(f"  {link.name} - Text: '{link.get_text(strip=True)}' - href: {link.get('href')} - class: {link.get('class')}")

print("\nAll nav elements:")
navs = soup.select('nav, .navigation, .pagination')
for nav in navs[:3]:
    print(f"\n{nav.name} - class: {nav.get('class')}")
    print(f"  HTML: {str(nav)[:300]}...")
