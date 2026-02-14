"""
BBCSinhalaScraper - Concrete scraper for BBC Sinhala news website.

Website: https://www.bbc.com/sinhala
Pattern: Topic-based navigation with articles
"""

import logging
import re
from typing import List, Dict
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from core.base_scraper import BaseScraper, ArticleMetadata, Article


logger = logging.getLogger(__name__)


class BBCSinhalaScraper(BaseScraper):
    """
    Concrete scraper for BBC Sinhala news website.
    
    URL Structure:
    - Homepage: https://www.bbc.com/sinhala
    - Topics: https://www.bbc.com/sinhala/topics/[topic_id]
    - Article: https://www.bbc.com/sinhala/articles/[article_id]
    
    Categories are organized by topics with unique IDs.
    """
    
    BASE_URL = 'https://www.bbc.com'
    SINHALA_BASE = 'https://www.bbc.com/sinhala'
    
    # BBC Sinhala topics
    CATEGORIES = {
        'latest': {
            'id': 'homepage',
            'name': 'ප්‍රධාන පුවත්'
        },
        'sri_lanka': {
            'id': 'cg7267dz901t',
            'name': 'ශ්‍රී ලංකා'
        },
        'world': {
            'id': 'c83plvepnq1t',
            'name': 'ලෝකය'
        },
        'sports': {
            'id': 'cvjp2jy9g2qt',
            'name': 'ක්‍රීඩා'
        },
        'health': {
            'id': 'cz74k723j57t',
            'name': 'සෞඛ්‍ය'
        },
    }
    
    def get_category_urls(self) -> Dict[str, str]:
        """
        Get mapping of category names to their URLs.
        
        Returns:
            Dict mapping category_name → category_url
        """
        category_urls = {}
        
        for category_key, category_info in self.CATEGORIES.items():
            cat_id = category_info['id']
            if cat_id == 'homepage':
                url = self.SINHALA_BASE
            else:
                url = f"{self.SINHALA_BASE}/topics/{cat_id}"
            category_urls[category_key] = url
        
        logger.info(f"BBC Sinhala: Found {len(category_urls)} categories")
        return category_urls
    
    def get_article_list_url(self, category_url: str, page: int = 1) -> str:
        """
        Build URL for a specific page of article list.
        
        BBC Sinhala uses client-side rendering with infinite scroll.
        Only page 1 is reliably scrapeable.
        
        Args:
            category_url: Base URL for category
            page: Page number (1-indexed)
        
        Returns:
            Category URL (only page 1 supported)
        """
        # BBC Sinhala uses JavaScript infinite scroll - no server-side pagination
        return category_url
    
    def parse_article_list_page(self, html: str, category: str) -> List[ArticleMetadata]:
        """
        Parse article list page and extract article metadata.
        
        BBC Sinhala structure:
        - Articles in promo containers
        - Link: <a href="/sinhala/articles/[id]">
        - Headline: <h3> or <h2>
        - Date: <time> tag
        
        Args:
            html: HTML content of list page
            category: Category name
        
        Returns:
            List of ArticleMetadata objects
        """
        soup = BeautifulSoup(html, 'lxml')
        articles = []
        
        # BBC uses promo elements
        main_area = soup.select_one('main') or soup
        
        # Find all promo elements that contain article links
        promo_containers = main_area.select('[class*="promo"]')
        
        if not promo_containers:
            logger.warning(f"No promo containers found in BBC Sinhala {category} list page")
            return articles
        
        for container in promo_containers:
            try:
                # Find article link - must contain /sinhala/articles/
                link_elem = container.select_one('a[href*="/sinhala/articles/"]')
                
                if not link_elem:
                    continue
                
                article_url = link_elem.get('href', '')
                
                # Make absolute URL
                if article_url.startswith('/'):
                    article_url = urljoin(self.BASE_URL, article_url)
                elif not article_url.startswith('http'):
                    article_url = urljoin(self.BASE_URL, article_url)
                
                # Must be a BBC Sinhala article
                if '/sinhala/articles/' not in article_url:
                    continue
                
                # Extract headline
                headline_elem = (
                    container.select_one('h3') or
                    container.select_one('h2') or
                    container.select_one('[data-testid*="headline"]') or
                    link_elem
                )
                
                headline = headline_elem.get_text(strip=True) if headline_elem else 'Untitled'
                
                # Skip if headline is empty or too short
                if len(headline) < 10:
                    continue
                
                # Extract date (optional)
                date_elem = container.select_one('time')
                
                date_str = None
                if date_elem:
                    date_str = date_elem.get('datetime') or date_elem.get_text(strip=True)
                
                # Extract excerpt (optional) - BBC may have description
                excerpt_elem = container.select_one('p')
                excerpt = excerpt_elem.get_text(strip=True) if excerpt_elem else None
                
                # Create metadata
                metadata = ArticleMetadata(
                    url=article_url,
                    headline=self.text_processor.process_headline(headline),
                    category=category,
                    date=date_str,
                    excerpt=excerpt
                )
                
                articles.append(metadata)
                
            except Exception as e:
                logger.warning(f"Failed to parse promo container in BBC Sinhala list: {e}")
                continue
        
        logger.info(f"BBC Sinhala {category}: Extracted {len(articles)} articles from list page")
        
        return articles
    
    def parse_article_page(self, html: str, metadata: ArticleMetadata) -> Article:
        """
        Parse individual article page and extract full content.
        
        BBC article structure:
        - Headline: <h1>
        - Body: Multiple <div data-component="text-block">
        - Date: <time>
        
        Args:
            html: HTML content of article page
            metadata: Metadata from list page
        
        Returns:
            Complete Article object
        
        Raises:
            ValueError: If article structure is invalid/unexpected
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # Extract headline
        headline_elem = soup.select_one('h1')
        
        if not headline_elem:
            headline = metadata.headline
        else:
            headline = self.text_processor.process_headline(headline_elem.get_text())
        
        # Extract body - BBC uses data-component="text-block" for paragraphs
        text_blocks = soup.select('[data-component="text-block"]')
        
        if not text_blocks:
            # Fallback: try main tag
            main = soup.select_one('main')
            if main:
                # Get all paragraphs in main
                text_blocks = main.select('p')
        
        if not text_blocks:
            raise ValueError(f"Article body not found for: {metadata.url}")
        
        # Combine all text blocks
        body_parts = []
        for block in text_blocks:
            text = block.get_text(strip=True)
            if len(text) > 20:  # Skip very short blocks
                body_parts.append(text)
        
        body = '\n\n'.join(body_parts)
        body = self.text_processor.process(body)
        
        if len(body) < 100:
            raise ValueError(f"Article body too short ({len(body)} chars): {metadata.url}")
        
        # Extract date
        date_elem = soup.select_one('time')
        
        if date_elem:
            date_str = date_elem.get('datetime') or date_elem.get_text(strip=True)
            date_str = self.text_processor.process_headline(date_str)
        else:
            date_str = metadata.date or datetime.now().strftime('%Y-%m-%d')
        
        # BBC articles don't typically show author
        author = 'BBC Sinhala'
        
        # Create article object
        article = Article(
            url=metadata.url,
            headline=headline,
            body=body,
            category=metadata.category,
            date=date_str,
            author=author,
            source='bbc_sinhala',
            extraction_timestamp=datetime.now().isoformat()
        )
        
        return article
    
    def get_next_page_url(self, current_url: str, html: str, current_page: int) -> str:
        """Get URL for the next page. BBC Sinhala only supports page 1."""
        # No pagination for BBC Sinhala (JavaScript infinite scroll)
        return None
