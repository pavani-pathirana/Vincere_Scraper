"""
Test AdaDerana category pages vs homepage
"""
import requests
from bs4 import BeautifulSoup
import re

urls = {
    'Homepage': 'https://sinhala.adaderana.lk/',
    'Hot News': 'https://sinhala.adaderana.lk/sinhala-hot-news.php',
    'Category ID=5 (local)': 'https://sinhala.adaderana.lk/news.php?id=5',
    'Category ID=2 (sports)': 'https://sinhala.adaderana.lk/news.php?id=2',
}

def count_articles(url):
    response = requests.get(url, timeout=30, headers={
        'User-Agent': 'Mozilla/5.0'
    })
    soup = BeautifulSoup(response.content, 'lxml')
    all_links = soup.select('a[href]')
    
    # Count articles with different patterns
    patterns = {
        'news/XXXXXX': lambda h: re.search(r'^news/\d+', h),  # relative
        '/news/XXXXXX': lambda h: re.search(r'^/news/\d+', h),  # absolute
        'news.php?nid=': lambda h: 'news.php?nid=' in h,
    }
    
    results = {}
    for name, checker in patterns.items():
        matches = set([link.get('href', '') for link in all_links if checker(link.get('href', ''))])
        results[name] = len(matches)
    
    return results, soup

print("=" * 70)
print("TESTING DIFFERENT PAGES")
print("=" * 70)

for name, url in urls.items():
    print(f"\n{name}:")
    print(f"  URL: {url}")
    try:
        results, soup = count_articles(url)
        print(f"  Articles found:")
        for pattern, count in results.items():
            if count > 0:
                print(f"    {pattern}: {count} articles")
        
        # Check for pagination
        next_link = soup.select_one('a[href*="page="]')
        if next_link:
            print(f"  ✓ Pagination available: {next_link.get('href', '')}")
        else:
            print(f"  ✗ No pagination found")
            
    except Exception as e:
        print(f"  ERROR: {e}")

# Test pagination on category page
print("\n" + "=" * 70)
print("TESTING PAGINATION")
print("=" * 70)

test_url = 'https://sinhala.adaderana.lk/news.php?id=2&page=2'
print(f"Testing: {test_url}")

try:
    response = requests.get(test_url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.content, 'lxml')
    all_links = soup.select('a[href]')
    
    article_links = [link.get('href', '') for link in all_links if re.search(r'news/\d+|news\.php\?nid=', link.get('href', ''))]
    article_links = list(set(article_links))
    
    print(f"Status: {response.status_code}")
    print(f"Articles found: {len(article_links)}")
    if article_links:
        print(f"Sample:")
        for href in article_links[:5]:
            print(f"  {href}")
except Exception as e:
    print(f"ERROR: {e}")
