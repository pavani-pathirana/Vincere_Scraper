import requests
from bs4 import BeautifulSoup
import time

base_url = 'https://www.bbc.com/sinhala/topics/c83plvepnq1t'

print("Investigating BBC Sinhala pagination...\n")

# Test if there's pagination in the URL
test_urls = [
    base_url,
    f"{base_url}?page=1",
    f"{base_url}?page=2",
    f"{base_url}/page/1",
    f"{base_url}/page/2",
]

for url in test_urls:
    try:
        print(f"\nTesting: {url}")
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Count article links
            article_links = soup.select('[href*="/sinhala/articles/"]')
            unique_articles = set(a.get('href') for a in article_links if a.get('href'))
            print(f"Articles found: {len(unique_articles)}")
            
            # Look for pagination indicators
            pagination = soup.select('a[rel="next"], button[aria-label*="next"], [class*="pagination"], [class*="load-more"], [data-testid*="pagination"]')
            if pagination:
                print(f"Pagination elements found: {len(pagination)}")
                for elem in pagination[:3]:
                    print(f"  - {elem.name}: {elem.get('class')} - {elem.get_text(strip=True)[:50]}")
            
            # Check for infinite scroll indicators
            lazy_load = soup.select('[data-testid*="promo"], [data-testid*="skeleton"], script[type="application/json"]')
            print(f"Lazy load indicators: {len(lazy_load)}")
            
            # Sample first few article URLs
            if unique_articles:
                print("\nFirst 3 articles:")
                for i, article_url in enumerate(list(unique_articles)[:3], 1):
                    print(f"  {i}. {article_url}")
                    
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(1)

print("\n" + "="*60)
print("Checking homepage for more articles...")
print("="*60)

try:
    homepage = 'https://www.bbc.com/sinhala'
    response = requests.get(homepage, timeout=10)
    soup = BeautifulSoup(response.content, 'lxml')
    
    article_links = soup.select('[href*="/sinhala/articles/"]')
    unique_articles = set(a.get('href') for a in article_links if a.get('href'))
    print(f"\nHomepage articles: {len(unique_articles)}")
    
    # Check for topic/category pagination
    all_links = soup.select('a[href]')
    topic_pages = [a.get('href') for a in all_links if '/sinhala/topics/' in a.get('href', '')]
    print(f"Topic pages found: {len(set(topic_pages))}")
    
except Exception as e:
    print(f"Error checking homepage: {e}")
