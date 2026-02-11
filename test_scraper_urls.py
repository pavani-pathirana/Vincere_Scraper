"""
URL Verification Utility for Vincere Scrapers

Tests scraper URL patterns against actual websites to verify they work
before running full scrapes.

Usage:
    python test_scraper_urls.py --site itn
    python test_scraper_urls.py --site all
"""

import argparse
import sys
from typing import Dict

from core.session_manager import SessionManager

# Import scrapers
from scrapers.adaderana_scraper import AdaDeranaScraper
from scrapers.hirunews_scraper import HiruNewsScraper
from scrapers.itn_scraper import ITNScraper
from scrapers.newsfirst_scraper import NewsFirstScraper
from scrapers.lankatruth_scraper import LankaTruthScraper


def test_scraper_urls(scraper_class, site_name: str):
    """
    Test URL patterns for a specific scraper.
    
    Args:
        scraper_class: Scraper class to test
        site_name: Name of the site
    """
    print(f"\n{'='*70}")
    print(f"  Testing: {site_name.upper()}")
    print(f"{'='*70}\n")
    
    # Create temporary scraper instance (no state/file writing needed)
    scraper = scraper_class.__new__(scraper_class)
    
    # Get category URLs
    try:
        categories = scraper.get_category_urls()
        print(f"✓ Found {len(categories)} categories\n")
    except Exception as e:
        print(f"✗ Failed to get categories: {e}\n")
        return
    
    # Initialize session manager for testing
    session_mgr = SessionManager(requests_per_minute=10)
    
    # Test each category URL
    results = {
        'accessible': [],
        'not_found': [],
        'errors': []
    }
    
    for cat_name, cat_url in categories.items():
        try:
            print(f"Testing: {cat_name}")
            print(f"  URL: {cat_url}")
            
            # Try to fetch the URL
            response = session_mgr.get(cat_url, timeout=10)
            
            if response.status_code == 200:
                print(f"  ✓ Status: 200 OK (Page size: {len(response.content)} bytes)")
                results['accessible'].append((cat_name, cat_url))
            elif response.status_code == 404:
                print(f"  ✗ Status: 404 Not Found")
                results['not_found'].append((cat_name, cat_url))
            else:
                print(f"  ⚠ Status: {response.status_code}")
                results['errors'].append((cat_name, cat_url, response.status_code))
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results['errors'].append((cat_name, cat_url, str(e)))
        
        print()
    
    # Print summary
    print(f"{'='*70}")
    print(f"  SUMMARY: {site_name.upper()}")
    print(f"{'='*70}\n")
    
    print(f"✓ Accessible:  {len(results['accessible'])}/{len(categories)}")
    print(f"✗ Not Found:   {len(results['not_found'])}/{len(categories)}")
    print(f"⚠ Errors:      {len(results['errors'])}/{len(categories)}\n")
    
    if results['not_found']:
        print("❌ URLs returning 404 (need fixing):")
        for cat_name, cat_url in results['not_found']:
            print(f"  - {cat_name}: {cat_url}")
        print()
    
    if results['errors']:
        print("⚠️  URLs with errors:")
        for item in results['errors']:
            if len(item) == 3:
                cat_name, cat_url, error = item
                print(f"  - {cat_name}: {error}")
        print()
    
    # Cleanup
    session_mgr.close()
    
    return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Test scraper URL patterns',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test single scraper
  python test_scraper_urls.py --site itn
  
  # Test all scrapers
  python test_scraper_urls.py --site all
        """
    )
    
    parser.add_argument(
        '--site',
        type=str,
        required=True,
        help='Site to test (adaderana, hirunews, itn, newsfirst, lankatruth, or "all")'
    )
    
    args = parser.parse_args()
    
    # Scraper registry
    scrapers = {
        'adaderana': AdaDeranaScraper,
        'hirunews': HiruNewsScraper,
        'itn': ITNScraper,
        'newsfirst': NewsFirstScraper,
        'lankatruth': LankaTruthScraper,
    }
    
    print("\n" + "="*70)
    print("  VINCERE URL VERIFICATION UTILITY")
    print("="*70)
    
    # Test requested scrapers
    if args.site.lower() == 'all':
        sites_to_test = scrapers.keys()
    else:
        if args.site.lower() not in scrapers:
            print(f"\n✗ Error: Unknown site '{args.site}'")
            print(f"Available: {', '.join(scrapers.keys())}")
            sys.exit(1)
        sites_to_test = [args.site.lower()]
    
    # Run tests
    all_results = {}
    for site_name in sites_to_test:
        scraper_class = scrapers[site_name]
        results = test_scraper_urls(scraper_class, site_name)
        all_results[site_name] = results
    
    # Final summary
    print("\n" + "="*70)
    print("  FINAL SUMMARY")
    print("="*70 + "\n")
    
    total_categories = 0
    total_working = 0
    total_broken = 0
    
    for site_name, results in all_results.items():
        working = len(results['accessible'])
        broken = len(results['not_found']) + len(results['errors'])
        total = working + broken
        
        total_categories += total
        total_working += working
        total_broken += broken
        
        status = "✓" if broken == 0 else "✗"
        print(f"{status} {site_name:<15} {working}/{total} working")
    
    print(f"\n{'='*70}")
    print(f"Total: {total_working}/{total_categories} URLs working")
    print(f"{'='*70}\n")
    
    if total_broken > 0:
        print("⚠️  ACTION REQUIRED:")
        print(f"  {total_broken} URL patterns need to be fixed in the scrapers.")
        print("  Visit the websites in a browser and update the URL patterns.")
        print("  See the scraper files in scrapers/ directory.\n")
    else:
        print("✅ All URL patterns verified! Ready to scrape.\n")


if __name__ == "__main__":
    main()
