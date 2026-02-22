"""
Roar Media Archive Scraper

Scraper for Roar Media Sinhala tech section (https://archive.roar.media/sinhala/tech-s/).
"""

import logging
import re
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from core.base_scraper import BaseScraper, ArticleMetadata, Article

logger = logging.getLogger(__name__)


class RoarMediaScraper(BaseScraper):
    """
    Scraper for Roar Media Archive Sinhala technology section.
    
    Site structure:
    - Archive site (ceased operations in 2024)
    - Tech section: /sinhala/tech-s/
    - Pagination: /page/2/, /page/3/, etc.
    - Article URLs: /sinhala/tech/{category}/{slug}/
    - Content in .entry-content container
    """
    
    BASE_URL = "https://archive.roar.media"
    SITE_NAME = "roarmedia"
    
    CATEGORIES = {
        'tech': {
            'name': 'Technology',
            'url': f'{BASE_URL}/sinhala/tech-s/',
            'slug': 'tech'
        }
    }
    
    def get_category_urls(self) -> Dict[str, str]:
        """Get mapping of category names to their URLs."""
        category_urls = {}
        for category_key, category_info in self.CATEGORIES.items():
            category_urls[category_key] = category_info['url']
        
        logger.info(f"Roar Media: Found {len(category_urls)} categories")
        return category_urls
    
    def get_article_list_url(self, category_url: str, page_number: int) -> str:
        """Construct URL for a specific page of article list."""
        if page_number == 1:
            return category_url
        else:
            # Standard WordPress-style pagination
            return f"{category_url}page/{page_number}/"
    
    def parse_article_list_page(self, html: str, category: str) -> List[ArticleMetadata]:
        """Parse article list page and extract article metadata."""
        soup = BeautifulSoup(html, 'lxml')
        articles = []
        
        # Find all article containers
        article_containers = soup.select('article')
        
        logger.info(f"Roar Media {category}: Found {len(article_containers)} article containers")
        
        for container in article_containers:
            try:
                # Get article link (first link in article)
                link = container.select_one('a')
                if not link or not link.get('href'):
                    continue
                
                url = link.get('href')
                
                # Make absolute URL
                if not url.startswith('http'):
                    url = urljoin(self.BASE_URL, url)
                
                # Skip non-article URLs
                if not '/sinhala/tech/' in url:
                    continue
                
                # Get title from link text
                title = link.get_text(strip=True)
                
                # Try to get title from h2/h3 if link text is too short
                if not title or len(title) < 10:
                    title_elem = container.select_one('h2, h3')
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                
                if not title:
                    continue
                
                article = ArticleMetadata(
                    url=url,
                    headline=title,
                    category=category
                )
                articles.append(article)
                
            except Exception as e:
                logger.warning(f"Error parsing article container: {e}")
                continue
        
        logger.info(f"Roar Media {category}: Extracted {len(articles)} articles from list page")
        return articles
    
    def parse_article_page(self, html: str, metadata: ArticleMetadata) -> Article:
        """Parse individual article page and extract content."""
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Extract headline
            headline = metadata.headline
            headline_elem = soup.select_one('h1')
            if headline_elem:
                headline = headline_elem.get_text(strip=True)
            
            # Extract content from .entry-content
            content_elem = soup.select_one('.entry-content')
            
            if not content_elem:
                raise ValueError(f"No content found for {metadata.url}")
            
            # Extract paragraphs
            paragraphs = content_elem.select('p')
            
            body_paragraphs = []
            for para in paragraphs:
                text = para.get_text(strip=True)
                # Skip short lines, ads, captions
                if len(text) > 30:
                    body_paragraphs.append(text)
            
            if not body_paragraphs:
                # Fallback to all text
                text = content_elem.get_text(strip=True)
                if len(text) > 50:
                    body_paragraphs = [text]
            
            if not body_paragraphs:
                logger.warning(f"Minimal content for {metadata.url}")
                body_paragraphs = [headline]
            
            body = '\\n\\n'.join(body_paragraphs)
            
            # Calculate word count
            word_count = len(body.split())
            
            # Extract date from time element
            date_str = datetime.now().strftime('%Y-%m-%d')
            time_elem = soup.select_one('time')
            if time_elem:
                datetime_attr = time_elem.get('datetime')
                if datetime_attr:
                    try:
                        # Parse ISO format datetime (e.g., "2023-05-09T12:26:26+05:30")
                        parsed_date = datetime.fromisoformat(datetime_attr.split('T')[0])
                        date_str = parsed_date.strftime('%Y-%m-%d')
                    except Exception as e:
                        logger.debug(f"Date parsing error: {e}")
            
            # Extract author
            author = None
            author_elem = soup.select_one('.author-name, [rel="author"], .post-author, .author')
            if author_elem:
                author = author_elem.get_text(strip=True)
            
            # Extract category from page or metadata
            tags = [metadata.category]
            
            # Try to find subcategory from URL or page
            if '/trending/' in metadata.url:
                tags.append('trending')
            elif '/apps/' in metadata.url:
                tags.append('apps')
            elif '/gadgets/' in metadata.url:
                tags.append('gadgets')
            elif '/identities/' in metadata.url:
                tags.append('identities')
            
            # Add category from page if exists
            category_elem = soup.select_one('.category')
            if category_elem:
                cat_text = category_elem.get_text(strip=True)
                if cat_text and cat_text not in tags:
                    tags.append(cat_text)
            
            return Article(
                url=metadata.url,
                headline=headline,
                body=body,
                date=date_str,
                source=self.website_name,
                category=metadata.category,
                author=author,
                tags=tags,
                word_count=word_count,
                extraction_timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error parsing article {metadata.url}: {e}")
            raise
    
    def get_next_page_url(self, current_url: str, html: str, current_page: int) -> Optional[str]:
        """Extract URL for next page of articles."""
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Look for pagination link with "පැරණි ලිපි" (older articles) or next page number
            next_link = None
            
            # Try to find explicit next link
            for link in soup.select('a[href*="/page/"]'):
                text = link.get_text(strip=True)
                href = link.get('href', '')
                
                # Check if it's the next page
                if f'/page/{current_page + 1}/' in href:
                    next_link = link
                    break
                
                # Or if it contains pagination text
                if 'පැරණි' in text or 'ලිපි' in text or 'Next' in text:
                    next_link = link
                    break
            
            if next_link and next_link.get('href'):
                next_url = next_link.get('href')
                if not next_url.startswith('http'):
                    next_url = urljoin(self.BASE_URL, next_url)
                logger.info(f"Found next page URL: {next_url}")
                return next_url
            
            # Fallback: check if there are enough articles
            articles = soup.select('article')
            if len(articles) < 10:
                logger.info(f"Only {len(articles)} articles found, likely last page")
                return None
            
            logger.info("No next page URL found")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting next page URL: {e}")
            return None
