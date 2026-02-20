"""
Colombo Times Sinhala Scraper

Scraper for Colombo Times Sinhala edition (https://colombotimes.lk/sinhala/).
"""

import logging
import re
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from core.base_scraper import BaseScraper, ArticleMetadata, Article

logger = logging.getLogger(__name__)


class ColomboTimesScraper(BaseScraper):
    """
    Scraper for Colombo Times Sinhala news website.
    
    Site structure:
    - Custom platform
    - Categories: /sinhala/{category}
    - Pagination: ?q={page_number}
    - Article URLs: /sinhala/{slug}.html
    - Content in .entry-content container
    """
    
    BASE_URL = "https://colombotimes.lk"
    SITE_NAME = "colombotimes"
    
    CATEGORIES = {
        'local': {
            'name': 'Local News',
            'url': f'{BASE_URL}/sinhala/local',
            'slug': 'local'
        },
        'world': {
            'name': 'World News',
            'url': f'{BASE_URL}/sinhala/world',
            'slug': 'world'
        },
        'political': {
            'name': 'Political',
            'url': f'{BASE_URL}/sinhala/political',
            'slug': 'political'
        },
        'sports': {
            'name': 'Sports',
           'url': f'{BASE_URL}/sinhala/sports',
            'slug': 'sports'
        },
        'entertainment': {
            'name': 'Entertainment',
            'url': f'{BASE_URL}/sinhala/entertainment',
            'slug': 'entertainment'
        }
    }
    
    def get_category_urls(self) -> Dict[str, str]:
        """Get mapping of category names to their URLs."""
        category_urls = {}
        for category_key, category_info in self.CATEGORIES.items():
            category_urls[category_key] = category_info['url']
        
        logger.info(f"Colombo Times: Found {len(category_urls)} categories")
        return category_urls
    
    def get_article_list_url(self, category_url: str, page_number: int) -> str:
        """Construct URL for a specific page of article list."""
        if page_number == 1:
            return category_url
        else:
            return f"{category_url}?q={page_number}"
    
    def parse_article_list_page(self, html: str, category: str) -> List[ArticleMetadata]:
        """Parse article list page and extract article metadata."""
        soup = BeautifulSoup(html, 'lxml')
        articles = []
        
        # Find all article containers using .post selector
        post_containers = soup.select('.post')
        
        logger.info(f"Colombo Times {category}: Found {len(post_containers)} article containers")

        for container in post_containers:
            try:
                # Get article link from h2 or h3 (title links only, not image links)
                link = container.select_one('h2 a, h3 a')
                if not link:
                    continue
                
                url = link.get('href')
                if not url or not url.endswith('.html'):
                    continue
                
                if not url.startswith('http'):
                    url = urljoin(self.BASE_URL, url)
                
                # Get title from link text
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
                logger.warning(f"Error parsing article container: {e}")
                continue
        
        logger.info(f"Colombo Times {category}: Extracted {len(articles)} articles from list page")
        return articles
    
    def parse_article_page(self, html: str, metadata: ArticleMetadata) -> Article:
        """Parse individual article page and extract content.
        
        Note: Colombo Times does NOT have dedicated article pages.
        Fetching an article URL returns the same category listing page.
        We extract all meaningful paragraphs from the page instead.
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # No dedicated article page - get headline from h1 if available
            headline = metadata.headline
            h1 = soup.select_one('h1')
            if h1:
                headline = h1.get_text(strip=True)
            
            # Extract all paragraphs with meaningful content
            paragraphs = soup.select('p')
            body_paragraphs = []
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 50:
                    body_paragraphs.append(text)
            
            if not body_paragraphs:
                body_paragraphs = [headline]
            
            body = '\n\n'.join(body_paragraphs)
            word_count = len(body.split())
            
            # Extract date
            date_str = datetime.now().strftime('%Y-%m-%d')
            date_elem = soup.select_one('time, .date, .publish-date, .post-date')
            if date_elem:
                date_text = date_elem.get('datetime') or date_elem.get_text(strip=True)
                if date_text:
                    date_match = re.search(r'(\d{1,2})\s+(\w+)\s+(\d{4})', date_text)
                    if date_match:
                        day, month_name, year = date_match.groups()
                        months = {
                            'January': '01', 'February': '02', 'March': '03', 'April': '04',
                            'May': '05', 'June': '06', 'July': '07', 'August': '08',
                            'September': '09', 'October': '10', 'November': '11', 'December': '12'
                        }
                        month = months.get(month_name, '01')
                        date_str = f'{year}-{month}-{day.zfill(2)}'
            
            return Article(
                url=metadata.url,
                headline=headline,
                body=body,
                date=date_str,
                source=self.website_name,
                category=metadata.category,
                author=None,
                tags=[metadata.category],
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
            
            # Check if there are enough articles to continue
            posts = soup.select('.post')
            if len(posts) < 3:
                logger.info(f"Only {len(posts)} posts found, stopping pagination")
                return None
            
            # Construct next page URL using ?q= parameter
            base_url = current_url.split('?')[0]
            next_url = f"{base_url}?q={current_page + 1}"
            logger.info(f"Next page URL: {next_url}")
            return next_url
            
        except Exception as e:
            logger.error(f"Error extracting next page URL: {e}")
            return None
