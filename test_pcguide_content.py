import requests
from bs4 import BeautifulSoup

# Test one article URL
url = "https://www.pcguide.lk/byd-surpass-the-tesla/"
r = requests.get(url)
soup = BeautifulSoup(r.text, 'lxml')

# Find all elements with content in class name
content_divs = soup.select('[class*="content"]')
print(f"Found {len(content_divs)} elements with 'content' in class\n")

for i, div in enumerate(content_divs[:10]):
    classes = div.get('class', [])
    paras = div.select('p')
    text_len = len(div.get_text(strip=True))
    print(f"{i+1}. Classes: {classes}")
    print(f"   Paragraphs: {len(paras)}, Text length: {text_len}")
    if paras:
        preview = paras[0].get_text(strip=True)[:100]
        print(f"   First para: {preview}...")
    print()
