"""
Detailed HTML structure inspection for NewsFirst article pages
"""
import requests
from bs4 import BeautifulSoup

test_url = "https://www.newsfirst.lk/sinhala/2026/02/10/%e0%b6%a2%e0%b6%b1%e0%b6%b4%e0%b6%ad%e0%b7%92-%e0%b6%85%e0%b6%b1%e0%b7%94%e0%b6%bb-%e0%b6%b4%e0%b7%8f%e0%b6%9a%e0%b7%92%e0%b7%83%e0%b7%8a%e0%b6%ae%e0%b7%8f%e0%b6%b1"

print(f"Fetching URL: {test_url}\n")

response = requests.get(test_url, timeout=30, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

soup = BeautifulSoup(response.content, 'lxml')

# Find the paragraphs and trace their parent structure
print("=" * 70)
print("PARAGRAPH PARENT STRUCTURE")
print("=" * 70)

paragraphs = soup.select('p')
if paragraphs:
    # Get first paragraph with meaningful content
    content_p = None
    for p in paragraphs:
        text = p.get_text(strip=True)
        if len(text) > 50:  # Skip short paragraphs
            content_p = p
            break
    
    if content_p:
        print(f"Sample paragraph ({len(content_p.get_text(strip=True))} chars):")
        print(f"  {content_p.get_text()[:150]}...\n")
        
        print("Parent hierarchy:")
        parent = content_p.parent
        level = 1
        while parent and level <= 10:
            tag_name = parent.name
            tag_class = ' '.join(parent.get('class', []))
            tag_id = parent.get('id', '')
            
            # Count children
            children_tags = [child.name for child in parent.children if hasattr(child, 'name')]
            
            print(f"  Level {level}: <{tag_name} class='{tag_class}' id='{tag_id}'>")
            print(f"    Child tags: {', '.join(set(children_tags))}")
            
            # If this is a div with a class or id, check if it contains all paragraphs
            if tag_name == 'div' and (tag_class or tag_id):
                paragraphs_in_container = parent.select('p')
                text_length = len(parent.get_text(strip=True))
                print(f"    Contains {len(paragraphs_in_container)} <p> tags, {text_length} chars total")
                
                # This might be our content container!
                if len(paragraphs_in_container) >= 3:
                    print(f"    ⭐ POTENTIAL CONTENT CONTAINER")
            
            parent = parent.parent
            level += 1

print("\n" + "=" * 70)
print("SEARCHING FOR COMMON CONTENT WRAPPERS")
print("=" * 70)

# Test broader selectors
broad_selectors = [
    ('main', 'main'),
    ('#content', '#content'),
    ('.content', '.content'),
    ('#main', '#main'),
    ('.main-content', '.main-content'),
    ('.post', '.post'),
    ('.single', '.single'),
    ('div[class*="post"]', 'div with "post" in class'),
    ('div[class*="article"]', 'div with "article" in class'),
    ('div[class*="content"]', 'div with "content" in class'),
]

for selector, description in broad_selectors:
    elem = soup.select_one(selector)
    if elem:
        p_count = len(elem.select('p'))
        text_len = len(elem.get_text(strip=True))
        if p_count > 0:
            print(f"✓ {description}: {p_count} paragraphs, {text_len} chars")
            print(f"   Classes: {elem.get('class', [])}")
            print(f"   ID: {elem.get('id', 'none')}")

print("\n" + "=" * 70)
print("ALL DIVS WITH SINHALA TEXT")
print("=" * 70)

# Find all divs that contain Sinhala text
divs = soup.find_all('div')
sinhala_divs = []

for div in divs:
    text = div.get_text(strip=True)
    # Check if contains Sinhala characters (0x0D80-0x0DFF Unicode range)
    if text and any('\u0d80' <= char <= '\u0dff' for char in text):
        # Count direct paragraphs (not nested deep)
        direct_ps = len([p for p in div.find_all('p', recursive=True)])
        if direct_ps >= 2:  # At least 2 paragraphs
            div_class = ' '.join(div.get('class', []))
            div_id = div.get('id', '')
            sinhala_divs.append((div_class, div_id, len(text), direct_ps))

# Sort by text length (longest first)
sinhala_divs.sort(key=lambda x: x[2], reverse=True)

print(f"Found {len(sinhala_divs)} divs with Sinhala content and 2+ paragraphs:\n")
for i, (div_class, div_id, text_len, p_count) in enumerate(sinhala_divs[:10]):
    print(f"{i+1}. <div class='{div_class}' id='{div_id}'>")
    print(f"   {text_len} chars, {p_count} paragraphs")
