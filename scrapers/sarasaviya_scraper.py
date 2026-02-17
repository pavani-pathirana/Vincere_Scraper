"""
Sarasaviya Scraper

Scraper for Sarasaviya (https://sarasaviya.lk/) - Sinhala entertainment and cinema magazine.
"""

import logging
import re
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urljoin, quote, unquote

from bs4 import BeautifulSoup

from core.base_scraper import BaseScraper, ArticleMetadata, Article

logger = logging.getLogger(__name__)


class SarasaviyaScraper(BaseScraper):
    """
    Scraper for Sarasaviya entertainment magazine website.
    
    Site structure:
    - WordPress platform
    - Post containers: [class*="post"]
    - Categories via /category/{slug}/
    - URLs may contain URL-encoded Sinhala characters
    - Standard WordPress pagination
    """
    
    BASE_URL = "https://sarasaviya.lk"
    SITE_NAME = "sarasaviya"
    
    CATEGORIES = {
        'news': {
            'name': 'පුවත්',
            'url': f'{BASE_URL}/category/news/',
            'slug': 'news'
        },
        'features': {
            'name': 'විශේෂාංග',
            'url': f'{BASE_URL}/category/features/',
            'slug': 'features'
        },
        'discussions': {
            'name': 'සංවාද',
            'url': f'{BASE_URL}/category/discussions/',
            'slug': 'discussions'
        },
        'critics': {
            'name': 'විචාර',
            'url': f'{BASE_URL}/category/critics/',
            'slug': 'critics'
        },
        '12-frames': {
            'name': 'ලාංකිය සිනමාව',
            'url': f'{BASE_URL}/category/12-frames/',
            'slug': '12-frames'
        },
        '24-frames': {
            'name': 'විදෙස් සිනමා',
            'url': f'{BASE_URL}/category/24-frames/',
            'slug': '24-frames'
        },
        'drama': {
            'name': 'වේදිකාව',
            'url': f'{BASE_URL}/category/drama/',
            'slug': 'drama'
        }
    }
    
    def get_category_urls(self) -> Dict[str, str]:
        """Get mapping of category names to their URLs."""
        category_urls = {}
        for category_key, category_info in self.CATEGORIES.items():
            category_urls[category_key] = category_info['url']
        
        logger.info(f"Sarasaviya: Found {len(category_urls)} categories")
        return category_urls
    
    def get_article_list_url(self, category_url: str, page: int) -> str:
        """
        Generate URL for article list page.
        
        WordPress standard pagination: /category/slug/page/N/
        """
        if page == 1:
            return category_url
        
        # Remove trailing slash for consistency
        base_url = category_url.rstrip('/')
        
        # WordPress pagination
        return f"{base_url}/page/{page}/"
    
    def parse_article_list_page(self, html: str, category: str) -> List[ArticleMetadata]:
        """Parse article list page and extract article metadata."""
        soup = BeautifulSoup(html, 'lxml')
        articles = []
        
        # Find post containers
        post_containers = soup.select('[class*="post"]')
        if not post_containers:
            post_containers = soup.select('article')
        
        logger.info(f"Sarasaviya {category}: Found {len(post_containers)} post containers")
        
        for container in post_containers:
            try:
                # Find article link
                link = container.select_one('a[href*="/202"], a.entry-title, h3 a, h2 a, h1 a')
                if not link:
                    link = container.select_one('a[href]')
                
                if not link or not link.get('href'):
                    continue
                
                url = link.get('href')
                
                # Make URL absolute
                if not url.startswith('http'):
                    url = urljoin(self.BASE_URL, url)
                
                # Skip category, tag, author pages
                if '/category/' in url or '/tag/' in url or '/author/' in url or url == self.BASE_URL + '/':
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
        
        logger.info(f"Sarasaviya {category}: Extracted {len(articles)} articles from list page")
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
            
            # Extract content - WordPress common selectors
            content_elem = soup.select_one('.entry-content, .post-content, .article-content, .content')
            if not content_elem:
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
                source='sarasaviya',
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
            
            # Sarasaviya uses <link rel="next"> in HTML head for pagination
            # This is an SEO tag, not a visible link
            link_tag = soup.select_one('link[rel="next"]')
            if link_tag and link_tag.get('href'):
                next_url = link_tag.get('href')
                if not next_url.startswith('http'):
                    next_url = urljoin(self.BASE_URL, next_url)
                logger.info(f"Found next page URL (SEO tag): {next_url}")
                return next_url
            
            # Fallback: Look for visible next page links
            next_link = soup.select_one('.next, .next-page, a[rel="next"], .pagination .next')
            if next_link and next_link.get('href'):
                next_url = next_link.get('href')
                if not next_url.startswith('http'):
                    next_url = urljoin(self.BASE_URL, next_url)
                logger.info(f"Found next page URL: {next_url}")
                return next_url
            
            # Check if we found any posts
            posts = soup.select('[class*="post"]')
            if len(posts) < 3:
                logger.info(f"Only {len(posts)} posts found, likely last page")
                return None
            
            logger.info("No next page URL found")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting next page URL: {e}")
            return None
