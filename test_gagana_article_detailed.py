"""Test Gagana article page detailed structure"""
import requests
from bs4 import BeautifulSoup

url = "https://gagana.lk/article/two-districts-under-landslide-watch-1771220934"

response = requests.get(url, timeout=15)
print(f"Status: {response.status_code}\n")

soup = BeautifulSoup(response.text, 'lxml')

# Find all paragraphs with substantial content
print("=== All paragraphs with >50 chars ===")
all_paras = soup.find_all('p')
content_paras = []
for i, p in enumerate(all_paras):
    text = p.get_text(strip=True)
    if len(text) > 50:
        content_paras.append(p)
        parent_classes = ' '.join(p.parent.get('class', [])) if p.parent else 'no parent'
        print(f"P{i+1}: {len(text)} chars")
        print(f"  Parent: <{p.parent.name if p.parent else 'none'}> class='{parent_classes}'")
        print(f"  Text: {text[:100]}...\n")

print(f"Total content paragraphs: {len(content_paras)}")

# Try to find common parent
if content_paras:
    print("\n=== Finding common parent ===")
    first_para = content_paras[0]
    parent = first_para.parent
    depth = 0
    while parent and depth < 5:
        parent_classes = ' '.join(parent.get('class', []))
        parent_id = parent.get('id', '')
        print(f"Level {depth}: <{parent.name}> class='{parent_classes}' id='{parent_id}'")
        
        # Check if this parent contains all content paragraphs
        paras_in_parent = parent.find_all('p')
        content_in_parent = sum(1 for p in paras_in_parent if len(p.get_text(strip=True)) > 50)
        print(f"  Contains {content_in_parent}/{len(content_paras)} content paragraphs")
        
        if content_in_parent == len(content_paras):
            print(f"  ✓ THIS IS THE CONTENT CONTAINER!")
            if parent_classes:
                print(f"\n### Use selector: .{parent_classes.split()[0]}")
            elif parent_id:
                print(f"\n### Use selector: #{parent_id}")
            break
        
        parent = parent.parent
        depth += 1
