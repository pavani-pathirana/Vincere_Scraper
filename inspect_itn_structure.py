"""Inspect ITN article link structure"""
import requests
from bs4 import BeautifulSoup

url = "https://www.itnnews.lk/local/"
response = requests.get(url, timeout=10)
soup = BeautifulSoup(response.content, 'lxml')

# Find links with 2026
links_2026 = soup.find_all('a', href=lambda x: x and '2026' in x and '/2026/' in x)

print(f"Found {len(links_2026)} links with 2026")
print("="*70)

# Look at first few
for i, link in enumerate(links_2026[:6], 1):
    href = link.get('href', '')
    text = link.get_text(strip=True)
    
    print(f"\n{i}. URL: {href}")
    print(f"   Link text: '{text}'")
    print(f"   Link text length: {len(text)}")
    
    # Check parent and siblings for headline text
    parent = link.parent
    if parent:
        print(f"   Parent tag: {parent.name}")
        print(f"   Parent classes: {parent.get('class', [])}")
        
        # Look for h1-h6 in parent or siblings
        for tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            headline_in_parent = parent.find(tag_name)
            if headline_in_parent:
                print(f"   Found {tag_name} in parent: {headline_in_parent.get_text(strip=True)[:50]}")
                break
        
        # Check next sibling
        next_sib = link.find_next_sibling()
        if next_sib:
            print(f"   Next sibling: {next_sib.name}, text: {next_sib.get_text(strip=True)[:50]}")
    
    print(f"   Full link HTML: {str(link)[:200]}")
