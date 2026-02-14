"""
SiluminaScraper - Concrete scraper for Silumina newspaper website.

Website: https://www.silumina.lk
Pattern: WordPress-based with standard categories
"""

import logging
import re
from typing import List, Dict
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from core.base_scraper import BaseScraper, ArticleMetadata, Article


logger = logging.getLogger(__name__)


class SiluminaScraper(BaseScraper):
    """
    Concrete scraper for Silumina newspaper website.
    
    URL Structure:
    - Homepage: https://www.silumina.lk
    - Category: https://www.silumina.lk/category/[slug]/
    - Pagination: https://www.silumina.lk/category/[slug]/page/[N]/
    - Article: https://www.silumina.lk/YYYY/MM/DD/[category]/[id]/[slug]
    
    Categories:
    - Politics (politics)
    - News (news)
    - Business (business)
    - Features (news-features)
    - Sports (various sport categories)
    """
    
    BASE_URL = 'https://www.silumina.lk'
    
    # Categories based on site navigation
    CATEGORIES = {
        'politics': {
            'slug': 'politics',
            'name': 'දේශපාලන'
        },
        'news': {
            'slug': 'news',
            'name': 'පුවත්'
        },
        'business': {
            'slug': 'business',
            'name': 'ව්‍යාපාරික'
        },
        'features': {
            'slug': 'news-features',
            'name': 'විශේෂාංග'
        },
        'sports': {
            'slug': 'sport',
            'name': 'ක්‍රීඩා'
        },
        'world': {
            'slug': 'world',
            'name': 'විදෙස්'
        },
        'entertainment': {
            'slug': 'rasanduna',
            'name': 'රසඳුන'
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
            slug = category_info['slug']
            url = f"{self.BASE_URL}/category/{slug}/"
            category_urls[category_key] = url
        
        logger.info(f"Silumina: Found {len(category_urls)} categories")
        return category_urls
    
    def get_article_list_url(self, category_url: str, page: int = 1) -> str:
        """
        Build URL for a specific page of article list.
        
        Silumina uses standard WordPress pagination: /page/N/
        
        Args:
            category_url: Base URL for category
            page: Page number (1-indexed)
        
        Returns:
            Full URL for article list page
        """
        if page == 1:
            return category_url
        
        # Ensure trailing slash
        base = category_url.rstrip('/')
        return f"{base}/page/{page}/"
    
    def parse_article_list_page(self, html: str, category: str) -> List[ArticleMetadata]:
        """
        Parse article list page and extract article metadata.
        
        Silumina structure:
        - Articles in <article class="item hentry">
        - Link: <a> with href to article
        - Headline: <h2>
        - Date: <span class="date"> or <time>
        - Excerpt: <p>
        
        Args:
            html: HTML content of list page
            category: Category name
        
        Returns:
            List of ArticleMetadata objects
        """
        soup = BeautifulSoup(html, 'lxml')
        articles = []
        
        # Silumina uses <article> tags
        article_containers = soup.select('article') or soup.select('article.item')
        
        if not article_containers:
            logger.warning(f"No article containers found in Silumina {category} list page")
            return articles
        
        for container in article_containers:
            try:
                # Extract article link
                link_elem = container.select_one('a')
                
                if not link_elem:
                    continue
                
                article_url = link_elem.get('href', '')
                
                # Make absolute URL
                if article_url.startswith('/'):
                    article_url = urljoin(self.BASE_URL, article_url)
                elif not article_url.startswith('http'):
                    article_url = urljoin(self.BASE_URL, article_url)
                
                # Skip if not a Silumina article
                if 'silumina.lk' not in article_url:
                    continue
                
                # Skip category pages
                if '/category/' in article_url or '/page/' in article_url:
                    continue
                
                # Extract headline
                headline_elem = (
                    container.select_one('h2') or
                    container.select_one('h3') or
                    container.select_one('.title') or
                    link_elem
                )
                
                headline = headline_elem.get_text(strip=True) if headline_elem else 'Untitled'
                
                # Skip if headline is empty or too short
                if len(headline) < 10:
                    continue
                
                # Extract date (optional)
                date_elem = (
                    container.select_one('time') or
                    container.select_one('.date') or
                    container.select_one('span[class*="date"]')
                )
                
                date_str = None
                if date_elem:
                    date_str = date_elem.get('datetime') or date_elem.get_text(strip=True)
                
                # Extract excerpt (optional)
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
                logger.warning(f"Failed to parse article container in Silumina list: {e}")
                continue
        
        logger.info(f"Silumina {category}: Extracted {len(articles)} articles from list page")
        
        return articles
    
    def parse_article_page(self, html: str, metadata: ArticleMetadata) -> Article:
        """
        Parse individual article page and extract full content.
        
        Silumina article structure:
        - Headline: <h1 class="entry-title">
        - Body: <div class="entry-content">
        - Date: <time> or <span class="date">
        - Author: <span class="author">
        
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
        headline_elem = (
            soup.select_one('h1.entry-title') or
            soup.select_one('h1') or
            soup.select_one('.entry-title')
        )
        
        if not headline_elem:
            headline = metadata.headline
        else:
            headline = self.text_processor.process_headline(headline_elem.get_text())
        
        # Extract body (main content)
        body_elem = soup.select_one('.entry-content')
        
        if not body_elem:
            raise ValueError(f"Article body not found for: {metadata.url}")
        
        # Remove unwanted elements
        for unwanted in body_elem.select('.ad, .advertisement, .related, .share, .social, script, style, iframe'):
            unwanted.decompose()
        
        # Get HTML content and process
        body_html = str(body_elem)
        body = self.text_processor.process(body_html)
        
        if len(body) < 100:
            raise ValueError(f"Article body too short ({len(body)} chars): {metadata.url}")
        
        # Extract date
        date_elem = (
            soup.select_one('time') or
            soup.select_one('.date') or
            soup.select_one('.entry-date')
        )
        
        if date_elem:
            date_str = date_elem.get('datetime') or date_elem.get_text(strip=True)
            date_str = self.text_processor.process_headline(date_str)
        else:
            date_str = metadata.date or datetime.now().strftime('%Y-%m-%d')
        
        # Extract author (optional)
        author_elem = (
            soup.select_one('.author-name') or
            soup.select_one('.by-author') or
            soup.select_one('a[rel="author"]')
        )
        
        author = author_elem.get_text(strip=True) if author_elem else None
        
        # Create article object
        article = Article(
            url=metadata.url,
            headline=headline,
            body=body,
            category=metadata.category,
            date=date_str,
            author=author,
            source='silumina',
            extraction_timestamp=datetime.now().isoformat()
        )
        
        return article
    
    def get_next_page_url(self, current_url: str, html: str, current_page: int) -> str:
        """Get URL for the next page."""
        return self.get_article_list_url(current_url.split('/page/')[0].rstrip('/') + '/', current_page + 1)
