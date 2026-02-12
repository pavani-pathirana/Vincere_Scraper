"""
Test how deep Lankadeepa business archive goes
"""
import requests
from bs4 import BeautifulSoup
import re

def test_page(page_num):
    url = f'https://www.lankadeepa.lk/business?page={page_num}'
    try:
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0'
        })
        
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Count business article links
        pattern = re.compile(r'/business/[^/]+/\d+-\d+')
        count = 0
        dates = []
        
        for link in soup.select('a[href]'):
            href = link.get('href', '')
            if pattern.search(href):
                count += 1
                # Try to extract date from article if visible
                date_elem = link.find_parent().find_all('time') if link.find_parent() else []
                for d in date_elem:
                    date_text = d.get_text(strip=True)
                    if date_text:
                        dates.append(date_text)
        
        return {
            'articles': count,
            'dates': dates[:3]  # First 3 dates
        }
    except Exception as e:
        return None

# Test strategic page numbers
test_pages = [1, 10, 50, 100, 200, 500, 1000]

print("Testing Lankadeepa business archive depth:")
print("="*60)

for page in test_pages:
    result = test_page(page)
    if result:
        status = f"✓ Page {page:4d}: {result['articles']} articles"
        if result['dates']:
            status += f" | Dates: {', '.join(result['dates'])}"
        print(status)
    else:
        print(f"✗ Page {page:4d}: No content or error")
        # If this page fails, likely end of archive
        break

print("\nConclusion: Archive appears to have", end=" ")
if result and result['articles'] > 0:
    print(f"at least {page * 13} articles")
else:
    print(f"approximately {page * 13} articles")
