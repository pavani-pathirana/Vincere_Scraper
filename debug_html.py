"""
Debug utility to inspect HTML structure of news websites.
Helps identify correct CSS selectors before updating scrapers.

Usage:
    python debug_html.py https://www.itnnews.lk/local/
"""

import sys
import requests
from bs4 import BeautifulSoup


def inspect_page(url: str):
    """
    Fetch and analyze page structure.
    
    Args:
        url: URL to inspect
    """
    print(f"\n{'='*70}")
    print(f"  Inspecting: {url}")
    print(f"{'='*70}\n")
    
    try:
        # Fetch page
        print("Fetching page...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Size: {len(response.content)} bytes\n")
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Look for common article containers
        print("="*70)
        print("  ARTICLE CONTAINERS")
        print("="*70 + "\n")
        
        containers = [
            ('article', soup.select('article')),
            ('div.post', soup.select('div.post')),
            ('div.news-item', soup.select('div.news-item')),
            ('div[class*="post"]', soup.select('div[class*="post"]')),
            ('div[class*="item"]', soup.select('div[class*="item"]')),
            ('div[class*="article"]', soup.select('div[class*="article"]')),
        ]
        
        for selector, elements in containers:
            if elements:
                print(f"✓ {selector}: {len(elements)} elements")
                if len(elements) > 0:
                    first = elements[0]
                    classes = first.get('class', [])
                    print(f"  First element classes: {classes}")
                    # Try to find link inside
                    link = first.select_one('a')
                    if link:
                        print(f"  First link href: {link.get('href', 'N/A')}")
                    print()
        
        # Look for all links with date patterns
        print("="*70)
        print("  ARTICLE LINKS (Date-based URLs)")
        print("="*70 + "\n")
        
        date_links = soup.select('a[href*="/2024/"], a[href*="/2025/"], a[href*="/2026/"]')
        print(f"Found {len(date_links)} links with date patterns\n")
        
        if date_links:
            print("First 10 article URLs:")
            for i, link in enumerate(date_links[:10], 1):
                href = link.get('href', '')
                text = link.get_text(strip=True)[:50]
                print(f"  {i}. {href}")
                print(f"     Text: {text}")
                print()
        
        # Look for all <a> tags
        print("="*70)
        print("  ALL LINKS ANALYSIS")
        print("="*70 + "\n")
        
        all_links = soup.select('a')
        print(f"Total links on page: {len(all_links)}\n")
        
        # Categorize links
        internal_links = [a for a in all_links if a.get('href', '').startswith('/')]
        external_links = [a for a in all_links if a.get('href', '').startswith('http')]
        
        print(f"Internal links (start with /): {len(internal_links)}")
        print(f"External links (start with http): {len(external_links)}\n")
        
        # Show some internal links
        if internal_links:
            print("Sample internal links:")
            for link in internal_links[:15]:
                href = link.get('href', '')
                print(f"  {href}")
            print()
        
        # Look for main content area
        print("="*70)
        print("  CONTENT AREA SELECTORS")
        print("="*70 + "\n")
        
        content_selectors = [
            ('main', soup.select_one('main')),
            ('.content', soup.select_one('.content')),
            ('#content', soup.select_one('#content')),
            ('.main-content', soup.select_one('.main-content')),
            ('.site-content', soup.select_one('.site-content')),
        ]
        
        for selector, element in content_selectors:
            if element:
                print(f"✓ Found: {selector}")
                # Count links inside
                links_inside = element.select('a')
                print(f"  Links inside: {len(links_inside)}")
                print()
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Error fetching page: {e}")
        sys.exit(1)
    
    except Exception as e:
        print(f"✗ Error parsing page: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_html.py <url>")
        print("\nExamples:")
        print("  python debug_html.py https://www.itnnews.lk/local/")
        print("  python debug_html.py https://www.newsfirst.lk/sinhala/local/")
        print("  python debug_html.py https://lankatruth.com/si/news/")
        sys.exit(1)
    
    url = sys.argv[1]
    inspect_page(url)
