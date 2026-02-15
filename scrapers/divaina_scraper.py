"""
DivainaScraper - Concrete scraper for Divaina news website.

Website: https://www.divaina.lk
Pattern: Foxiz WordPress theme with category-based navigation
"""

import logging
import re
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from core.base_scraper import BaseScraper, ArticleMetadata, Article


logger = logging.getLogger(__name__)


class DivainaScraper(BaseScraper):
    """
    Scraper for Divaina (www.divaina.lk) - Major Sinhala newspaper.
    
    Uses Foxiz WordPress theme:
    - Article containers: .p-wrap elements
    - Pagination: May use AJAX (currently page 1 only)
    """
    
    BASE_URL = 'https://www.divaina.lk'
    
    # Categories found from navigation
    CATEGORIES = {
        'breaking': {
            'slug': 'breaking-news',
            'name': 'විගස පුවත්'
        },
        'main': {
            'slug': 'main-news',
            'name': 'ප්‍රධාන පුවත්'
        },
        'provincial': {
            'slug': 'provincial-news',
            'name': 'ප්‍රාදේශීය පුවත්'
        },
        'sports': {
            'slug': 'sports-news',
            'name': 'ක්‍රීඩා'
        },
        'business': {
            'slug': 'business-news',
            'name': 'ගණුදෙනු ලොව'
        },
        'foreign': {
            'slug': 'foreign-news',
            'name': 'විදෙස්'
        },
        'features': {
            'slug': 'features',
            'name': 'විශේෂාංග'
        },
        'editorial': {
            'slug': 'editorial',
            'name': 'කතුවැකි'
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
            url = f"{self.BASE_URL}/category/{slug}"
            category_urls[category_key] = url
        
        logger.info(f"Divaina: Found {len(category_urls)} categories")
        return category_urls
    
    def get_article_list_url(self, category_url: str, page: int) -> str:
        """
        Get the URL for a specific page of articles in a category.
        
        Divaina uses WordPress pagination: /page/N/
        
        Args:
            category_url: Base URL for category
            page: Page number (1-indexed)
        
        Returns:
            Category URL with page number
        """
        if page == 1:
            return category_url
        return f"{category_url}/page/{page}/"
    
    def parse_article_list_page(self, html: str, category: str) -> List[ArticleMetadata]:
        """
        Parse article list page and extract article metadata.
        
        Divaina (Foxiz theme) structure:
        - Article containers: .p-wrap elements
        - Link: Direct URL in <a> tag
        - Headline: <h2> or <h3>
        - Data attribute: data-pid for post ID
        
        Args:
            html: Raw HTML content
            category: Category name
        
        Returns:
            List of ArticleMetadata objects
        """
        soup = BeautifulSoup(html, 'lxml')
        articles = []
        
        # Find article containers (Foxiz theme uses .p-wrap)
        article_containers = soup.select('.p-wrap')
        
        if not article_containers:
            logger.warning(f"Divaina {category}: No .p-wrap containers found")
            return articles
        
        for container in article_containers:
            try:
                # Find link
                link_elem = container.select_one('a')
                if not link_elem or not link_elem.get('href'):
                    continue
                
                article_url = link_elem.get('href')
                
                # Make absolute URL
                if not article_url.startswith('http'):
                    article_url = urljoin(self.BASE_URL, article_url)
                
                # Find headline
                headline_elem = container.select_one('h2, h3, .entry-title')
                if not headline_elem:
                    continue
                
                headline = headline_elem.get_text(strip=True)
                
                # Create metadata
                article_metadata = ArticleMetadata(
                    url=article_url,
                    headline=headline,
                    category=category
                )
                
                articles.append(article_metadata)
                
            except Exception as e:
                logger.warning(f"Divaina {category}: Error parsing article container: {e}")
                continue
        
        logger.info(f"Divaina {category}: Extracted {len(articles)} articles from list page")
        return articles
    
    def parse_article_page(self, html: str, metadata: ArticleMetadata) -> Article:
        """
        Parse individual article page.
        
        Divaina article structure:
        - Headline: <h1>
        - Content: .entry-content
        - Date: Various formats in meta or text
        
        Args:
            html: Raw HTML of article page
            metadata: Article metadata from list page
        
        Returns:
            Article object with full content
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # Extract headline
        headline = metadata.headline
        headline_elem = soup.select_one('h1, h1.entry-title')
        if headline_elem:
            headline = headline_elem.get_text(strip=True)
        
        # Extract body content
        content_elem = soup.select_one('.entry-content')
        if not content_elem:
            raise ValueError(f"No content found for {metadata.url}")
        
        # Get all paragraphs and text
        paragraphs = content_elem.select('p')
        body_parts = []
        
        for p in paragraphs:
            text = p.get_text(strip=True)
            if len(text) > 20:  # Skip very short paragraphs
                body_parts.append(text)
        
        body = '\n\n'.join(body_parts)
        
        if not body or len(body) < 50:
            raise ValueError(f"Insufficient content for {metadata.url}")
        
        # Extract date
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        # Try to find date in various locations
        time_elem = soup.select_one('time, .meta-date, .entry-date')
        if time_elem:
            date_text = time_elem.get('datetime') or time_elem.get_text(strip=True)
            # Try to parse date
            try:
                # Match YYYY-MM-DD pattern
                date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_text)
                if date_match:
                    date_str = date_match.group(0)
            except:
                pass
        
        # Extract author (if available)
        author = None
        author_elem = soup.select_one('.author, .entry-author, .meta-author')
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
            source='divaina',
            extraction_timestamp=datetime.now().isoformat()
        )
        
        return article
    
    def get_next_page_url(self, current_url: str, html: str, current_page: int) -> Optional[str]:
        """
        Get URL for the next page.
        
        Divaina uses WordPress pagination with /page/N/ pattern.
        
        Args:
            current_url: Current page URL
            html: Current page HTML
            current_page: Current page number (1-indexed)
        
        Returns:
            URL for next page, or None if on last page
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # Look for "next" link
        next_link = soup.select_one('a[rel="next"], .next.page-numbers, a.next')
        if next_link and next_link.get('href'):
            next_href = next_link.get('href')
            if next_href.startswith('http'):
                return next_href
            else:
                return urljoin(self.BASE_URL, next_href)
        
        # Fallback: check if there are articles on page (if empty, no next page)
        articles = soup.select('.p-wrap')
        if len(articles) == 0:
            return None
        
        # Generate next page URL (WordPress standard)
        next_page = current_page + 1
        base_url = current_url.split('/page/')[0]  # Remove /page/N if present
        return f"{base_url}/page/{next_page}/"
