import requests
from bs4 import BeautifulSoup

# Test real Ada.lk article
url = 'https://www.ada.lk/sports/අනුරාධපුරට-නව-ක්‍රීඩා-සංකීර්ණයක්/9-421237'

print(f"Testing Ada.lk article: {url}\n")

response = requests.get(url, timeout=10, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

soup = BeautifulSoup(response.content, 'lxml')

# Find headline
h1 = soup.select_one('h1')
if h1:
    print(f"Headline (h1): {h1.get_text(strip=True)}\n")

# Find description/content
description = soup.select_one('.description')
if description:
    text = description.get_text(strip=True)
    print(f"Description class: {len(text)} chars")
    print(f"Preview: {text[:200]}\n")

# Find all paragraphs
paragraphs = soup.select('p')
print(f"Total paragraphs: {len(paragraphs)}\n")

# Filter meaningful paragraphs
content_paras = []
for p in paragraphs:
    text = p.get_text(strip=True)
    if len(text) > 50:  # Skip short ones
        content_paras.append(text)

print(f"Content paragraphs (>50 chars): {len(content_paras)}\n")
if content_paras:
    print("First 3 paragraphs:")
    for i, text in enumerate(content_paras[:3], 1):
        print(f"  {i}. {text[:150]}...")

# Check for article body container
body_containers = soup.select('.article-body, .news-body, [itemprop="articleBody"], .single-content')
print(f"\nArticle body containers: {len(body_containers)}")
for container in body_containers:
    text = container.get_text(strip=True)
    print(f"  {container.name}.{'.'.join(container.get('class', []))}: {len(text)} chars")
