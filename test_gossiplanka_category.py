import requests
from bs4 import BeautifulSoup

url = "https://www.gossiplanka.com/search/label/entertainment"

response = requests.get(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

print(f"Status: {response.status_code}\n")

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'lxml')
    
    # Check posts
    posts = soup.select('.post')
    print(f"Posts found: {len(posts)}\n")
    
    # Check for load more button
    load_more = soup.select_one('.load-more[data-load], .blog-pager-older-link[data-load], #load-more-link[data-load]')
    if load_more:
        print(f"Load more button found!")
        print(f"data-load: {load_more.get('data-load')}\n")
    else:
        print("No load more button with data-load found\n")
    
    # Check for any load more or pagination elements
    pagers = soup.select('.blog-pager, .pagination, [class*="pag"]')
    print(f"Pagination elements: {len(pagers)}")
    for elem in pagers:
        print(f"  {elem.name}: {elem.get('class')}")
        print(f"  {elem.get_text(strip=True)[:100]}")
        
        # Check children
        for child in elem.find_all(['a', 'button']):
            href = child.get('href', 'N/A')
            data_load = child.get('data-load', 'N/A')
            text = child.get_text(strip=True)
            print(f"    {child.name}: href={href[:50] if href != 'N/A' else 'N/A'}, data-load={data_load[:50] if data_load != 'N/A' else 'N/A'}, text={text}")
        print()
