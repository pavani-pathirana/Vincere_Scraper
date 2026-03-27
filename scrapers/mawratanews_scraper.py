"""
Mawrata News Scraper

Scraper for Mawrata News (https://sinhala.mawratanews.lk/) - Sinhala news website.
"""

import logging
import re
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from core.base_scraper import BaseScraper, ArticleMetadata, Article

logger = logging.getLogger(__name__)


class MawrataNewsScraper(BaseScraper):
    """
    Scraper for Mawrata News website.
    
    Site structure:
    - WordPress platform with JNews theme
    - Post containers: article.jeg_post, .jeg_pl_lg_2
    - Various category pages
    - Standard WordPress pagination
    """
    
    BASE_URL = "https://sinhala.mawratanews.lk"
    SITE_NAME = "mawratanews"
    
    # Categories using /category/{name}/ URL format
    CATEGORIES = {
        'astrology': {
            'name': 'Astrology',
            'url': f'{BASE_URL}/category/astrology/',
            'slug': 'astrology'
        },
        'heart': {
            'name': 'Heart',
            'url': f'{BASE_URL}/category/heart/',
            'slug': 'heart'
        },
        'politics': {
            'name': 'Politics',
            'url': f'{BASE_URL}/category/politics/',
            'slug': 'politics'
        },
        'exclusive': {
            'name': 'Exclusive',
            'url': f'{BASE_URL}/category/exclusive/',
            'slug': 'exclusive'
        },
        'local': {
            'name': 'Local',
            'url': f'{BASE_URL}/category/local/',
            'slug': 'local'
        },
        'world': {
            'name': 'World',
            'url': f'{BASE_URL}/category/world/',
            'slug': 'world'
        },
        'sports': {
            'name': 'Sports',
            'url': f'{BASE_URL}/category/sports/',
            'slug': 'sports'
        },
        'entertainment': {
            'name': 'Entertainment',
            'url': f'{BASE_URL}/category/entertainment/',
            'slug': 'entertainment'
        }
    }
    
    def get_category_urls(self) -> Dict[str, str]:
        """Get mapping of category names to their URLs."""
        category_urls = {}
        for category_key, category_info in self.CATEGORIES.items():
            category_urls[category_key] = category_info['url']
        
        logger.info(f"Mawrata News: Found {len(category_urls)} categories")
        return category_urls
    
    def get_article_list_url(self, category_url: str, page: int) -> str:
        """
        Generate URL for article list page.
        
        WordPress pagination: /category/page/N/
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
        
        # Find post containers - JNews theme specific
        post_containers = soup.select('article.jeg_post, article[class*="jeg_"]')
        if not post_containers:
            # Fallback to generic selectors
            post_containers = soup.select('article, [class*="post"]')
        
        logger.info(f"Mawrata News {category}: Found {len(post_containers)} post containers")
        
        for container in post_containers:
            try:
                # Find article link - JNews stores links in various places
                link = container.select_one('a[href*="/202"], a.jeg_post_title, h3 a, h2 a')
                if not link:
                    link = container.select_one('a[href]')
                
                if not link or not link.get('href'):
                    continue
                
                url = link.get('href')
                
                # Make URL absolute
                if not url.startswith('http'):
                    url = urljoin(self.BASE_URL, url)
                
                # Skip category, tag pages
                if '/category/' in url or '/tag/' in url or url == self.BASE_URL + '/':
                    continue
                
                # Get headline
                headline = link.get_text(strip=True)
                if not headline:
                    title_elem = container.select_one('h1, h2, h3, .jeg_post_title, .entry-title')
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
        
        logger.info(f"Mawrata News {category}: Extracted {len(articles)} articles from list page")
        return articles
    
    def parse_article_page(self, html: str, metadata: ArticleMetadata) -> Article:
        """Parse individual article page and extract content."""
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Extract headline
            headline = metadata.headline
            headline_elem = soup.select_one('h1, .jeg_post_title, .entry-title, .article-title')
            if headline_elem:
                headline = headline_elem.get_text(strip=True)
            
            # Extract content - JNews and WordPress selectors
            content_elem = soup.select_one('.entry-content, .jeg_maincontent, .content-inner, .post-content')
            if not content_elem:
                content_elem = soup.select_one('article')
            
            if not content_elem:
                raise ValueError(f"No content found for {metadata.url}")
            
            # Extract paragraphs
            paragraphs = content_elem.select('p')
            
            body_paragraphs = []
            for para in paragraphs:
                text = para.get_text(strip=True)
                # Skip short lines
                if len(text) > 30:
                    body_paragraphs.append(text)
            
            # Fallback to all text
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
        
            # Extract date
            date_str = datetime.now().strftime('%Y-%m-%d')
            date_elem = soup.select_one('time, .date, .published, .jeg_meta_date, .post-date')
            if date_elem:
                date_text = date_elem.get('datetime') or date_elem.get_text(strip=True)
                if date_text:
                    try:
                        date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_text)
                        if date_match:
                            date_str = date_match.group(0)
                    except:
                        pass
            
            # Extract author
            author = None
            author_elem = soup.select_one('.author, .jeg_meta_author, .post-author, [class*="author"]')
            if author_elem:
                author = author_elem.get_text(strip=True)
            
            article = Article(
                headline=headline,
                body=body,
                url=metadata.url,
                category=metadata.category,
                date=date_str,
                author=author,
                source='mawratanews',
                               word_count=word_count,
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
            
            # Look for next page link - JNews theme uses specific classes
            # Try JNews-specific selector first
            next_link = soup.select_one('a.page_nav.next, a.page_number_link.next')
            if next_link and next_link.get('href'):
                next_url = next_link.get('href')
                if not next_url.startswith('http'):
                    next_url = urljoin(self.BASE_URL, next_url)
                logger.info(f"Found next page URL (JNews): {next_url}")
                return next_url
            
            # Fallback: Generic WordPress and other selectors
            next_link = soup.select_one('.next, .next-page, a[rel="next"], .jeg_navigation .next')
            if next_link and next_link.get('href'):
                next_url = next_link.get('href')
                if not next_url.startswith('http'):
                    next_url = urljoin(self.BASE_URL, next_url)
                logger.info(f"Found next page URL: {next_url}")
                return next_url
            
            # Check if we found posts
            posts = soup.select('article')
            if len(posts) < 3:
                logger.info(f"Only {len(posts)} posts found, likely last page")
                return None
            
            logger.info("No next page URL found")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting next page URL: {e}")
            return None
