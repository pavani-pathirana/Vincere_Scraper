"""
Deep analysis of Ada.lk saaravita category
"""

import requests
from bs4 import BeautifulSoup

url = "https://www.ada.lk/saaravita/8"

print(f"Deep analysis of Ada.lk Saaravita")
print("=" * 70)

response = requests.get(url, timeout=10)
print(f"Status: {response.status_code}\n")

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'lxml')
    
    # Look for all anchor tags with href containing news-details
    all_links = soup.find_all('a', href=True)
    news_links = [link for link in all_links if 'news-details' in link.get('href', '')]
    
    print(f"Found {len(news_links)} news-details links")
    
    if news_links:
        print("\nFirst 5 article links:")
        for i, link in enumerate(news_links[:5], 1):
            href = link.get('href')
            text = link.get_text(strip=True)
            
            # Get parent container info
            parent = link.find_parent()
            parent_class = parent.get('class', []) if parent else []
            
            print(f"\n{i}. {text[:60]}")
            print(f"   URL: {href}")
            print(f"   Parent: {parent.name if parent else 'None'} - {parent_class}")
    
    # Check HTML structure
    print("\n" + "=" * 70)
    print("Container Analysis:")
    print("=" * 70)
    
    # Look for div/section containers
    containers = soup.find_all(['div', 'section'], class_=True)
    container_classes = {}
    for cont in containers:
        for cls in cont.get('class', []):
            if cls not in container_classes:
                container_classes[cls] = 0
            container_classes[cls] += 1
    
    print("\nTop 10 most common classes:")
    sorted_classes = sorted(container_classes.items(), key=lambda x: x[1], reverse=True)
    for cls, count in sorted_classes[:10]:
        print(f"  .{cls}: {count} occurrences")
    
    # Check if it's same structure as other Ada categories
    print("\n" + "=" * 70)
    print("Checking if pagination exists:")
    print("=" * 70)
    
    # Look for pagination elements
    page_links = soup.find_all('a', href=lambda x: x and '/saaravita/8/' in x)
    if page_links:
        print(f"Found {len(page_links)} pagination links:")
        for link in page_links[:5]:
            print(f"  {link.get('href')}")
    else:
        print("No pagination links found")
