"""
Find actual Lankadeepa categories from homepage
"""
import requests
from bs4 import BeautifulSoup
import re

url = 'https://www.lankadeepa.lk/'
response = requests.get(url, timeout=30, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

soup = BeautifulSoup(response.content, 'lxml')

print("="*70)
print("FINDING ALL LANKADEEPA LINKS")
print("="*70)

# Get all links and categorize them
category_links = {}

for link in soup.select('a[href]'):
    href = link.get('href', '')
    text = link.get_text(strip=True)
    
    # Convert relative to absolute
    if href.startswith('/') and not href.startswith('//'):
        href = 'https://www.lankadeepa.lk' + href
    
    # Look for category patterns in href
    if 'lankadeepa.lk' in href:
        # Extract category name and ID
        match = re.search(r'lankadeepa\.lk/([a-z-]+)/(\d+)/?', href)
        if match:
            cat_name = match.group(1)
            cat_id = match.group(2)
            
            if cat_name not in category_links:
                category_links[cat_name] = {
                    'id': cat_id,
                    'url': href,
                    'text': text
                }

print("\nFound categories with IDs:")
for cat, info in sorted(category_links.items()):
    if len(cat) > 3:  # Filter out very short names
        print(f"  {cat:20s} | ID: {info['id']:4s} | Text: {info['text'][:30]:30s}")

# Test each category
print("\n" + "="*70)
print("TESTING EACH CATEGORY")
print("="*70)

working_categories = {}

for cat, info in sorted(category_links.items()):
    if len(cat) <= 3:
        continue
    
    # Test the category URL
    test_url = f"https://www.lankadeepa.lk/{cat}/{info['id']}/"
    try:
        resp = requests.get(test_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        test_soup = BeautifulSoup(resp.content, 'lxml')
        
        # Look for article links in this category
        article_pattern = re.compile(rf'/{cat}/[^/]+/\d+-\d+')
        article_count = 0
        
        for a in test_soup.select('a[href]'):
            if article_pattern.search(a.get('href', '')):
                article_count += 1
        
        # Test pagination
        page2_url = f"https://www.lankadeepa.lk/{cat}/{info['id']}/30"
        resp2 = requests.get(page2_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        has_pagination = resp2.status_code == 200
        
        if resp.status_code == 200 and article_count > 0:
            print(f"\n✓ {cat:20s} | Articles: {article_count:3d} | Pagination: {has_pagination}")
            working_categories[cat] = info['id']
        else:
            print(f"✗ {cat:20s} | Status: {resp.status_code} | Articles: {article_count}")
            
    except Exception as e:
        print(f"✗ {cat:20s} | Error: {str(e)[:50]}")

# Generate code
print("\n" + "="*70)
print("PYTHON CODE FOR SCRAPER")
print("="*70)

print("\n# Categories:")
print("CATEGORIES = {")
print("    'latest': 'Latest',  # Homepage")
for cat in sorted(working_categories.keys()):
    cat_key = cat.replace('-', '_')
    cat_title = cat.replace('-', ' ').title()
    print(f"    '{cat_key}': '{cat_title}',  # ID: {working_categories[cat]}")
print("}")

print("\n# Category URLs:")
print("return {")
print("    'latest': f'{self.BASE_URL}/',  # Homepage")
for cat in sorted(working_categories.keys()):
    cat_key = cat.replace('-', '_')
    print(f"    '{cat_key}': f'{{self.BASE_URL}}/{cat}/{working_categories[cat]}/',")
print("}")
