"""
Lanka C News Scraper

Scraper for Lanka C News (https://www.lankacnews.com/) - Sinhala news website on Blogger platform.
"""

import logging
import re
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urljoin, quote

from bs4 import BeautifulSoup

from core.base_scraper import BaseScraper, ArticleMetadata, Article

logger = logging.getLogger(__name__)


class LankaCNewsScraper(BaseScraper):
    """
    Scraper for Lanka C News website.
    
    Site structure:
    - Blogger platform
    - Post containers: .post, .hentry
    - Categories via /search/label/{category}
    - Standard Blogger pagination
    """
    
    BASE_URL = "https://www.lankacnews.com"
    SITE_NAME = "lankacnews"
    
    CATEGORIES = {
        'local': {
            'name': 'Local',
            'url': f'{BASE_URL}/search/label/Local',
            'slug': 'local'
        },
        'foreign': {
            'name': 'Foreign',
            'url': f'{BASE_URL}/search/label/Foreign',
            'slug': 'foreign'
        },
        'sports': {
            'name': 'Sports',
            'url': f'{BASE_URL}/search/label/Sports',
            'slug': 'sports'
        },
        'economy': {
            'name': 'Economy',
            'url': f'{BASE_URL}/search/label/Economy',
            'slug': 'economy'
        },
        'market': {
            'name': 'Market',
            'url': f'{BASE_URL}/search/label/Market',
            'slug': 'market'
        },
        'technology': {
            'name': 'Technology',
            'url': f'{BASE_URL}/search/label/Technology',
            'slug': 'technology'
        },
        'arts': {
            'name': 'Arts',
            'url': f'{BASE_URL}/search/label/Arts',
            'slug': 'arts'
        },
        'auto': {
            'name': 'Auto',
            'url': f'{BASE_URL}/search/label/Auto',
            'slug': 'auto'
        },
        'featured': {
            'name': 'Featured',
            'url': f'{BASE_URL}/search/label/Featured',
            'slug': 'featured'
        }
    }
    
    def get_category_urls(self) -> Dict[str, str]:
        """Get mapping of category names to their URLs."""
        category_urls = {}
        for category_key, category_info in self.CATEGORIES.items():
            category_urls[category_key] = category_info['url']
        
        logger.info(f"Lanka C News: Found {len(category_urls)} categories")
        return category_urls
    
    def get_article_list_url(self, category_url: str, page: int) -> str:
        """
        Generate URL for article list page.
        
        Blogger uses pagination with updated-max parameter.
        For page 1, return the category URL.
        """
        if page == 1:
            return category_url
        
        # Blogger pagination uses ?updated-max parameter
        # This will be handled by get_next_page_url()
        return category_url
    
    def parse_article_list_page(self, html: str, category: str) -> List[ArticleMetadata]:
        """Parse article list page and extract article metadata."""
        soup = BeautifulSoup(html, 'lxml')
        articles = []
        
        # Find post containers
        post_containers = soup.select('.post, .hentry, article')
        
        logger.info(f"Lanka C News {category}: Found {len(post_containers)} post containers")
        
        for container in post_containers:
            try:
                # Find article link - look for link to full post
                link = container.select_one('a[href*="/202"], a.entry-title, h3 a, h2 a')
                if not link:
                    # Try any link in the container
                    link = container.select_one('a[href]')
                
                if not link or not link.get('href'):
                    continue
                
                url = link.get('href')
                
                # Make URL absolute
                if not url.startswith('http'):
                    url = urljoin(self.BASE_URL, url)
                
                # Skip non-article URLs (search, label pages, etc.)
                if '/search/' in url or url == self.BASE_URL + '/':
                    continue
                
                # Get headline
                headline = link.get_text(strip=True)
                if not headline:
                    # Try to find heading
                    title_elem = container.select_one('h1, h2, h3, .entry-title, .post-title')
                    if title_elem:
                        headline = title_elem.get_text(strip=True)
                
                if not headline:
                    continue
                
                article_metadata = ArticleMetadata(
                    url=url,
                    headline=headline,
                    category=category
                )
                
                articles.append(article_metadata)
                
            except Exception as e:
                logger.warning(f"Error parsing article container: {e}")
                continue
        
        logger.info(f"Lanka C News {category}: Extracted {len(articles)} articles from list page")
        return articles
    
    def parse_article_page(self, html: str, metadata: ArticleMetadata) -> Article:
        """Parse individual article page and extract content."""
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Extract headline
            headline = metadata.headline
            headline_elem = soup.select_one('h1, h2, .entry-title, .post-title')
            if headline_elem:
                headline = headline_elem.get_text(strip=True)
            
            # Extract content - Blogger uses .post-body
            content_elem = soup.select_one('.post-body, .entry-content, .post-content')
            if not content_elem:
                raise ValueError(f"No content found for {metadata.url}")
            
            # Extract paragraphs
            paragraphs = content_elem.select('p')
            
            body_paragraphs = []
            for para in paragraphs:
                text = para.get_text(strip=True)
                # Skip short lines (ads, captions)
                if len(text) > 30:
                    body_paragraphs.append(text)
            
            # Fallback to div content if no good paragraphs
            if not body_paragraphs:
                text = content_elem.get_text(strip=True)
                if len(text) > 50:
                    body_paragraphs = [text]
            
            if not body_paragraphs:
                logger.warning(f"Minimal content for {metadata.url}, using headline")
                body_paragraphs = [headline]
            
            body = '\n\n'.join(body_paragraphs)
            
            # Extract date
            date_str = datetime.now().strftime('%Y-%m-%d')
            date_elem = soup.select_one('time, .date, .published, .post-timestamp, .datetime')
            if date_elem:
                date_text = date_elem.get('datetime') or date_elem.get_text(strip=True)
                if date_text:
                    try:
                        # Try to extract date
                        date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_text)
                        if date_match:
                            date_str = date_match.group(0)
                    except:
                        pass
            
            # Extract author
            author = None
            author_elem = soup.select_one('.author, .post-author, [class*="author"]')
            if author_elem:
                author = author_elem.get_text(strip=True)
            
            article = Article(
                headline=headline,
                body=body,
                url=metadata.url,
                category=metadata.category,
                date=date_str,
                author=author,
                source='lankacnews',
                extraction_timestamp=datetime.now().isoformat()
            )
            
            return article
            
        except Exception as e:
            logger.error(f"Error parsing article {metadata.url}: {e}")
            raise
    
    def get_next_page_url(self, current_url: str, html: str, current_page: int) -> Optional[str]:
        """Extract URL for next page of articles."""
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Look for "Older Posts" or next page link
            next_link = soup.select_one('.blog-pager-older-link, a[id*="older"], #blog-pager-older-link')
            if next_link and next_link.get('href'):
                next_url = next_link.get('href')
                if not next_url.startswith('http'):
                    next_url = urljoin(self.BASE_URL, next_url)
                logger.info(f"Found next page URL: {next_url}")
                return next_url
            
            # Check if we found any posts (if < 5, likely last page)
            posts = soup.select('.post, .hentry')
            if len(posts) < 5:
                logger.info(f"Only {len(posts)} posts found, likely last page")
                return None
            
            logger.info("No next page URL found")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting next page URL: {e}")
            return None
