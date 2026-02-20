"""
Check URLs on Asian Mirror political page 2
"""

import requests
from bs4 import BeautifulSoup

for page_num in [2, 3, 5, 10]:
    url = f'https://sinhala.asianmirror.lk/news/political/page/{page_num}/'
    
    print(f"\n{'='*70}")
    print(f"PAGE {page_num}: {url}")
    print('='*70)
    
    r = requests.get(url, timeout=10)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, 'lxml')
    
    # Find article links
    article_links = soup.select('li.listitem a')
    
    print(f"Found {len(article_links)} links")
    
    # Categorize by URL pattern
    breaking = []
    political = []
    other = []
    
    for link in article_links:
        href = link.get('href', '')
        text = link.get_text(strip=True)
        
        if '/news/' not in href or href.count('/') < 6:
            continue
            
        if '/breaking/' in href:
            breaking.append((text, href))
        elif '/political/' in href:
            political.append((text, href))
        else:
            other.append((text, href))
    
    print(f"  - /news/breaking/: {len(breaking)}")
    print(f"  - /news/political/: {len(political)}")
    print(f"  - Other: {len(other)}")
    
    if political:
        print("\nPolitical articles:")
        for text, href in political[:5]:
            print(f"  • {text}")
            print(f"    {href}")
