"""Test Gagana's Load More button mechanism"""
import requests
from bs4 import BeautifulSoup
import re

# First, get the category page
url = "https://gagana.lk/news/politics"
response = requests.get(url, timeout=15)
soup = BeautifulSoup(response.text, 'lxml')

print("=== Page 1 Articles ===")
page1_posts = soup.select('.a-item')
print(f"Total posts: {len(page1_posts)}")

# Get first 3 article titles and URLs
page1_articles = []
for i, post in enumerate(page1_posts[:5]):
    link = post.select_one('a[href*="/article/"]')
    if link:
        title = link.get_text(strip=True)[:60]
        url = link.get('href')
        page1_articles.append((title, url))
        print(f"{i+1}. {title}")
        print(f"   {url}")

print("\n=== Testing ?page=2 ===")
url2 = "https://gagana.lk/news/politics?page=2"
response2 = requests.get(url2, timeout=15)
soup2 = BeautifulSoup(response2.text, 'lxml')

page2_posts = soup2.select('.a-item')
print(f"Total posts: {len(page2_posts)}")

# Get first 3 article titles
page2_articles = []
for i, post in enumerate(page2_posts[:5]):
    link = post.select_one('a[href*="/article/"]')
    if link:
        title = link.get_text(strip=True)[:60]
        url = link.get('href')
        page2_articles.append((title, url))
        print(f"{i+1}. {title}")
        print(f"   {url}")

# Compare
print("\n=== Comparison ===")
page1_urls = {url for _, url in page1_articles}
page2_urls = {url for _, url in page2_articles}

common = page1_urls & page2_urls
print(f"Articles in both pages: {len(common)}")
print(f"Unique to page 1: {len(page1_urls - page2_urls)}")
print(f"Unique to page 2: {len(page2_urls - page1_urls)}")

if len(page2_urls - page1_urls) > 0:
    print("\n✓ PAGINATION WORKS - Different articles on page 2!")
else:
    print("\n✗ Same articles on both pages")

# Try higher page numbers
print("\n=== Testing ?page=3 ===")
url3 = "https://gagana.lk/news/politics?page=3"
response3 = requests.get(url3, timeout=15)
soup3 = BeautifulSoup(response3.text, 'lxml')
page3_posts = soup3.select('.a-item')
print(f"Total posts: {len(page3_posts)}")
if len(page3_posts) > 0:
    link = page3_posts[0].select_one('a[href*="/article/"]')
    if link:
        print(f"First article: {link.get_text(strip=True)[:60]}")

# Check for an API endpoint by looking at browser console/network
print("\n=== Looking for data-* attributes ===")
container = soup.select_one('.lsb-sec-items')
if container:
    print(f"Container attributes: {container.attrs}")

load_more = soup.select_one('.loadMore')
if load_more:
    print(f"Load More button attributes: {load_more.attrs}")
