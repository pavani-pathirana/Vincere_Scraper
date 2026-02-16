"""Verify if timestamp-based pagination works"""
import requests
from bs4 import BeautifulSoup

category = "politics"

# Get page 1
print("=== Page 1 ===")
response1 = requests.get(f"https://gagana.lk/news/{category}", timeout=15)
soup1 = BeautifulSoup(response1.text, 'lxml')
page1_posts = soup1.select('.a-item')

page1_urls = []
for post in page1_posts:
    link = post.select_one('a[href*="/article/"]')
    if link:
        page1_urls.append(link.get('href'))

print(f"Page 1: {len(page1_urls)} articles")
print(f"First: {page1_urls[0] if page1_urls else 'none'}")
print(f"Last:  {page1_urls[-1] if page1_urls else 'none'}")

# Extract last article timestamp
import re
if page1_urls:
    match = re.search(r'-(\d+)$', page1_urls[-1])
    if match:
        last_timestamp = match.group(1)
        print(f"Last timestamp: {last_timestamp}")
        
        # Try loading with ?before=timestamp
        print(f"\n=== Using ?before={last_timestamp} ===")
        response2 = requests.get(f"https://gagana.lk/news/{category}?before={last_timestamp}", timeout=15)
        soup2 = BeautifulSoup(response2.text, 'lxml')
        page2_posts = soup2.select('.a-item')
        
        page2_urls = []
        for post in page2_posts:
            link = post.select_one('a[href*="/article/"]')
            if link:
                page2_urls.append(link.get('href'))
        
        print(f"Page 2: {len(page2_urls)} articles")
        print(f"First: {page2_urls[0] if page2_urls else 'none'}")
        print(f"Last:  {page2_urls[-1] if page2_urls else 'none'}")
        
        # Check overlap
        page1_set = set(page1_urls)
        page2_set = set(page2_urls)
        common = page1_set & page2_set
        
        print(f"\n=== Analysis ===")
        print(f"Common articles: {len(common)}")
        print(f"Unique to page 1: {len(page1_set - page2_set)}")
        print(f"Unique to page 2: {len(page2_set - page1_set)}")
        
        if len(page2_set - page1_set) > 0:
            print("\n✓ SUCCESS! ?before= parameter works!")
            print("\nSample unique articles from page 2:")
            for url in list(page2_set - page1_set)[:5]:
                print(f"  {url}")
        else:
            print("\n✗ Same articles returned")
            
        # If ?before= doesn't work, try getting more articles by going back in time
        if len(page2_set - page1_set) == 0:
            print(f"\n=== Trying older timestamp ===")
            # Try with an even older timestamp
            older_timestamp = str(int(last_timestamp) - 100000)
            print(f"Using timestamp: {older_timestamp}")
            response3 = requests.get(f"https://gagana.lk/news/{category}?before={older_timestamp}", timeout=15)
            soup3 = BeautifulSoup(response3.text, 'lxml')
            page3_posts = soup3.select('.a-item')
            
            page3_urls = []
            for post in page3_posts:
                link = post.select_one('a[href*="/article/"]')
                if link:
                    page3_urls.append(link.get('href'))
            
            print(f"Results: {len(page3_urls)} articles")
            if page3_urls:
                print(f"First: {page3_urls[0]}")
                print(f"Last:  {page3_urls[-1]}")
                
                page3_set = set(page3_urls)
                if len(page3_set - page1_set) > 0:
                    print(f"\n✓ Found {len(page3_set - page1_set)} different articles!")
