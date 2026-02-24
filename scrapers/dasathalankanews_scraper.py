"""
Dasatha Lanka News Scraper

Scraper for Dasatha Lanka News (https://dasathalankanews.com/) - Sinhala news website.
"""

import logging
import re
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from core.base_scraper import BaseScraper, ArticleMetadata, Article

logger = logging.getLogger(__name__)


class DasathaLankaNewsScraper(BaseScraper):
    """
    Scraper for Dasatha Lanka News website.
    
    Site structure:
    - WordPress platform with tagDiv Composer theme
    - Post containers: .td_module_wrap, .td-module-container
    - Category-based navigation
    - Standard WordPress pagination (/page/N/)
    """
    
    BASE_URL = "https://dasathalankanews.com"
    SITE_NAME = "dasathalankanews"
    
    CATEGORIES = {
        'local-news': {
            'name': 'Local News',
            'url': f'{BASE_URL}/local-news/',
            'slug': 'local'
        },
        'star-gossip': {
            'name': 'Star Gossip',
            'url': f'{BASE_URL}/star-gossip/',
            'slug': 'gossip'
        },
        'political-news': {
            'name': 'Political News',
            'url': f'{BASE_URL}/political-news/',
            'slug': 'politics'
        },
        'sports-news': {
            'name': 'Sports News',
            'url': f'{BASE_URL}/sports-news/',
            'slug': 'sports'
        },
        'world-news': {
            'name': 'World News',
            'url': f'{BASE_URL}/world-news/',
            'slug': 'world'
        },
        'business-news': {
            'name': 'Business News',
            'url': f'{BASE_URL}/business-news/',
            'slug': 'business'
        }
    }
    
    def get_category_urls(self) -> Dict[str, str]:
        """Get mapping of category names to their URLs."""
        category_urls = {}
        for category_key, category_info in self.CATEGORIES.items():
            category_urls[category_key] = category_info['url']
        
        logger.info(f"Dasatha Lanka News: Found {len(category_urls)} categories")
        return category_urls
    
    def get_article_list_url(self, category_url: str, page_number: int) -> str:
        """Construct URL for a specific page of article list."""
        if page_number == 1:
            return category_url
        else:
            # WordPress pagination format
            base_url = category_url.rstrip('/')
            return f"{base_url}/page/{page_number}/"
    
    def parse_article_list_page(self, html: str, category: str) -> List[ArticleMetadata]:
        """Parse article list page and extract article metadata."""
        soup = BeautifulSoup(html, 'lxml')
        articles = []
        
        # Find article containers (tagDiv theme specific)
        article_containers = soup.select('.td_module_wrap, .td-module-container')
        
        logger.info(f"Dasatha {category}: Found {len(article_containers)} article containers")
        
        for container in article_containers:
            try:
                # Find article link (tagDiv stores in multiple possible locations)
                link = container.select_one('h3 a, .entry-title a, .td-module-title a, .td-image-wrap a')
                
                if not link or not link.get('href'):
                    continue
                
                url = link.get('href')
                
                # Make URL absolute
                if not url.startswith('http'):
                    url = urljoin(self.BASE_URL, url)
                
                # Skip non-article URLs
                if '/category/' in url or '/tag/' in url or url == self.BASE_URL + '/':
                    continue
                
                # Get headline
                # Try title from h3 first (more likely to be headline)
                title_elem = container.select_one('h3 a, h3, .entry-title, .td-module-title')
                if title_elem:
                    headline = title_elem.get_text(strip=True)
                else:
                    headline = link.get_text(strip=True)
                
                if not headline or len(headline) < 10:
                    continue
                
                article = ArticleMetadata(
                    url=url,
                    headline=headline,
                    category=category
                )
                articles.append(article)
                
            except Exception as e:
                logger.warning(f"Error parsing article container: {e}")
                continue
        
        logger.info(f"Dasatha {category}: Extracted {len(articles)} articles from list page")
        return articles
    
    def parse_article_page(self, html: str, metadata: ArticleMetadata) -> Article:
        """Parse individual article page and extract content."""
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Extract headline
            headline = metadata.headline
            headline_elem = soup.select_one('h1.entry-title, h1, .td-post-title')
            if headline_elem:
                headline = headline_elem.get_text(strip=True)
            
            # Extract content (tagDiv theme specific selectors)
            content_elem = soup.select_one('.td-post-content, .entry-content, .post-content, .td-pb-row')
            
            if not content_elem:
                # Fallback to article tag
                content_elem = soup.select_one('article')
            
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
            
            # Fallback to all text if no paragraphs
            if not body_paragraphs:
                text = content_elem.get_text(strip=True)
                if len(text) > 50:
                    body_paragraphs = [text]
            
            if not body_paragraphs:
                logger.warning(f"Minimal content for {metadata.url}")
                body_paragraphs = [headline]
            
            body = '\n\n'.join(body_paragraphs)
            
            # Calculate word count
            word_count = len(body.split())
            
            # Extract date (tagDiv theme specific)
            date_str = datetime.now().strftime('%Y-%m-%d')
            date_elem = soup.select_one('time, .td-post-date, .entry-date, .updated')
            if date_elem:
                datetime_attr = date_elem.get('datetime')
                if datetime_attr:
                    try:
                        # Parse ISO format datetime
                        parsed_date = datetime.fromisoformat(datetime_attr.split('T')[0])
                        date_str = parsed_date.strftime('%Y-%m-%d')
                    except:
                        # Try to extract from text
                        date_text = date_elem.get_text(strip=True)
                        date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_text)
                        if date_match:
                            date_str = date_match.group(0)
            
            # Extract author
            author = None
            author_elem = soup.select_one('.td-post-author-name, .author, [rel="author"]')
            if author_elem:
                author = author_elem.get_text(strip=True)
            
            # Extract tags/categories
            tags = [metadata.category]
            
            # Try to get categories from page
            category_elems = soup.select('.td-post-category, .entry-category, .category')
            for cat_elem in category_elems:
                cat_text = cat_elem.get_text(strip=True)
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
            
            # Look for next page link (tagDiv theme specific)
            next_link = soup.select_one('.next, .next-page, a[rel="next"], .td-next-page, .page-nav a.next')
            
            if next_link and next_link.get('href'):
                next_url = next_link.get('href')
                if not next_url.startswith('http'):
                    next_url = urljoin(self.BASE_URL, next_url)
                logger.info(f"Found next page URL: {next_url}")
                return next_url
            
            # Fallback: look for page number links
            page_links = soup.select('a.page-numbers, .page-nav a')
            for link in page_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # Check if it's the next page number
                if f'/page/{current_page + 1}/' in href:
                    next_url = href if href.startswith('http') else urljoin(self.BASE_URL, href)
                    logger.info(f"Found next page URL (by number): {next_url}")
                    return next_url
            
            # Check if we found articles - if too few, probably last page
            articles = soup.select('.td_module_wrap, .td-module-container')
            if len(articles) < 5:
                logger.info(f"Only {len(articles)} articles found, likely last page")
                return None
            
            logger.info("No next page URL found")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting next page URL: {e}")
            return None
