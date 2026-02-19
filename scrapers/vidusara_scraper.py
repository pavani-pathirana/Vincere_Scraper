"""
Vidusara Scraper

Scraper for Vidusara (https://www.vidusara.lk/) - Sinhala science and technology magazine.
"""

import logging
import re
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from core.base_scraper import BaseScraper, ArticleMetadata, Article

logger = logging.getLogger(__name__)


class VidusaraScraper(BaseScraper):
    """
    Scraper for Vidusara science magazine website.
    
    Site structure:
    - WordPress platform
    - Categories via /category/{slug}/
    - Article URLs: /{category-slug}/{article-id}/
    - Content in .entry-content container
    - Focus on science, technology, and educational content
    """
    
    BASE_URL = "https://www.vidusara.lk"
    SITE_NAME = "vidusara"
    
    CATEGORIES = {
        'science-news': {
            'name': 'විදු පුවත්',
            'url': f'{BASE_URL}/category/science-news/',
            'slug': 'science-news'
        },
        'viduhala': {
            'name': 'විදුසර විදුහල',
            'url': f'{BASE_URL}/category/viduhala/',
            'slug': 'viduhala'
        },
        'entertainment': {
            'name': 'වින්දන',
            'url': f'{BASE_URL}/category/entertainment/',
            'slug': 'entertainment'
        },
        'features': {
            'name': 'Features',
            'url': f'{BASE_URL}/category/features/',
            'slug': 'features'
        },
        'technology': {
            'name': 'තාක්ෂණ',
            'url': f'{BASE_URL}/category/features/technology/',
            'slug': 'features/technology'
        },
        'physics': {
            'name': 'භෞතික විද්\u200dයා',
            'url': f'{BASE_URL}/category/features/physics/',
            'slug': 'features/physics'
        },
        'space': {
            'name': 'අභ්\u200dයවකාශ',
            'url': f'{BASE_URL}/category/features/space/',
            'slug': 'features/space'
        },
        'health': {
            'name': 'Health',
            'url': f'{BASE_URL}/category/features/health/',
            'slug': 'features/health'
        },
        'environmental': {
            'name': 'Environmental',
            'url': f'{BASE_URL}/category/features/environmental/',
            'slug': 'features/environmental'
        },
        'science-fiction': {
            'name': 'විද්\u200dයා ප්\u200dරබන්ධ',
            'url': f'{BASE_URL}/category/entertainment/science-fiction/',
            'slug': 'entertainment/science-fiction'
        }
    }
    
    def get_category_urls(self) -> Dict[str, str]:
        """Get mapping of category names to their URLs."""
        category_urls = {}
        for category_key, category_info in self.CATEGORIES.items():
            category_urls[category_key] = category_info['url']
        
        logger.info(f"Vidusara: Found {len(category_urls)} categories")
        return category_urls
    
    def get_article_list_url(self, category_url: str, page: int) -> str:
        """
        Generate URL for article list page.
        
        WordPress pagination: /category/slug/page/N/
        """
        if page == 1:
            return category_url
        
        # Remove trailing slash
        base_url = category_url.rstrip('/')
        
        # WordPress pagination
        return f"{base_url}/page/{page}/"
    
    def parse_article_list_page(self, html: str, category: str) -> List[ArticleMetadata]:
        """Parse article list page and extract article metadata."""
        soup = BeautifulSoup(html, 'lxml')
        articles = []
        
        # Find post containers - Vidusara doesn't use <article> tags on category pages
        # Instead it uses divs with "post" in class name
        post_containers = soup.select('[class*="post"]')
        if not post_containers:
            # Fallback to article tags (used on individual pages)
            post_containers = soup.select('article')
        
        logger.info(f"Vidusara {category}: Found {len(post_containers)} post containers")
        
        for container in post_containers:
            try:
                # Find article link - various possible locations
                link = container.select_one('a[href*="/science-news/"], a[href*="/viduhala/"], a[href*="/entertainment/"], a[href*="/features/"]')
                if not link:
                    # Try any link with year in URL (e.g., /2026/)
                    link = container.select_one('a[href*="/202"]')
                if not link:
                    # Try h2/h3 links
                    link = container.select_one('h2 a, h3 a, h1 a')
                
                if not link or not link.get('href'):
                    continue
                
                url = link.get('href')
                
                # Make URL absolute
                if not url.startswith('http'):
                    url = urljoin(self.BASE_URL, url)
                
                # Skip category, author, tag pages
                if '/category/' in url or '/tag/' in url or '/author/' in url:
                    continue
                
                # Skip homepage
                if url == self.BASE_URL or url == self.BASE_URL + '/':
                    continue
                
                # Get headline
                headline = link.get_text(strip=True)
                if not headline:
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
        
        logger.info(f"Vidusara {category}: Extracted {len(articles)} articles from list page")
        return articles
    
    def parse_article_page(self, html: str, metadata: ArticleMetadata) -> Article:
        """Parse individual article page and extract content."""
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Extract headline
            headline = metadata.headline
            headline_elem = soup.select_one('h1, .entry-title, .post-title, .article-title')
            if headline_elem:
                headline = headline_elem.get_text(strip=True)
            
            # Extract content - Vidusara uses .entry-content
            content_elem = soup.select_one('.inner-post-entry.entry-content, .entry-content, .post-content, .article-content')
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
            
            # Fallback to all text if no good paragraphs
            if not body_paragraphs:
                text = content_elem.get_text(strip=True)
                if len(text) > 50:
                    body_paragraphs = [text]
            
            if not body_paragraphs:
                logger.warning(f"Minimal content for {metadata.url}")
                body_paragraphs = [headline]
            
            body = '\n\n'.join(body_paragraphs)
            
            # Extract date
            date_str = datetime.now().strftime('%Y-%m-%d')
            date_elem = soup.select_one('time, .date, .published, .entry-date, .post-date')
            if date_elem:
                date_text = date_elem.get('datetime') or date_elem.get_text(strip=True)
                if date_text:
                    try:
                        # Parse ISO datetime format
                        date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_text)
                        if date_match:
                            date_str = date_match.group(0)
                    except:
                        pass
            
            # Extract author
            author = None
            author_elem = soup.select_one('.author, .by-line, .post-author, [class*="author"]')
            if author_elem:
                author = author_elem.get_text(strip=True)
            
            article = Article(
                headline=headline,
                body=body,
                url=metadata.url,
                category=metadata.category,
                date=date_str,
                author=author,
                source='vidusara',
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
            
            # Look for next page link - WordPress selectors
            next_link = soup.select_one('.next, .next-page, a[rel="next"], .pagination .next, .nav-links .next')
            if next_link and next_link.get('href'):
                next_url = next_link.get('href')
                if not next_url.startswith('http'):
                    next_url = urljoin(self.BASE_URL, next_url)
                logger.info(f"Found next page URL: {next_url}")
                return next_url
            
            # Check if we found posts (if < 3 posts, likely last page)
            posts = soup.select('article')
            if len(posts) < 3:
                logger.info(f"Only {len(posts)} posts found, likely last page")
                return None
            
            logger.info("No next page URL found")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting next page URL: {e}")
            return None
