"""
Find article paragraphs on Asian Mirror
"""

import requests
from bs4 import BeautifulSoup

url = 'https://sinhala.asianmirror.lk/news/breaking/breaking-news-198/'

print(f"Testing: {url}\n")

r = requests.get(url, timeout=10)
r.encoding = 'utf-8'
soup = BeautifulSoup(r.text, 'lxml')

# Find all paragraphs
all_paras = soup.select('p')
print(f"Total paragraphs on page: {len(all_paras)}\n")

# Filter paragraphs with substantial text
substantive_paras = []
for para in all_paras:
    text = para.get_text(strip=True)
    if len(text) > 30:  # Longer than 30 chars
        substantive_paras.append((para, text))

print(f"Paragraphs with >30 chars: {len(substantive_paras)}\n")

print("="*70)
print("PARAGRAPHS WITH CONTENT")
print("="*70)

for i, (para, text) in enumerate(substantive_paras[:10], 1):
    parent = para.parent
    parent_class = ' '.join(parent.get('class', []))
    parent_id = parent.get('id', '')
    
    print(f"\n{i}. Parent: {parent.name} class='{parent_class}' id='{parent_id}'")
    print(f"   Text: {text[:80]}...")

# Try to find the main article container
print("\n" + "="*70)
print("FINDING ARTICLE CONTAINER")
print("="*70)

# Group paragraphs by parent
from collections import Counter
parent_counts = Counter()

for para, text in substantive_paras:
    parent = para.parent
    parent_key = f"{parent.name}.{' '.join(parent.get('class', []))}"
    parent_counts[parent_key] += 1

print("\nMost common parent containers:")
for parent_key, count in parent_counts.most_common(5):
    print(f"  {parent_key}: {count} paragraphs")

# Try finding the container with most paragraphs
if substantive_paras:
    # Find the common ancestor of all paragraphs
    first_para = substantive_paras[0][0]
    
    # Go up the tree and count paragraphs in each ancestor
    current = first_para.parent
    while current and current.name != 'body':
        paras_in_container = current.select('p')
        substantive_in_container = [p for p in paras_in_container if len(p.get_text(strip=True)) > 30]
        
        if len(substantive_in_container) >= 3:  # At least 3 paragraphs
            classes = ' '.join(current.get('class', []))
            id_attr = current.get('id', '')
            print(f"\n  {current.name} class='{classes}' id='{id_attr}': {len(substantive_in_container)} paras")
            
            # Show selector
            if classes:
                print(f"    Selector: .{classes.split()[0]}")
            elif id_attr:
                print(f"    Selector: #{id_attr}")
        
        current = current.parent
