"""
Lankadeepa News Scraper
Website: https://www.lankadeepa.lk/
"""

from typing import Optional, Dict, Any, List
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from datetime import datetime
from core.base_scraper import BaseScraper, ArticleMetadata, Article
import logging

logger = logging.getLogger(__name__)


class LankadeepaScraper(BaseScraper):
    """Scraper for Lankadeepa news website"""
    
    BASE_URL = "https://www.lankadeepa.lk"
    SITE_NAME = "lankadeepa"
    
    # Categories available on Lankadeepa
    CATEGORIES = {
        'latest': 'Latest',
        'business': 'Business',
        'sports': 'Sports',
        'kelimadala': 'Kelimadala (Sports)',
        'news': 'News',
        'politics': 'Politics',
        'thaksalawa': 'Thaksalawa',
        'visheshanga': 'Visheshanga',
        'mathawada': 'Mathawada',
    }
    
    def get_site_name(self) -> str:
        """Return the site name"""
        return self.SITE_NAME
    
    def get_category_urls(self) -> Dict[str, str]:
        """
        Get category URLs for Lankadeepa.
        Returns mapping of category name to URL.
        
        Lankadeepa uses category IDs in URLs:
        - business: /business/9/
        - sports: /sports/3/
        - news: /news/101/
        - politics: /politics/54/
        - thaksalawa: /thaksalawa/55/
        - visheshanga: /visheshanga/26/
        - mathawada: /mathawada/317/
        - latest: homepage
        """
        return {
            'latest': f'{self.BASE_URL}/',  # Homepage
            'business': f'{self.BASE_URL}/business/9/',
            'sports': f'{self.BASE_URL}/sports/3/',
            'kelimadala': f'{self.BASE_URL}/kelimadala/3/',  # Sports/Kelimadala
            'news': f'{self.BASE_URL}/news/101/',
            'politics': f'{self.BASE_URL}/politics/54/',
            'thaksalawa': f'{self.BASE_URL}/thaksalawa/55/',
            'visheshanga': f'{self.BASE_URL}/visheshanga/26/',
            'mathawada': f'{self.BASE_URL}/mathawada/317/',
        }
    
    def get_article_list_url(self, category_url: str, page: int) -> Optional[str]:
        """
        Get URL for article list page.
        
        Lankadeepa uses offset-based pagination:
        - Page 1: /business/9/
        - Page 2: /business/9/30
        - Page 3: /business/9/60
        
        Each page shows 30 articles, offset increments by 30.
        """
        if page == 1:
            return category_url
        
        # Calculate offset: (page - 1) * 30
        offset = (page - 1) * 30
        
        # Add offset to URL (remove trailing slash first)
        base = category_url.rstrip('/')
        return f"{base}/{offset}"
    
    def parse_article_list_page(self, html: str, category: str) -> List[ArticleMetadata]:
        """
        Extract article URLs from category page.
        
        Lankadeepa has article URLs in format:
        /category/sinhala-slug/ID-NUMBER
        Example: /business/සළ-හ-මධය-වයපර-කඩ-වටණත-රටම-කඩ-වටව/9-688100
        
        Args:
            html: HTML content of list page
            category: Category name
        
        Returns:
            List of ArticleMetadata objects
        """
        soup = BeautifulSoup(html, 'lxml')
        articles = []
        
        # Pattern to match article URLs: /category/title/id-number
        # Format: /[category]/[sinhala-slug]/[digit]-[article-id]
        article_pattern = re.compile(r'/[a-z-]+/[^/]+/\d+-\d+')
        
        # Find all links on the page
        for link in soup.select('a[href]'):
            href = link.get('href', '')
            
            # Check if href matches article pattern
            if article_pattern.search(href):
                # Get headline text to verify it's Sinhala content
                text = link.get_text(strip=True)
                
                # Check for Sinhala Unicode characters (0D80-0DFF is Sinhala block)
                if text and any('\u0d80' <= char <= '\u0dff' for char in text):
                    # Convert relative URL to absolute
                    if not href.startswith('http'):
                        href = urljoin(self.BASE_URL, href)
                    
                    # Only include lankadeepa.lk articles, exclude external links
                    if 'lankadeepa.lk' in href:
                        articles.append(ArticleMetadata(
                            url=href,
                            headline=text,
                            category=category
                        ))
        
        logger.info(f"Found {len(articles)} article URLs on Lankadeepa {category} page")
        return articles
    
    def parse_article_page(self, html: str, metadata: ArticleMetadata) -> Article:
        """
        Parse individual article page and extract content.
        
        Args:
            html: HTML content of article page
            metadata: ArticleMetadata from list page
        
        Returns:
            Article object with full content
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # Extract headline
        headline_elem = soup.select_one('h1')
        if not headline_elem:
            raise ValueError(f"No headline found for {metadata.url}")
        
        headline = headline_elem.get_text(strip=True)
        
        # Validate headline has Sinhala content
        if not any('\u0d80' <= char <= '\u0dff' for char in headline):
            raise ValueError(f"Headline not in Sinhala: {headline}")
        
        # Extract body content
        body_elem = soup.select_one('.article-body')
        if not body_elem:
            raise ValueError(f"No article body found for {metadata.url}")
        
        # Get all paragraphs from body
        paragraphs = body_elem.select('p')
        if not paragraphs:
            raise ValueError(f"No paragraphs found in article body for {metadata.url}")
        
        # Combine paragraph text
        body_text = '\n\n'.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        
        # Validate body has content
        if len(body_text) < 100:
            raise ValueError(f"Article body too short ({len(body_text)} chars): {metadata.url}")
        
        # Validate body has Sinhala content
        if not any('\u0d80' <= char <= '\u0dff' for char in body_text):
            raise ValueError(f"Body text not in Sinhala: {metadata.url}")
        
        # Extract date (optional)
        date_elem = soup.select_one('time') or soup.select_one('.date') or soup.select_one('span[class*="date"]')
        date_str = ''
        if date_elem:
            date_str = date_elem.get('datetime') or date_elem.get_text(strip=True)
        
        # Fallback to metadata date or current date if empty
        if not date_str:
            date_str = metadata.date or datetime.now().strftime('%Y-%m-%d')
        
        return Article(
            headline=headline,
            body=body_text,
            source=self.SITE_NAME,
            category=metadata.category,
            date=date_str,
            url=metadata.url,
            extraction_timestamp=datetime.now().isoformat()
        )
    
    def get_next_page_url(self, soup: BeautifulSoup, current_url: str, current_page: int) -> Optional[str]:
        """
        Get URL for next page of article list.
        
        Lankadeepa uses offset-based pagination.
        Next page URL calculated by adding 30 to current offset.
        """
        # Calculate next offset
        next_offset = current_page * 30
        
        # Extract base URL (e.g., /business/9/ from /business/9/30)
        if '/' in current_url:
            parts = current_url.rstrip('/').split('/')
            # Check if last part is numeric (offset)
            if parts[-1].isdigit():
                base_url = '/'.join(parts[:-1])
            else:
                base_url = current_url.rstrip('/')
        else:
            base_url = current_url.rstrip('/')
        
        return f"{base_url}/{next_offset}"
    
    def validate_article_url(self, url: str) -> bool:
        """
        Validate if URL is a valid Lankadeepa article URL.
        
        Valid format: /category/sinhala-slug/ID-NUMBER
        Example: /business/සළ-හ-මධය-වයපර-කඩ-වටණත-රටම-කඩ-වටව/9-688100
        """
        # Check domain
        if 'lankadeepa.lk' not in url:
            return False
        
        # Check pattern: /category/slug/id-number
        pattern = re.compile(r'/[a-z-]+/[^/]+/\d+-\d+')
        return bool(pattern.search(url))
