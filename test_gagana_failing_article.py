"""Test one of the failing Gagana articles"""
import requests
from bs4 import BeautifulSoup

url = "https://gagana.lk/article/potato-prices-may-rise-after-harvest-ends-1771078850"

response = requests.get(url, timeout=15)
print(f"Status: {response.status_code}\n")

soup = BeautifulSoup(response.text, 'lxml')

# Test .ds-content
print("=== Testing .ds-content selector ===")
content_elem = soup.select_one('.ds-content')
if content_elem:
    text = content_elem.get_text(strip=True)
    print(f"Found: {len(text)} chars")
    print(f"Text: {text[:200]}...")
else:
    print("NOT FOUND")

# Look for any div with content
print("\n=== Looking for content divs ===")
all_divs = soup.find_all('div', class_=True)
for div in all_divs:
    classes = ' '.join(div.get('class', []))
    text = div.get_text(strip=True)
    if len(text) > 200 and len(text) < 1000:
        print(f"Class: {classes}")
        print(f"Length: {len(text)} chars")
        print(f"Sample: {text[:150]}...")
        print()

# Find all paragraphs
print("=== All paragraphs ===")
paras = soup.find_all('p')
print(f"Total <p> tags: {len(paras)}")
for i, p in enumerate(paras):
    text = p.get_text(strip=True)
    if len(text) > 50:
        parent_class = ' '.join(p.parent.get('class', [])) if p.parent else ''
        print(f"P{i+1}: {len(text)} chars, parent class: {parent_class}")
        print(f"  {text[:100]}...")
