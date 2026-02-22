"""
Tech Sayura Scraper

Scraper for Tech Sayura (https://www.techsayura.com/) - Sinhala technology blog on Blogger platform.
"""

import logging
import re
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from core.base_scraper import BaseScraper, ArticleMetadata, Article

logger = logging.getLogger(__name__)


class TechSayuraScraper(BaseScraper):
    """
    Scraper for Tech Sayura technology blog.
    
    Site structure:
    - Blogger/Blogspot platform
    - Homepage shows latest tech articles
    - Article URLs: /{year}/{month}/{slug}.html (Blogger format)
    - Content in .entry-content container
    - Uses Blogger classes: blog-post, hentry, index-post
    """
    
    BASE_URL = "https://www.techsayura.com"
    SITE_NAME = "techsayura"
    
    CATEGORIES = {
        'all': {
            'name': 'All Tech News',
            'url': f'{BASE_URL}/',
            'slug': 'all'
        }
    }
    
    def get_category_urls(self) -> Dict[str, str]:
        """Get mapping of category names to their URLs."""
        category_urls = {}
        for category_key, category_info in self.CATEGORIES.items():
            category_urls[category_key] = category_info['url']
        
        logger.info(f"Tech Sayura: Found {len(category_urls)} categories")
        return category_urls
    
    def get_article_list_url(self, category_url: str, page: int) -> str:
        """
        Generate URL for article list page.
        
        Blogger pagination: uses continuation tokens or max-results
        For simplicity, we'll use the default homepage and rely on get_next_page_url
        """
        if page == 1:
            return category_url
        
        # Blogger doesn't use simple /page/N/ pagination
        # It uses continuation tokens which we'll extract from the page
        # Just return the base URL for now, get_next_page_url will handle it
        return category_url
    
    def parse_article_list_page(self, html: str, category: str) -> List[ArticleMetadata]:
        """Parse article list page and extract article metadata."""
        soup = BeautifulSoup(html, 'lxml')
        articles = []
        
        # Find post containers - Blogger uses article.blog-post or .hentry
        post_containers = soup.select('article.blog-post, article.hentry, .blog-post, .hentry')
        if not post_containers:
            # Fallback to article tags
            post_containers = soup.select('article')
        
        logger.info(f"Tech Sayura {category}: Found {len(post_containers)} post containers")
        
        for container in post_containers:
            try:
                # Find article link
                # Blogger typically has title links in h2 or h3
                link = container.select_one('h2 a, h3 a, h1 a, .entry-title a, .post-title a')
                if not link:
                    # Try any link with Blogger URL pattern
                    link = container.select_one('a[href*=".html"]')
                
                if not link or not link.get('href'):
                    continue
                
                url = link.get('href')
                
                # Make URL absolute
                if not url.startswith('http'):
                    url = urljoin(self.BASE_URL, url)
                
                # Skip non-article pages (Blogger search, labels, etc.)
                if '/search/' in url or '/p/' in url:
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
                
                # Skip if headline is too short (likely not a real article)
                if len(headline) < 10:
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
        
        logger.info(f"Tech Sayura {category}: Extracted {len(articles)} articles from list page")
        return articles
    
    def parse_article_page(self, html: str, metadata: ArticleMetadata) -> Article:
        """Parse individual article page and extract content."""
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Extract headline
            headline = metadata.headline
            headline_elem = soup.select_one('h1.entry-title, h1.post-title, h1, .entry-title, .post-title')
            if headline_elem:
                headline = headline_elem.get_text(strip=True)
            
            # Extract content - Blogger uses .entry-content or .post-body
            content_elem = soup.select_one('.entry-content, .post-body, .post-content, article .content')
            if not content_elem:
                # Fallback to article tag
                content_elem = soup.select_one('article')
            
            if not content_elem:
                raise ValueError(f"No content found for {metadata.url}")
            
            # Remove unwanted elements (Blogger has many widgets)
            for unwanted in content_elem.select('.ad, .advertisement, .related, .share, .social, script, style, .widget'):
                unwanted.decompose()
            
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
            
            # Calculate word count
            word_count = len(body.split())
            
            # Extract date - Blogger uses time element or abbr.published
            date_str = datetime.now().strftime('%Y-%m-%d')
            date_elem = soup.select_one('time, .published, abbr.published, .entry-date, .post-date, [class*="date"]')
            if date_elem:
                date_text = date_elem.get('datetime') or date_elem.get('title') or date_elem.get_text(strip=True)
                if date_text:
                    try:
                        # Parse ISO datetime format
                        date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_text)
                        if date_match:
                            date_str = date_match.group(0)
                        else:
                            # Try Blogger's common format: MM/DD/YYYY
                            date_match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', date_text)
                            if date_match:
                                month, day, year = date_match.groups()
                                date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    except:
                        pass
            
            # Extract author - Blogger uses .author or .post-author
            author = None
            author_elem = soup.select_one('.author, .post-author, [class*="author"] .fn, [rel="author"]')
            if author_elem:
                author = author_elem.get_text(strip=True)
            
            # Extract tags/labels - Blogger uses rel="tag"
            tags = [metadata.category]
            tag_links = soup.select('a[rel="tag"]') or soup.select('.labels a')
            if tag_links:
                tags.extend([tag.get_text(strip=True) for tag in tag_links[:5]])
            
            article = Article(
                headline=headline,
                body=body,
                url=metadata.url,
                category=metadata.category,
                date=date_str,
                author=author,
                source='techsayura',
                extraction_timestamp=datetime.now().isoformat(),
                tags=tags if len(tags) > 1 else None,
                word_count=word_count
            )
            
            logger.debug(f"Parsed Tech Sayura article: {headline[:50]}... ({word_count} words)")
            
            return article
            
        except Exception as e:
            logger.error(f"Error parsing article {metadata.url}: {e}")
            raise
    
    def get_next_page_url(self, current_url: str, html: str, current_page: int) -> Optional[str]:
        """Extract URL for next page of articles."""
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Blogger pagination - look for "Older Posts" or similar link
            # Common selectors: .blog-pager-older-link, a.blog-pager-older-link, #blog-pager-older-link
            next_link = soup.select_one(
                '.blog-pager-older-link, a.blog-pager-older-link, '
                '#blog-pager-older-link, a[href*="max-results"], '
                '.older-posts a, a:contains("Older")'
            )
            
            if next_link and next_link.get('href'):
                next_url = next_link.get('href')
                # Skip javascript links
                if next_url.startswith('javascript:'):
                    logger.info("Skipping javascript pagination link")
                    return None
                if not next_url.startswith('http'):
                    next_url = urljoin(self.BASE_URL, next_url)
                logger.info(f"Found next page URL: {next_url}")
                return next_url
            
            # Check if we found posts (if < 3 posts, likely last page)
            posts = soup.select('article.blog-post, .blog-post, .hentry')
            if len(posts) < 3:
                logger.info(f"Only {len(posts)} posts found, likely last page")
                return None
            
            logger.info("No next page URL found")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting next page URL: {e}")
            return None
 