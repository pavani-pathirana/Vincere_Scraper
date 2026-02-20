"""Test lakvahini pagination more carefully"""
import requests
from bs4 import BeautifulSoup

url = 'https://lakvahini.lk/archives/category/entertainment/'
print(f"Testing: {url}")
r = requests.get(url, timeout=10)
soup = BeautifulSoup(r.text, 'lxml')

print("\nAll links with '/page/' in href:")
page_links = []
for link in soup.select('a'):
    href = link.get('href', '')
    if '/page/' in href:
        text = link.get_text(strip=True)
        classes = link.get('class', [])
        print(f"  Text: '{text}' | href: {href} | class: {classes}")
        page_links.append((text, href, classes))

# Find the next link - likely the one with no text that points to page/2/
print("\n\nFinding 'next' link:")
for link in soup.select('a[href*="/page/2/"]'):
    text = link.get_text(strip=True)
    if not text or text in ['', '›', '»', 'Next', 'පෙර']:
        print(f"  Potential next link: text='{text}', href={link.get('href')}, class={link.get('class')}")

# Check for rel="next"
print("\nLinks with rel='next':")
next_link = soup.select_one('a[rel="next"]')
if next_link:
    print(f"  Found: {next_link.get('href')}")
else:
    print("  None found")
