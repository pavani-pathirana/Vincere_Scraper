"""
AdaLkScraper - Concrete scraper for Ada.lk news website.

Website: https://www.ada.lk
Pattern: Category-based navigation with simple structure
"""

import logging
import re
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from core.base_scraper import BaseScraper, ArticleMetadata, Article


logger = logging.getLogger(__name__)


class AdaLkScraper(BaseScraper):
    """
    Scraper for Ada.lk (www.ada.lk) - Sinhala news website.
    
    Simple structure:
    - Category URLs: /{category-name}/{id}
    - Article listing via links on category pages
    - Content in paragraph tags
    """
    
    BASE_URL = 'https://www.ada.lk'
    
    # Categories from navigation
    CATEGORIES = {
        'latest': {
            'slug': 'latest-news',
            'id': '11',
            'name': 'නවතම පුවත්'
        },
        'international': {
            'slug': 'international',
            'id': '3',
            'name': 'විදේශීය'
        },
        'sports': {
            'slug': 'sports',
            'id': '9',
            'name': 'ක්‍රීඩා'
        },
        'business': {
            'slug': 'business',
            'id': '7',
            'name': 'ව්‍යාපාර'
        },
        'technology': {
            'slug': 'technology',
            'id': '5',
            'name': 'තාක්ෂණය'
        },
        'opinion': {
            'slug': 'opinion',
            'id': '2',
            'name': 'මතය'
        },
        'women': {
            'slug': 'woman',
            'id': '6',
            'name': 'කාන්තා'
        },
        'religion': {
            'slug': 'religion',
            'id': '4',
            'name': 'ආගම'
        },
        'saaravita': {
            'slug': 'saaravita',
            'id': '8',
            'name': 'සාරවිට - විනෝදාංශ'
        }
    }
    
    def get_category_urls(self) -> Dict[str, str]:
        """
        Get mapping of category names to their URLs.
        
        Returns:
            Dict mapping category_name → category_url
        """
        category_urls = {}
        
        for category_key, category_info in self.CATEGORIES.items():
            slug = category_info['slug']
            cat_id = category_info['id']
            url = f"{self.BASE_URL}/{slug}/{cat_id}"
            category_urls[category_key] = url
        
        logger.info(f"Ada.lk: Found {len(category_urls)} categories")
        return category_urls
    
    def get_article_list_url(self, category_url: str, page: int) -> str:
        """
        Get the URL for a specific page of articles in a category.
        
        Ada.lk pagination uses offset: /{category}/{id}/{offset}
        Offset increases by 30 per page (0, 30, 60, 90...)
        
        Args:
            category_url: Base URL for category
            page: Page number (1-indexed)
        
        Returns:
            Category URL with offset
        """
        if page == 1:
            return category_url
        
        # Calculate offset (30 per page, starting from 30 for page 2)
        offset = (page - 1) * 30
        return f"{category_url}/{offset}"
    
    def parse_article_list_page(self, html: str, category: str) -> List[ArticleMetadata]:
        """
        Parse article list page and extract article metadata.
        
        Ada.lk structure:
        - Article links in <a> tags with href matching category pattern
        - Pattern: /{category}/{sinhala-slug}/{id}-{article_id}
        - Headlines in link text        
        Args:
            html: Raw HTML content
            category: Category name
        
        Returns:
            List of ArticleMetadata objects
        """
        soup = BeautifulSoup(html, 'lxml')
        articles = []
        
        # Find all links
        links = soup.select('a[href]')
        
        # Filter for article links (contain category name and ID pattern)
        seen_urls = set()
        
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Article links have format: /category/slug/id-article_id
            # Skip navigation links (just /category/id)
            if href and self.BASE_URL in href:
                # Check if it's an article (has slug and long URL)
                path_parts = href.replace(self.BASE_URL, '').split('/')
                
                # Article URLs have at least 4 parts: '', category, slug, id-article_id
                if len(path_parts) >= 4 and text and len(text) > 10:
                    # Avoid duplicates
                    if href in seen_urls:
                        continue
                    seen_urls.add(href)
                    
                    # Check if last part looks like an article ID (contains hyphen and numbers)
                    last_part = path_parts[-1]
                    if '-' in last_part and any(c.isdigit() for c in last_part):
                        article_metadata = ArticleMetadata(
                            url=href,
                            headline=text,
                            category=category
                        )
                        articles.append(article_metadata)
        
        logger.info(f"Ada.lk {category}: Extracted {len(articles)} articles from list page")
        return articles
    
    def parse_article_page(self, html: str, metadata: ArticleMetadata) -> Article:
        """
        Parse individual article page.
        
        Ada.lk article structure:
        - Headline: <h1>
        - Content: Multiple <p> tags (filter by length)
        - No specific article container
        
        Args:
            html: Raw HTML of article page
            metadata: Article metadata from list page
        
        Returns:
            Article object with full content
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # Extract headline
        headline = metadata.headline
        headline_elem = soup.select_one('h1')
        if headline_elem:
            headline = headline_elem.get_text(strip=True)
        
        # Extract paragraphs
        paragraphs = soup.select('p')
        
        body_parts = []
        for p in paragraphs:
            text = p.get_text(strip=True)
            # Filter out navigation, forms, and very short text
            if len(text) > 50:  # Meaningful paragraph threshold
                body_parts.append(text)
        
        body = '\n\n'.join(body_parts)
        
        if not body or len(body) < 100:
            raise ValueError(f"Insufficient content for {metadata.url}")
        
        # Extract date (try to find in page)
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        # Try various date selectors
        date_elem = soup.select_one('time, .date, .publish-date, [class*="date"]')
        if date_elem:
            date_text = date_elem.get('datetime') or date_elem.get_text(strip=True)
            # Try to extract date
            try:
                date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_text)
                if date_match:
                    date_str = date_match.group(0)
            except:
                pass
        
        # Author (if available)
        author = None
        author_elem = soup.select_one('.author, .by-line, [class*="author"]')
        if author_elem:
            author = author_elem.get_text(strip=True)
        
        # Create Article object
        article = Article(
            headline=headline,
            body=body,
            url=metadata.url,
            category=metadata.category,
            date=date_str,
            author=author,
            source='ada_lk',
            extraction_timestamp=datetime.now().isoformat()
        )
        
        return article
    
    def get_next_page_url(self, current_url: str, html: str, current_page: int) -> Optional[str]:
        """
        Get URL for the next page.
        
        Ada.lk has pagination with "Next" link or offset-based URLs.
        
        Args:
            current_url: Current page URL
            html: Current page HTML
            current_page: Current page number (1-indexed)
        
        Returns:
            URL for next page, or None if on last page
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # Look for "Next" link in pagination
        next_link = soup.select_one('.pagination a.page-numbers[href], a.next.page-numbers[href]')
        if next_link:
            href = next_link.get('href')
            text = next_link.get_text(strip=True).lower()
            
            # Check if it's actually a "next" link (not a number)
            if 'next' in text or not text.isdigit():
                if href and href.startswith('http'):
                    return href
                elif href:
                    return urljoin(self.BASE_URL, href)
        
        # Fallback: check if there are articles (if none, no next page)
        # Get article links to verify content exists
        links = soup.select('a[href]')
        article_count = 0
        for link in links:
            href = link.get('href', '')
            if self.BASE_URL in href and '-' in href:
                article_count += 1
        
        # If we found fewer than 10 articles, probably last page
        if article_count < 10:
            return None
        
        # Generate next page URL with offset
        next_page = current_page + 1
        offset = (next_page - 1) * 30
        
        # Extract base URL (remove offset if present)
        base_url = current_url.split('/')[:-1] if current_url.endswith(tuple('0123456789')) else current_url.split('/')
        base_url = '/'.join([p for p in base_url if p])  # Remove empty parts
        
        return f"{base_url}/{offset}"
