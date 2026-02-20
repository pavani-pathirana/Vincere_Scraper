import requests
from bs4 import BeautifulSoup

# Check both page 1 and page 2
for page_num in [1, 2]:
    if page_num == 1:
        url = "https://www.pcguide.lk/category/tech-news/"
    else:
        url = f"https://www.pcguide.lk/category/tech-news/page/{page_num}/"
    
    print(f"\n{'='*70}")
    print(f"PAGE {page_num}: {url}")
    print(f"{'='*70}")
    
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    
    # Count articles
    h2_links = soup.select('h2 a, h3 a')
    print(f"Articles found (h2/h3 links): {len(h2_links)}")
    
    # Look for any numeric links (2, 3, 4, etc.)
    all_links = soup.find_all('a', href=True)
    numeric_links = [l for l in all_links if l.get_text(strip=True).isdigit()]
    if numeric_links:
        print(f"\nNumeric pagination links found: {len(numeric_links)}")
        for link in numeric_links[:5]:
            print(f"  Text: '{link.get_text()}' → {link.get('href')}")
    
    # Look for prev/next text
    nav_texts = ['next', 'prev', 'previous', '›', '‹', '»', '«']
    for text in nav_texts:
        links = [l for l in all_links if text in l.get_text().lower()]
        if links:
            print(f"\n'{text}' links found:")
            for link in links[:3]:
                print(f"  {link.get('href')} - '{link.get_text(strip=True)}'")
