"""
Siyatha News Scraper

Scraper for Siyatha News website (https://siyathanews.lk/).
"""

import logging
import re
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from core.base_scraper import BaseScraper, ArticleMetadata, Article

logger = logging.getLogger(__name__)


class SiyathaNewsScraper(BaseScraper):
    """
    Scraper for Siyatha News Sinhala news website.
    
    Site structure:
    - WordPress platform
    - Categories: /archives/category/{category-slug}
    - Article URLs: /archives/{id}
    - Content in article/post container
    """
    
    BASE_URL = "https://siyathanews.lk"
    SITE_NAME = "siyathanews"
    
    CATEGORIES = {
        'local-news': {
            'name': 'Local News',
            'url': f'{BASE_URL}/archives/category/local-news',
            'slug': 'local-news'
        },
        'world-news': {
            'name': 'World News',
            'url': f'{BASE_URL}/archives/category/world-news',
            'slug': 'world-news'
        },
        'business-news': {
            'name': 'Business',
            'url': f'{BASE_URL}/archives/category/business-news',
            'slug': 'business-news'
        },
        'sports-news': {
            'name': 'Sports',
            'url': f'{BASE_URL}/archives/category/sports-news',
            'slug': 'sports-news'
        },
        'entertainmentnews': {
            'name': 'Entertainment',
            'url': f'{BASE_URL}/archives/category/entertainmentnews',
            'slug': 'entertainmentnews'
        }
    }
    
    def get_category_urls(self) -> Dict[str, str]:
        """Get mapping of category names to their URLs."""
        category_urls = {}
        for category_key, category_info in self.CATEGORIES.items():
            category_urls[category_key] = category_info['url']
        
        logger.info(f"Siyatha News: Found {len(category_urls)} categories")
        return category_urls
    
    def get_article_list_url(self, category_url: str, page_number: int) -> str:
        """Construct URL for a specific page of article list."""
        if page_number == 1:
            return category_url
        else:
            # WordPress pagination format
            return f"{category_url}/page/{page_number}/"
    
    def parse_article_list_page(self, html: str, category: str) -> List[ArticleMetadata]:
        """Parse article list page and extract article metadata."""
        soup = BeautifulSoup(html, 'lxml')
        articles = []
        
        # Find all article links using h3 a selector
        article_links = soup.select('h3 a')
        
        logger.info(f"Siyatha News {category}: Found {len(article_links)} article links")
        
        for link in article_links:
            try:
                url = link.get('href')
                if not url:
                    continue
                
                if not url.startswith('http'):
                    url = urljoin(self.BASE_URL, url)
                
                # Skip non-article URLs
                if '/archives/' not in url or '/category/' in url:
                    continue
                
                title = link.get_text(strip=True)
                if not title:
                    continue
                
                article = ArticleMetadata(
                    url=url,
                    headline=title,
                    category=category
                )
                articles.append(article)
                
            except Exception as e:
                logger.warning(f"Error parsing article link: {e}")
                continue
        
        logger.info(f"Siyatha News {category}: Extracted {len(articles)} articles from list page")
        return articles
    
    def parse_article_page(self, html: str, metadata: ArticleMetadata) -> Article:
        """Parse individual article page and extract content."""
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Extract headline
            headline = metadata.headline
            headline_elem = soup.select_one('h1, .entry-title')
            if headline_elem:
                headline = headline_elem.get_text(strip=True)
            
            # Extract content from article or .post
            content_elem = soup.select_one('article, .post')
            
            if not content_elem:
                raise ValueError(f"No content found for {metadata.url}")
            
            # Extract paragraphs
            paragraphs = content_elem.select('p')
            
            body_paragraphs = []
            for para in paragraphs:
                text = para.get_text(strip=True)
                # Skip short lines, ads, captions, VIDEO markers
                if len(text) > 30 and 'VIDEO' not in text:
                    body_paragraphs.append(text)
            
            if not body_paragraphs:
                logger.warning(f"Minimal content for {metadata.url}")
                body_paragraphs = [headline]
            
            body = '\n\n'.join(body_paragraphs)
            
            # Calculate word count
            word_count = len(body.split())
            
            # Extract date
            date_str = datetime.now().strftime('%Y-%m-%d')
            date_elem = soup.select_one('time, .date, .posted-on, .entry-date')
            if date_elem:
                date_text = date_elem.get('datetime') or date_elem.get_text(strip=True)
                if date_text:
                    try:
                        # Try to parse date (format: "February 19, 2026")
                        date_match = re.search(r'(\w+)\s+(\d{1,2}),?\s+(\d{4})', date_text)
                        if date_match:
                            month_name, day, year = date_match.groups()
                            months = {
                                'January': '01', 'February': '02', 'March': '03', 'April': '04',
                                'May': '05', 'June': '06', 'July': '07', 'August': '08',
                                'September': '09', 'October': '10', 'November': '11', 'December': '12'
                            }
                            month = months.get(month_name, '01')
                            date_str = f"{year}-{month}-{day.zfill(2)}"
                    except Exception as e:
                        logger.debug(f"Date parsing error: {e}")
            
            # Extract author
            author = None
            author_elem = soup.select_one('.author, [rel="author"], .by-author')
            if author_elem:
                author = author_elem.get_text(strip=True)
            
            # Generate tags
            tags = [metadata.category]
            # Add VIDEO tag if article contains video
            if '(VIDEO)' in headline or 'VIDEO' in html[:1000]:
                tags.append('video')
            
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
            
            # Look for pagination links (Siyatha News uses aria-label="next-page")
            next_link = soup.select_one('a[aria-label="next-page"], a[rel="next"], .next, .pagination a[rel="next"]')
            if next_link and next_link.get('href'):
                next_url = next_link.get('href')
                if not next_url.startswith('http'):
                    next_url = urljoin(self.BASE_URL, next_url)
                logger.info(f"Found next page URL: {next_url}")
                return next_url
            
            # Fallback: check for page 2, 3, etc links
            page_links = soup.select('a[href*="/page/"]')
            if page_links:
                # Find the next sequential page
                next_page_num = current_page + 1
                for link in page_links:
                    href = link.get('href', '')
                    if f'/page/{next_page_num}' in href:
                        next_url = href
                        if not next_url.startswith('http'):
                            next_url = urljoin(self.BASE_URL, next_url)
                        logger.info(f"Found next page URL via page number: {next_url}")
                        return next_url
            
            # Check if we should continue based on article count
            articles = soup.select('h3 a')
            if len(articles) < 5:
                logger.info(f"Only {len(articles)} articles found, likely last page")
                return None
            
            logger.info("No next page URL found")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting next page URL: {e}")
            return None
