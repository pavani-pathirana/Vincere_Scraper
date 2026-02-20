"""Test a technews.lk article page"""
import requests
from bs4 import BeautifulSoup

url = 'https://technews.lk/cafe-cursor-is-coming-to-colombo/'
print(f"Testing article: {url}")
r = requests.get(url, timeout=10)
soup = BeautifulSoup(r.text, 'lxml')

# Find title
title = soup.select_one('h1, .post-title, .article-title')
if title:
    print(f"\nTitle: {title.get_text(strip=True)}")

# Find content
print("\nTrying content selectors:")
selectors = ['.post-content', '.article-content', 'article .content', 
             '.gh-content', '.post-full-content']
for sel in selectors:
    elem = soup.select_one(sel)
    if elem:
        text = elem.get_text(strip=True)
        print(f"  {sel}: Found! ({len(text)} chars)")
        if len(text) > 100:
            print(f"    First 150 chars: {text[:150]}...")

# Check for paragraphs
paragraphs = soup.select('article p, .post-content p, .gh-content p')
print(f"\nParagraphs found: {len(paragraphs)}")
if paragraphs:
    for i, p in enumerate(paragraphs[:3], 1):
        text = p.get_text(strip=True)
        if len(text) > 30:
            print(f"  P{i}: {text[:100]}...")

# Find date
print("\nDate elements:")
for sel in ['time', '.post-date', '.published', '.date']:
    elem = soup.select_one(sel)
    if elem:
        print(f"  {sel}: {elem.get_text(strip=True)}")
        if elem.get('datetime'):
            print(f"    datetime: {elem.get('datetime')}")

# Find category/tags
print("\nCategories/Tags:")
tags = soup.select('.tag, .category, .post-tag')
for tag in tags[:5]:
    print(f"  {tag.get_text(strip=True)}")
