import requests
from bs4 import BeautifulSoup

# Test potential category URLs for sports, world, and entertainment
base_url = 'https://www.silumina.lk'

potential_slugs = {
    'sports': ['sports', 'sport', 'ක්‍රීඩා', 'khela', 'krida'],
    'world': ['world', 'international', 'විදේශ', 'jaathika', 'videsa'],
    'entertainment': ['entertainment', 'විනෝදාස්වාදය', 'vinodaya', 'film', 'movies']
}

print("Investigating Silumina categories...\n")

# First, let's check the main page to see the menu
print("Checking main page navigation...")
try:
    response = requests.get(base_url, timeout=10)
    soup = BeautifulSoup(response.content, 'lxml')
    
    # Find navigation menu
    nav_links = soup.select('nav a, .menu a, header a')
    
    print(f"Found {len(nav_links)} navigation links\n")
    
    categories_found = {}
    
    for link in nav_links:
        href = link.get('href', '')
        text = link.get_text(strip=True)
        
        if '/category/' in href:
            print(f"Category: {text} → {href}")
            categories_found[text] = href
    
    print("\n" + "="*60)
    print("Testing specific category URLs:")
    print("="*60 + "\n")
    
    # Test each potential slug
    for category, slugs in potential_slugs.items():
        print(f"\n{category.upper()}:")
        for slug in slugs:
            url = f"{base_url}/category/{slug}/"
            try:
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    test_soup = BeautifulSoup(resp.content, 'lxml')
                    articles = test_soup.select('article')
                    print(f"  ✓ {slug}: {resp.status_code} - {len(articles)} articles found")
                    
                    # Get page title
                    title = test_soup.select_one('h1, .page-title, title')
                    if title:
                        print(f"    Title: {title.get_text(strip=True)[:100]}")
                else:
                    print(f"  ✗ {slug}: {resp.status_code}")
            except Exception as e:
                print(f"  ✗ {slug}: Error - {str(e)[:50]}")
                
except Exception as e:
    print(f"Error accessing main page: {e}")
