"""
Gagana.lk News Scraper

Scraper for Gagana.lk (https://gagana.lk/) - Sinhala news website.
"""

import logging
import re
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from core.base_scraper import BaseScraper, ArticleMetadata, Article

logger = logging.getLogger(__name__)


class GaganaLkScraper(BaseScraper):
    """
    Scraper for Gagana.lk news website.
    
    Site structure:
    - Post containers: .post-item
    - Categories accessible via /news/{category}
    - Modern site with good structure
    """
    
    BASE_URL = "https://gagana.lk"
    SITE_NAME = "gagana"
    
    CATEGORIES = {
        'srilanka': {
            'name': 'Sri Lanka',
            'url': f'{BASE_URL}/news/srilanka',
            'slug': 'srilanka'
        },
        'politics': {
            'name': 'Politics',
            'url': f'{BASE_URL}/news/politics',
            'slug': 'politics'
        },
        'business': {
            'name': 'Business',
            'url': f'{BASE_URL}/biznews',
            'slug': 'business'
        },
        'gossips': {
            'name': 'Gossip',
            'url': f'{BASE_URL}/news/gossips',
            'slug': 'gossips'
        },
        'sports': {
            'name': 'Sports',
            'url': f'{BASE_URL}/news/sports',
            'slug': 'sports'
        },
        'world': {
            'name': 'World',
            'url': f'{BASE_URL}/news/world',
            'slug': 'world'
        }
    }
    
    def get_category_urls(self) -> Dict[str, str]:
        """Get mapping of category names to their URLs."""
        category_urls = {}
        for category_key, category_info in self.CATEGORIES.items():
            category_urls[category_key] = category_info['url']
        
        logger.info(f"Gagana: Found {len(category_urls)} categories")
        return category_urls
    
    def get_article_list_url(self, category_url: str, page: int) -> str:
        """
        Generate URL for article list page.
        
        Gagana.lk appears to use client-side rendering or AJAX for pagination.
        For now, just return category URL.
        """
        if page == 1:
            return category_url
        
        # Try standard pagination patterns
        if '?' in category_url:
            return f"{category_url}&page={page}"
        else:
            return f"{category_url}?page={page}"
    
    def parse_article_list_page(self, html: str, category: str) -> List[ArticleMetadata]:
        """Parse article list page and extract article metadata."""
        soup = BeautifulSoup(html, 'lxml')
        articles = []
        
        # Find post containers - Gagana uses .a-item class
        post_containers = soup.select('.a-item')
        if not post_containers:
            post_containers = soup.select('[class*="post"]')
        
        logger.info(f"Gagana {category}: Found {len(post_containers)} post containers")
        
        for container in post_containers:
            try:
                # Find article link
                link = container.select_one('a[href*="/article/"]')
                if not link:
                    link = container.select_one('a[href]')
                
                if not link or not link.get('href'):
                    continue
                
                url = link.get('href')
                
                # Make URL absolute
                if not url.startswith('http'):
                    url = urljoin(self.BASE_URL, url)
                
                # Skip non-article URLs
                if '/article/' not in url:
                    continue
                
                # Get headline (from link text or nearby heading)
                headline = link.get_text(strip=True)
                if not headline:
                    title_elem = container.select_one('h1, h2, h3, h4, h5')
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
        
        logger.info(f"Gagana {category}: Extracted {len(articles)} articles from list page")
        return articles
    
    def parse_article_page(self, html: str, metadata: ArticleMetadata) -> Article:
        """Parse individual article page and extract content."""
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Extract headline
            headline = metadata.headline
            headline_elem = soup.select_one('h1, .article-title, .entry-title')
            if headline_elem:
                headline = headline_elem.get_text(strip=True)
            
            # Extract content - Gagana uses .ds-content
            content_elem = soup.select_one('.ds-content')
            if not content_elem:
                # Fallback to other selectors
                content_elem = soup.select_one('.article-content, .entry-content, .post-content')
            
            if not content_elem:
                raise ValueError(f"No content found for {metadata.url}")
            
            # Extract paragraphs
            paragraphs = content_elem.select('p')
            
            body_paragraphs = []
            for para in paragraphs:
                text = para.get_text(strip=True)
                if len(text) > 30:
                    body_paragraphs.append(text)
            
            # Fallback to all text if no good paragraphs
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
            date_elem = soup.select_one('time, .date, .published, [class*="date"]')
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
            author_elem = soup.select_one('.author, .by-line, [class*="author"]')
            if author_elem:
                author = author_elem.get_text(strip=True)
            
            article = Article(
                headline=headline,
                body=body,
                url=metadata.url,
                category=metadata.category,
                date=date_str,
                author=author,
                source='gagana',
                extraction_timestamp=datetime.now().isoformat()
            )
            
            return article
            
        except Exception as e:
            logger.error(f"Error parsing article {metadata.url}: {e}")
            raise
    
    def get_next_page_url(self, current_url: str, html: str, current_page: int) -> Optional[str]:
        """
        Extract URL for next page of articles.
        
        NOTE: Gagana.lk uses JavaScript/AJAX for pagination ("Load More" button).
        Server-side pagination parameters (?page=, ?before=, ?offset=) are ignored.
        Only the first ~36 articles per category are available without JavaScript execution.
        
        To get more articles, would need Selenium/Playwright for JavaScript rendering.
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Check if we found articles
            posts = soup.select('.a-item')
            
            # Gagana doesn't support server-side pagination
            # Each category only returns ~36 articles without JavaScript
            logger.info(f"Gagana.lk limitation: Only first page available per category (~{len(posts)} articles)")
            logger.info("Server-side pagination not supported - site uses JavaScript 'Load More' button")
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting next page URL: {e}")
            return None
