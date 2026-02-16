"""
Gossip Lanka News Scraper

This scraper extracts articles from Gossip Lanka News (https://www.gossiplankanews.com).
The site is built on Blogger/Blogspot platform with AJAX-based "Load More" pagination.
"""

import logging
import re
from typing import List, Optional
from datetime import datetime
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup

from core.base_scraper import BaseScraper, ArticleMetadata, Article

logger = logging.getLogger(__name__)


class GossipLankaScraper(BaseScraper):
    """
    Scraper for Gossip Lanka News website.
    
    Site structure:
    - Built on Blogger/Blogspot platform
    - Uses `.blog-post` containers for articles
    - Categories accessible via /search/label/{category}
    - Pagination uses updated-max parameter with timestamps
    """
    
    BASE_URL = "https://www.gossiplankanews.com"
    SITE_NAME = "gossiplanka"
    
    # Categories from the site navigation
    CATEGORIES = {
        'latest': {
            'name': 'Latest',
            'url': f'{BASE_URL}/',
            'slug': ''
        },
        'political': {
            'name': 'Political',
            'url': f'{BASE_URL}/search/label/Political',
            'slug': 'Political'
        },
        'world': {
            'name': 'World News',
            'url': f'{BASE_URL}/search/label/World%20News',
            'slug': 'World News'
        },
        'cartoon': {
            'name': 'Cartoon',
            'url': f'{BASE_URL}/search/label/Cartoon',
            'slug': 'Cartoon'
        },
        'photo': {
            'name': 'Photo',
            'url': f'{BASE_URL}/search/label/Photo',
            'slug': 'Photo'
        },
        'film': {
            'name': 'Film',
            'url': f'{BASE_URL}/search/label/Film',
            'slug': 'Film'
        },
        'crime': {
            'name': 'Crime',
            'url': f'{BASE_URL}/search/label/Crime',
            'slug': 'Crime'
        },
        'cricket': {
            'name': 'Cricket',
            'url': f'{BASE_URL}/search/label/Cricket',
            'slug': 'Cricket'
        },
        'odd': {
            'name': 'Odd',
            'url': f'{BASE_URL}/search/label/Odd',
            'slug': 'Odd'
        }
    }
    
    def get_categories(self) -> dict:
        """Return available categories for this scraper."""
        return self.CATEGORIES
    
    def get_category_urls(self) -> dict:
        """
        Get mapping of category names to their URLs.
        
        Returns:
            Dict mapping category_name → category_url
        """
        category_urls = {}
        
        for category_key, category_info in self.CATEGORIES.items():
            url = category_info['url']
            category_urls[category_key] = url
        
        logger.info(f"Gossip Lanka: Found {len(category_urls)} categories")
        return category_urls
    
    def get_article_list_url(self, category_url: str, page: int) -> str:
        """
        Generate URL for article list page.
        
        For Gossip Lanka, pagination is handled via updated-max parameter
        which is extracted from the previous page's "Load More" button.
        The first page doesn't need any parameters.
        """
        # First page is just the category URL
        if page == 1:
            return category_url
        
        # For subsequent pages, we rely on get_next_page_url to provide the full URL
        # So we just return the category URL (it won't be used directly)
        return category_url
    
    def parse_article_list_page(self, html: str, category: str) -> List[ArticleMetadata]:
        """
        Parse article list page and extract article metadata.
        
        Args:
            html: HTML content of the list page
            category: Category name
            
        Returns:
            List of ArticleMetadata objects
        """
        soup = BeautifulSoup(html, 'lxml')
        articles = []
        
        # Find all post containers (gossiplankanews.com uses .blog-post)
        post_containers = soup.select('.blog-post')
        
        logger.info(f"Gossip Lanka {category}: Found {len(post_containers)} post containers")
        
        for container in post_containers:
            try:
                # Extract title and URL
                title_elem = container.select_one('h2 a, h3 a, .post-title a, h2, h3')
                if not title_elem:
                    continue
                
                # Get link
                if title_elem.name == 'a':
                    link = title_elem
                else:
                    link = title_elem.select_one('a')
                
                if not link or not link.get('href'):
                    continue
                
                url = link.get('href')
                headline = link.get_text(strip=True)
                
                # Make sure URL is absolute
                if not url.startswith('http'):
                    url = urljoin(self.BASE_URL, url)
                
                # Skip if not a valid article URL
                if not url or self.BASE_URL not in url:
                    continue
                
                # Blogger articles typically have /YYYY/MM/ in URL
                if not re.search(r'/\d{4}/\d{2}/', url):
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
        
        logger.info(f"Gossip Lanka {category}: Extracted {len(articles)} articles from list page")
        return articles
    
    def parse_article_page(self, html: str, metadata: ArticleMetadata) -> Article:
        """
        Parse individual article page and extract content.
        
        Args:
            html: HTML content of article page
            metadata: Article metadata from list page
            
        Returns:
            Article object with full content
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Extract headline (use metadata as fallback)
            headline = metadata.headline
            headline_elem = soup.select_one('h1.post-title, h1, .post-title, h2.post-title')
            if headline_elem:
                headline = headline_elem.get_text(strip=True)
            
            # Extract content
            # Try multiple selectors for content
            content_elem = soup.select_one('.post-body, .post-content, article .content')
            if not content_elem:
                raise ValueError(f"No content found for {metadata.url}")
            
            # Extract paragraphs from content
            paragraphs = content_elem.select('p')
            
            if not paragraphs:
                # If no paragraphs, try to get text from divs
                paragraphs = content_elem.select('div')
            
            # Filter and clean paragraphs
            body_paragraphs = []
            for para in paragraphs:
                text = para.get_text(strip=True)
                # Filter out short paragraphs, ads, and navigation text
                if len(text) > 30:
                    body_paragraphs.append(text)
            
            # If still no content, try getting all text
            if not body_paragraphs:
                text = content_elem.get_text(strip=True)
                # Lower threshold for photo galleries and short articles
                if len(text) > 20:
                    body_paragraphs = [text]
            
            # If still insufficient content, use headline as body (for photo galleries)
            if not body_paragraphs:
                # Photo galleries and image-only posts
                logger.warning(f"Minimal text content for {metadata.url}, using headline as body")
                body_paragraphs = [f"{headline} (Photo Gallery)"]
            
            body = '\n\n'.join(body_paragraphs)
            
            # Extract published date
            date_str = datetime.now().strftime('%Y-%m-%d')
            date_elem = soup.select_one('time, .published, .post-timestamp, abbr[class*="published"]')
            if date_elem:
                date_text = date_elem.get('datetime') or date_elem.get_text(strip=True)
                if date_text:
                    try:
                        # Try parsing ISO format
                        parsed_date = datetime.fromisoformat(date_text.replace('Z', '+00:00'))
                        date_str = parsed_date.strftime('%Y-%m-%d')
                    except:
                        # Try other common formats
                        for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d']:
                            try:
                                parsed_date = datetime.strptime(date_text[:10], fmt)
                                date_str = parsed_date.strftime('%Y-%m-%d')
                                break
                            except:
                                continue
            
            # Extract author if available
            author = None
            author_elem = soup.select_one('.author, .post-author, [rel="author"]')
            if author_elem:
                author = author_elem.get_text(strip=True)
            
            # Create Article object
            article = Article(
                headline=headline,
                body=body,
                url=metadata.url,
                category=metadata.category,
                date=date_str,
                author=author,
                source='gossiplanka',
                extraction_timestamp=datetime.now().isoformat()
            )
            
            return article
            
        except Exception as e:
            logger.error(f"Error parsing article {metadata.url}: {e}")
            raise
    
    def get_next_page_url(self, current_url: str, html: str, current_page: int) -> Optional[str]:
        """
        Extract URL for next page of articles.
        
        Gossip Lanka uses Blogger's AJAX pagination with "Load More" button.
        The next page URL is stored in the data-load attribute.
        
        Args:
            current_url: Current page URL
            html: HTML content of current page
            current_page: Current page number
            
        Returns:
            URL for next page or None if no more pages
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Look for the "Load More" button with data-load attribute
            load_more_btn = soup.select_one('.load-more[data-load], .blog-pager-older-link[data-load], #load-more-link[data-load]')
            
            if load_more_btn and load_more_btn.get('data-load'):
                next_url = load_more_btn.get('data-load')
                
                # Make sure URL is absolute
                if not next_url.startswith('http'):
                    next_url = urljoin(self.BASE_URL, next_url)
                
                logger.info(f"Found next page URL from data-load: {next_url[:100]}...")
                return next_url
            
            # Alternative: Look for standard Blogger pagination link
            older_link = soup.select_one('a.blog-pager-older-link[href]:not([href^="javascript"])')
            if older_link:
                next_url = older_link.get('href')
                if next_url and not next_url.startswith('javascript'):
                    if not next_url.startswith('http'):
                        next_url = urljoin(self.BASE_URL, next_url)
                    logger.info(f"Found next page URL from older link: {next_url[:100]}...")
                    return next_url
            
            # Check if we have any posts on this page
            # If no posts, we've reached the end
            posts = soup.select('.blog-post')
            if len(posts) < 5:
                logger.info(f"Only {len(posts)} posts found, likely last page")
                return None
            
            logger.info("No next page URL found")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting next page URL: {e}")
            return None
