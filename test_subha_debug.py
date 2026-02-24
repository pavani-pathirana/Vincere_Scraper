"""Quick test to debug Subha scraper"""

import requests
from bs4 import BeautifulSoup

url = "https://subha.lk/blogs?page=1"

response = requests.get(url, timeout=10)
soup = BeautifulSoup(response.text, 'lxml')

all_links = soup.select('a[href]')

print(f"Total links: {len(all_links)}")

# Show all /blogs/ links
print("\nAll links containing '/blogs/':")
for link in all_links:
    href = link.get('href', '')
    if '/blogs/' in href:
        text = link.get_text(strip=True)
        print(f"  Text: '{text[:50]}' ({len(text)} chars)")
        print(f"  Href: {href}")
        print(f"  Slash count: {href.count('/')}")
        print()

blog_links = []
for link in all_links:
    href = link.get('href', '')
    
    # Filter for blog post links (format: /blogs/{id})
    if '/blogs/' in href and href.count('/') == 2:
        text = link.get_text(strip=True)
        print(f"Found link: '{text}' ({len(text)} chars) -> {href}")
        
        # Skip navigation links
        if text and len(text) > 15 and 'Next' not in text and 'Blogs' != text:
            blog_links.append((href, text))

print(f"\nFiltered blog links: {len(blog_links)}")

# Try with relaxed filtering
print("\n\nWith relaxed filtering (len > 10):")
blog_links2 = []
for link in all_links:
    href = link.get('href', '')
    
    if '/blogs/' in href and href.count('/') == 2:
        text = link.get_text(strip=True)
        
        if text and len(text) > 10 and 'Next' not in text:
            blog_links2.append((href, text[:50]))

print(f"Relaxed blog links: {len(blog_links2)}")
for href, text in blog_links2[:10]:
    print(f"  {text}")
