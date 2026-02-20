"""
PC Guide LK Scraper

Scraper for PC Guide (https://www.pcguide.lk/) - Sinhala technology news and guides.
"""

import logging
import re
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from core.base_scraper import BaseScraper, ArticleMetadata, Article

logger = logging.getLogger(__name__)


class PCGuideScraper(BaseScraper):
    """
    Scraper for PC Guide LK technology news website.
    
    Site structure:
    - WordPress platform
    - Main category: /category/tech-news/
    - Article URLs: /{slug}/
    - Content in .entry-content container
    - Focus on technology news, guides, and reviews in Sinhala
    """
    
    BASE_URL = "https://www.pcguide.lk"
    SITE_NAME = "pcguide"
    
    # Force UTF-8 encoding (site doesn't declare charset in Content-Type header)
    RESPONSE_ENCODING = 'utf-8'
    
    CATEGORIES = {
        'tech-news': {
            'name': 'Tech News',
            'url': f'{BASE_URL}/category/tech-news/',
            'slug': 'tech-news'
        }
    }
    
    def get_category_urls(self) -> Dict[str, str]:
        """Get mapping of category names to their URLs."""
        category_urls = {}
        for category_key, category_info in self.CATEGORIES.items():
            category_urls[category_key] = category_info['url']
        
        logger.info(f"PC Guide: Found {len(category_urls)} categories")
        return category_urls
    
    def get_article_list_url(self, category_url: str, page: int) -> str:
        """
        Generate URL for article list page.
        
        WordPress pagination: /category/tech-news/page/N/
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
        
        # PC Guide: article links are in h2/h3 tags in the main content area
        # Find all h2/h3 links that look like articles
        article_links = soup.select('h2 a, h3 a')
        
        logger.info(f"PC Guide {category}: Found {len(article_links)} article links")
        
        for link in article_links:
            try:
                if not link.get('href'):
                    continue
                
                url = link.get('href')
                
                # Make URL absolute
                if not url.startswith('http'):
                    url = urljoin(self.BASE_URL, url)
                
                # Skip category, author, tag pages, and other non-article pages
                if ('/category/' in url or '/tag/' in url or '/author/' in url or 
                    '/buy-and-sell/' in url or '/game-updates/' in url or
                    '/promos-and-giveaways/' in url or '/about-us/' in url or
                    '/contact-us/' in url):
                    continue
                
                # Skip homepage
                if url == self.BASE_URL or url == self.BASE_URL + '/':
                    continue
                
                # Get headline
                headline = link.get_text(strip=True)
                
                if not headline or len(headline) < 10:
                    continue
                
                article_metadata = ArticleMetadata(
                    url=url,
                    headline=headline,
                    category=category
                )
                
                articles.append(article_metadata)
                
            except Exception as e:
                logger.warning(f"Error parsing article link: {e}")
                continue
        
        logger.info(f"PC Guide {category}: Extracted {len(articles)} articles from list page")
        return articles
    
    def parse_article_page(self, html: str, metadata: ArticleMetadata) -> Article:
        """Parse individual article page and extract content."""
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Extract headline
            headline = metadata.headline
            headline_elem = soup.select_one('h1.entry-title, h1, .entry-title, .post-title, .article-title')
            if headline_elem:
                headline = headline_elem.get_text(strip=True)
            
            # Extract content - PC Guide uses .post_content
            content_elem = soup.select_one('.post_content, .post_content_w')
            if not content_elem:
                # Fallback to other common selectors
                content_elem = soup.select_one('.entry-content, .article-content')
            
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
            
            # Calculate word count
            word_count = len(body.split())
            
            # Extract date
            date_str = datetime.now().strftime('%Y-%m-%d')
            date_elem = soup.select_one('time, .entry-date, .date, .published, .post-date')
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
                source='pcguide',
                extraction_timestamp=datetime.now().isoformat(),
                tags=tags if len(tags) > 1 else None,
                word_count=word_count
            )
            
            logger.debug(f"Parsed PC Guide article: {headline[:50]}... ({word_count} words)")
            
            return article
            
        except Exception as e:
            logger.error(f"Error parsing article {metadata.url}: {e}")
            raise
    
    def get_next_page_url(self, current_url: str, html: str, current_page: int) -> Optional[str]:
        """Extract URL for next page of articles."""
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # PC Guide doesn't show pagination links, but pages exist
            # Check if we found articles on current page
            article_links = soup.select('h2 a, h3 a')
            
            # Continue if we found a full page of articles (13 is typical)
            # Stop if page is nearly empty (< 5 articles suggests end of content)
            if len(article_links) >= 5:
                next_page = current_page + 1
                # Safety limit: stop after 200 pages (2600 articles max)
                if next_page <= 200:
                    # Construct next page URL
                    if '/category/tech-news/' in current_url:
                        if current_page == 1:
                            next_url = "https://www.pcguide.lk/category/tech-news/page/2/"
                        else:
                            next_url = f"https://www.pcguide.lk/category/tech-news/page/{next_page}/"
                        logger.info(f"Constructed next page URL: {next_url}")
                        return next_url
                else:
                    logger.warning(f"Reached safety limit of 200 pages, stopping")
                    return None
            
            logger.info(f"Only {len(article_links)} articles found, likely last page")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting next page URL: {e}")
            return None
