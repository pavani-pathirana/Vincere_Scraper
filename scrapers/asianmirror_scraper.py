"""
Asian Mirror Sinhala Scraper
Website: https://sinhala.asianmirror.lk/

This scraper extracts Sinhala news articles from Asian Mirror.
Article links are found in <li class="listitem"> elements.
"""

import re
import logging
from typing import List, Dict
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from core.base_scraper import BaseScraper, ArticleMetadata, Article

logger = logging.getLogger(__name__)


class AsianMirrorScraper(BaseScraper):
    """Scraper for Asian Mirror Sinhala news website."""
    
    BASE_URL = "https://sinhala.asianmirror.lk"
    SITE_NAME = "asianmirror"
    
    CATEGORIES = {
        'local': {
            'name': 'Local News',
            'url': f'{BASE_URL}/news/local/',
            'slug': 'local'
        },
        'political': {
            'name': 'Political',
            'url': f'{BASE_URL}/news/political/',
            'slug': 'political'
        },
        'international': {
            'name': 'International',
            'url': f'{BASE_URL}/news/international/',
            'slug': 'international'
        },
        'sports': {
            'name': 'Sports',
            'url': f'{BASE_URL}/news/sports/',
            'slug': 'sports'
        },
        'business': {
            'name': 'Business',
            'url': f'{BASE_URL}/news/business/',
            'slug': 'business'
        },
        'crime': {
            'name': 'Crime',
            'url': f'{BASE_URL}/news/crime/',
            'slug': 'crime'
        },
        'special': {
            'name': 'Special Features',
            'url': f'{BASE_URL}/news/special/',
            'slug': 'special'
        },
        'technological': {
            'name': 'Science & Technology',
            'url': f'{BASE_URL}/news/technological/',
            'slug': 'technological'
        }
    }
    
    def get_category_urls(self) -> Dict[str, str]:
        """Get mapping of category names to their URLs."""
        category_urls = {}
        for category_key, category_info in self.CATEGORIES.items():
            category_urls[category_key] = category_info['url']
        
        logger.info(f"Asian Mirror: Found {len(category_urls)} categories")
        return category_urls
    
    def get_article_list_url(self, category_url: str, page_number: int) -> str:
        """Construct URL for a specific page of article list.
        
        Asian Mirror uses query parameter pagination:
        Page 1: Base category URL (no query params)
        Page 2: ?l=9&r=20
        Page 3: ?l=19&r=30
        Page n: ?l=(n-1)*10-1&r=n*10 (for n>1)
        """
        # Page 1 uses the base category URL with no query parameters
        if page_number == 1:
            return category_url
        
        # For subsequent pages, use query parameter pagination
        l_param = (page_number - 1) * 10 - 1
        r_param = page_number * 10
        
        return f"{category_url}?l={l_param}&r={r_param}"
    
    def _is_article_url(self, href: str) -> bool:
        """Check if URL is an article (not category/navigation)."""
        if not href:
            return False
        
        # Must contain /news/
        if '/news/' not in href:
            return False
        
        # Should not end with category names (category pages)
        category_endings = ('/local', '/political', '/sports', '/international', 
                          '/business', '/crime', '/special', '/technological')
        if href.rstrip('/').endswith(category_endings):
            return False
        
        # Should have a slug after category
        parts = href.rstrip('/').split('/')
        # Expected: ['https:', '', 'domain', 'news', 'category', 'slug']
        if len(parts) >= 6:  # Has category and slug
            return True
        
        return False
    
    def parse_article_list_page(self, html: str, category: str) -> List[ArticleMetadata]:
        """Parse article list page and extract article metadata."""
        soup = BeautifulSoup(html, 'lxml')
        articles = []
        
        # Find all article links in the main article list (NOT the breaking news ticker)
        article_links = soup.select('ul#list li a')
        
        logger.info(f"Asian Mirror {category}: Found {len(article_links)} potential links")
        
        for link in article_links:
            try:
                url = link.get('href')
                if not url:
                    continue
                
                # Make absolute URL
                if not url.startswith('http'):
                    url = urljoin(self.BASE_URL, url)
                
                # Skip non-article URLs
                if not self._is_article_url(url):
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
        
        logger.info(f"Asian Mirror {category}: Extracted {len(articles)} articles from list page")
        return articles
    
    def parse_article_page(self, html: str, metadata: ArticleMetadata) -> Article:
        """Parse individual article page and extract full content."""
        soup = BeautifulSoup(html, 'lxml')
        
        # Extract headline
        headline = metadata.headline
        
        # Try to get better headline from page
        title_elem = soup.select_one('h1')
        if title_elem:
            page_headline = title_elem.get_text(strip=True)
            if page_headline:
                headline = page_headline
        
        # Extract content from .col-sm-8 divs
        body = ""
        content_containers = soup.select('.col-sm-8')
        
        if content_containers:
            body_paragraphs = []
            
            for container in content_containers:
                # Get all paragraphs from this container
                paragraphs = container.select('p')
                
                for para in paragraphs:
                    text = para.get_text(strip=True)
                    # Skip short lines, ads, captions
                    if len(text) > 30:
                        body_paragraphs.append(text)
            
            body = '\n\n'.join(body_paragraphs)
        
        if not body:
            logger.warning(f"No content found for {metadata.url}")
            raise ValueError("No content extracted")
        
        # Extract date from .date div
        date_str = None
        date_elem = soup.select_one('.date, .col-6.date')
        if date_elem:
            date_text = date_elem.get_text(strip=True)
            
            # Try to parse Sinhala date format: "2026 පෙබරවාරි මස 20"
            # Extract year, month, day
            import re
            # Try English date format first
            date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_text)
            if date_match:
                date_str = date_match.group(0)
            else:
                # Try to extract year and day from Sinhala text
                year_match = re.search(r'(\d{4})', date_text)
                day_match = re.search(r'(\d{1,2})\s*වන', date_text)
                
                if year_match and day_match:
                    year = year_match.group(1)
                    day = day_match.group(1).zfill(2)
                    
                    # Detect month from Sinhala month names
                    month_map = {
                        'ජනවාරි': '01', 'පෙබරවාරි': '02', 'මාර්තු': '03', 'අප්‍රේල්': '04',
                        'මැයි': '05', 'ජූනි': '06', 'ජූලි': '07', 'අගෝස්තු': '08',
                        'සැප්තැම්බර්': '09', 'ඔක්තෝබර්': '10', 'නොවැම්බර්': '11', 'දෙසැම්බර්': '12'
                    }
                    
                    month = '01'  # Default
                    for sinhala_month, month_num in month_map.items():
                        if sinhala_month in date_text:
                            month = month_num
                            break
                    
                    date_str = f"{year}-{month}-{day}"
        
        # Extract author
        author = None
        author_elem = soup.select_one('.author, .by-author, [class*="author"]')
        if author_elem:
            author = author_elem.get_text(strip=True)
        
        # Generate tags
        tags = [metadata.category]
        
        # Calculate word count
        word_count = len(body.split())
        
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
    
    def get_next_page_url(self, current_url: str, html: str, current_page: int) -> str:
        """Get URL for next page of article list."""
        soup = BeautifulSoup(html, 'lxml')
        
        # Check if next page link exists in pagination
        pagination = soup.select_one('.pagination, ul.pagination, .page-numbers')
        if pagination:
            next_link = pagination.select_one('a[aria-label="Next"], a.next, a[rel="next"]')
            if not next_link:
                logger.info("No next page link found in pagination, reached end")
                return None
        
        # Check if there are articles on current page
        article_links = soup.select('ul#list li a')
        valid_articles = [link for link in article_links if self._is_article_url(link.get('href', ''))]
        
        # Continue if substantial articles found
        if len(valid_articles) >= 5:
            next_page = current_page + 1
            if next_page <= 270:  # Safety limit (site has 268 pages)
                # Construct next page URL with query parameters
                # Extract base URL (without query string)
                base_url = current_url.split('?')[0]
                
                # Calculate l and r parameters for next page
                l_param = (next_page - 1) * 10 - 1 if next_page > 1 else 0
                r_param = next_page * 10
                
                next_url = f"{base_url}?l={l_param}&r={r_param}"
                logger.info(f"Constructed next page URL: {next_url}")
                return next_url
            else:
                logger.warning(f"Reached safety limit of 270 pages")
        else:
            logger.info(f"Only {len(valid_articles)} articles found, likely last page")
        
        return None
