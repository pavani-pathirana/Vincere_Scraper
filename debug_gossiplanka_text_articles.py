import requests
from bs4 import BeautifulSoup

# Test a political news article (should have text content)
url = "https://www.gossiplankanews.com/2026/02/maithripala-sirisena-media-statement.html"

response = requests.get(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

print(f"Testing: {url}")
print(f"Status: {response.status_code}\n")

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'lxml')
    
    # Test headline
    print("=== Headline ===")
    headline_selectors = [
        'h1.post-title',
        'h1',
        '.post-title',
        'h2.post-title',
        '.entry-title'
    ]
    
    for sel in headline_selectors:
        h = soup.select_one(sel)
        if h:
            print(f"✓ Found with '{sel}': {h.get_text(strip=True)[:80]}")
            break
    
    # Test content
    print("\n=== Content ===")
    post_body = soup.select_one('.post-body')
    
    if post_body:
        print(f"✓ Found .post-body")
        
        # Check all elements inside
        all_text_elements = post_body.find_all(['p', 'div', 'span'])
        print(f"  Total text elements: {len(all_text_elements)}")
        
        # Get all paragraphs
        paragraphs = post_body.select('p')
        print(f"  <p> tags: {len(paragraphs)}")
        
        # Get text content
        full_text = post_body.get_text(strip=True)
        print(f"  Full text length: {len(full_text)} chars")
        
        if paragraphs:
            print(f"\n  Paragraph samples:")
            for i, p in enumerate(paragraphs[:5], 1):
                text = p.get_text(strip=True)
                print(f"    {i}. ({len(text)} chars) {text[:100]}")
        else:
            # Maybe content is in divs?
            print(f"\n  No <p> tags, checking divs...")
            divs = post_body.find_all('div', recursive=False)
            print(f"  Direct divs: {len(divs)}")
            
            for i, div in enumerate(divs[:5], 1):
                text = div.get_text(strip=True)
                if len(text) > 20:
                    print(f"    {i}. ({len(text)} chars) {text[:100]}")

# Test another URL - maybe cricket article
print("\n\n" + "="*80)
print("Testing Cricket Article")
print("="*80 + "\n")

url2 = "https://www.gossiplankanews.com/2026/02/t20-world-cup-pakistan-defeated-by.html"
response2 = requests.get(url2, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

print(f"Testing: {url2}")
print(f"Status: {response2.status_code}\n")

if response2.status_code == 200:
    soup2 = BeautifulSoup(response2.content, 'lxml')
    
    post_body2 = soup2.select_one('.post-body')
    if post_body2:
        paragraphs2 = post_body2.select('p')
        full_text2 = post_body2.get_text(strip=True)
        
        print(f"<p> tags: {len(paragraphs2)}")
        print(f"Full text length: {len(full_text2)} chars")
        
        if len(full_text2) > 100:
            print(f"Preview: {full_text2[:300]}")
