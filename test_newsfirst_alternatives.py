"""
Test alternative NewsFirst pagination methods
"""
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

def get_article_count(url):
    response = requests.get(url, timeout=30, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    soup = BeautifulSoup(response.content, 'lxml')
    all_links = soup.select('a[href]')
    date_pattern = re.compile(r'sinhala/\d{4}/\d{2}/\d{2}/')
    article_urls = set([link.get('href', '') for link in all_links if date_pattern.search(link.get('href', ''))])
    return len(article_urls)

print("Testing different pagination patterns:\n")

# Test 1: Standard WordPress pagination patterns
patterns = [
    ("Query param ?page=", "https://www.newsfirst.lk/sinhala/sports/?page=2"),
    ("Query param ?paged=", "https://www.newsfirst.lk/sinhala/sports/?paged=2"),
    ("Path /page/2/", "https://www.newsfirst.lk/sinhala/sports/page/2/"),
    ("Path /page/2", "https://www.newsfirst.lk/sinhala/sports/page/2"),
]

baseline = get_article_count("https://www.newsfirst.lk/sinhala/sports/")
print(f"Baseline (page 1): {baseline} articles\n")

for name, url in patterns:
    try:
        count = get_article_count(url)
        status = "✓ WORKS!" if count != baseline else "✗ Same as page 1"
        print(f"{name:25s} {count} articles - {status}")
    except Exception as e:
        print(f"{name:25s} ERROR: {e}")

# Test 2: Date-based archives
print("\n" + "=" * 70)
print("Testing date-based archives:")
print("=" * 70)

# Try different date formats
date_patterns = [
    "https://www.newsfirst.lk/sinhala/sports/2026/02/",
    "https://www.newsfirst.lk/sinhala/sports/2026/01/",
    "https://www.newsfirst.lk/sinhala/sports/2025/12/",
    "https://www.newsfirst.lk/sinhala/2026/02/",
]

for url in date_patterns:
    try:
        response = requests.get(url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
        print(f"\n{url}")
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            count = len(re.findall(r'sinhala/\d{4}/\d{2}/\d{2}/', response.text))
            print(f"  Articles found: {count}")
    except Exception as e:
        print(f"  ERROR: {e}")

# Test 3: Check HTML for actual pagination links
print("\n" + "=" * 70)
print("Looking for pagination links in page source:")
print("=" * 70)

response = requests.get("https://www.newsfirst.lk/sinhala/sports/", timeout=30, headers={
    'User-Agent': 'Mozilla/5.0'
})
soup = BeautifulSoup(response.content, 'lxml')

# Look for any links that might be pagination
possible_pagination = []
for link in soup.find_all('a', href=True):
    href = link.get('href', '')
    text = link.get_text(strip=True)  
    if any(keyword in href.lower() for keyword in ['page', 'next', 'more', 'load']) or \
       any(keyword in text.lower() for keyword in ['next', 'more', 'මීළඟ', 'load']):
        possible_pagination.append((text, href))

if possible_pagination:
    print("Found potential pagination links:")
    for text, href in possible_pagination[:10]:
        print(f"  Text: '{text}' -> {href}")
else:
    print("No pagination links found in HTML")

# Test 4: Look for API endpoints in page source
print("\n" + "=" * 70)
print("Looking for API endpoints:")
print("=" * 70)

# Check for API calls in scripts
api_patterns = [
    r'api[\'"]?\s*:\s*[\'"]([^\'"]+)',
    r'endpoint[\'"]?\s*:\s*[\'"]([^\'"]+)',
    r'https://[^\'"]+/api/[^\'"]+',
]

for pattern in api_patterns:
    matches = re.findall(pattern, response.text)
    if matches:
        print(f"Pattern '{pattern}':")
        for match in set(matches[:5]):
            print(f"  - {match}")
