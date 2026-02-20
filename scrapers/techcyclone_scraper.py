"""
The Tech Cyclone Scraper

Scraper for The Tech Cyclone (https://thetechcyclone.com/) - Sinhala technology news.
"""

import logging
import re
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from core.base_scraper import BaseScraper, ArticleMetadata, Article

logger = logging.getLogger(__name__)


class TechCycloneScraper(BaseScraper):
    """
    Scraper for The Tech Cyclone technology news website.
    
    Site structure:
    - WordPress platform with Kadence theme
    - Homepage shows latest tech articles
    - Article URLs: /{slug}/
    - Content in .entry-content container
    - Uses custom classes: entry, content-bg, single-entry
    """
    
    BASE_URL = "https://thetechcyclone.com"
    SITE_NAME = "techcyclone"
    
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
        
        logger.info(f"Tech Cyclone: Found {len(category_urls)} categories")
        return category_urls
    
    def get_article_list_url(self, category_url: str, page: int) -> str:
        """
        Generate URL for article list page.
        
        WordPress pagination: /page/N/
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
        
        # Find post containers - Tech Cyclone uses various post classes
        post_containers = soup.select('[class*="post"]')
        if not post_containers:
            # Fallback to article and entry selectors
            post_containers = soup.select('article, .entry')
        
        logger.info(f"Tech Cyclone {category}: Found {len(post_containers)} post containers")
        
        for container in post_containers:
            try:
                # Find article link
                link = container.select_one('h2 a, h1 a, h3 a, .entry-title a')
                if not link:
                    # Try any link within the container
                    link = container.select_one('a[href*="thetechcyclone.com"]')
                
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
                    title_elem = container.select_one('h1, h2, h3, .entry-title')
                    if title_elem:
                        headline = title_elem.get_text(strip=True)
                
                if not headline:
                    continue
                
                # Skip if headline is too short (likely not a real article)
                if len(headline) < 10:
                    continue
                
                # Skip common non-article pages
                if any(term in headline.lower() for term in ['contact us', 'privacy policy', 'about us', 'terms']):
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
        
        logger.info(f"Tech Cyclone {category}: Extracted {len(articles)} articles from list page")
        return articles
    
    def parse_article_page(self, html: str, metadata: ArticleMetadata) -> Article:
        """Parse individual article page and extract content."""
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Extract headline
            headline = metadata.headline
            headline_elem = soup.select_one('h1.entry-title, h1, .entry-title, .post-title')
            if headline_elem:
                headline = headline_elem.get_text(strip=True)
            
            # Extract content - Kadence theme uses .entry-content
            content_elem = soup.select_one('.entry-content, .post-content, .article-content, .content-inner')
            if not content_elem:
                # Fallback to article tag
                content_elem = soup.select_one('article .content, article')
            
            if not content_elem:
                raise ValueError(f"No content found for {metadata.url}")
            
            # Remove unwanted elements
            for unwanted in content_elem.select('.ad, .advertisement, .related, .share, .social, script, style'):
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
            
            # Extract date
            date_str = datetime.now().strftime('%Y-%m-%d')
            date_elem = soup.select_one('time, .entry-date, .date, .published, .post-date, [class*="date"]')
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
            
            # Extract tags
            tags = [metadata.category]
            tag_links = soup.select('a[rel="tag"]') or soup.select('.tags a')
            if tag_links:
                tags.extend([tag.get_text(strip=True) for tag in tag_links[:5]])
            
            article = Article(
                headline=headline,
                body=body,
                url=metadata.url,
                category=metadata.category,
                date=date_str,
                author=author,
                source='techcyclone',
                extraction_timestamp=datetime.now().isoformat(),
                tags=tags if len(tags) > 1 else None,
                word_count=word_count
            )
            
            logger.debug(f"Parsed Tech Cyclone article: {headline[:50]}... ({word_count} words)")
            
            return article
            
        except Exception as e:
            logger.error(f"Error parsing article {metadata.url}: {e}")
            raise
    
    def get_next_page_url(self, current_url: str, html: str, current_page: int) -> Optional[str]:
        """Extract URL for next page of articles."""
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Look for next page link - WordPress/Kadence selectors
            next_link = soup.select_one('.next, .next-page, a[rel="next"], .pagination .next, .nav-links .next, [class*="pag"] a[class*="next"]')
            if next_link and next_link.get('href'):
                next_url = next_link.get('href')
                if not next_url.startswith('http'):
                    next_url = urljoin(self.BASE_URL, next_url)
                logger.info(f"Found next page URL: {next_url}")
                return next_url
            
            # Check if we found posts (if < 5 posts, likely last page)
            posts = soup.select('[class*="post"]')
            if len(posts) < 5:
                logger.info(f"Only {len(posts)} posts found, likely last page")
                return None
            
            logger.info("No next page URL found")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting next page URL: {e}")
            return None
