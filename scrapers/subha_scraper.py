"""
Subha.lk Scraper

Scraper for Subha.lk (https://subha.lk/) - Sinhala astrology and lifestyle blog.
"""

import logging
import re
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urljoin, urlparse, parse_qs

from bs4 import BeautifulSoup

from core.base_scraper import BaseScraper, ArticleMetadata, Article

logger = logging.getLogger(__name__)


class SubhaScraper(BaseScraper):
    """
    Scraper for Subha.lk blog website.
    
    Site structure:
    - Blog platform
    - Main blogs page: /blogs?page=N
    - Individual blog posts: /blogs/{id}
    - Pagination using query parameter ?page=N
    """
    
    BASE_URL = "https://subha.lk"
    SITE_NAME = "subha"
    
    CATEGORIES = {
        'blogs': {
            'name': 'Blogs',
            'url': f'{BASE_URL}/blogs',
            'slug': 'blogs'
        }
    }
    
    def get_category_urls(self) -> Dict[str, str]:
        """Get mapping of category names to their URLs."""
        category_urls = {}
        for category_key, category_info in self.CATEGORIES.items():
            category_urls[category_key] = category_info['url']
        
        logger.info(f"Subha: Found {len(category_urls)} categories")
        return category_urls
    
    def get_article_list_url(self, category_url: str, page_number: int) -> str:
        """Construct URL for a specific page of article list."""
        if page_number == 1:
            return f"{category_url}?page=1"
        else:
            return f"{category_url}?page={page_number}"
    
    def parse_article_list_page(self, html: str, category: str) -> List[ArticleMetadata]:
        """Parse article list page and extract article metadata."""
        soup = BeautifulSoup(html, 'lxml')
        articles = []
        
        # Find all links that point to blog posts
        all_links = soup.select('a[href]')
        
        blog_links = []
        for link in all_links:
            href = link.get('href', '')
            
            # Filter for blog post links (format: /blogs/{id} or https://subha.lk/blogs/{id})
            # Check if it contains /blogs/ and ends with a number (blog ID)
            if '/blogs/' in href:
                # Get the part after /blogs/
                parts = href.split('/blogs/')
                if len(parts) == 2:
                    # Check if the second part is just a number (blog ID)
                    blog_id = parts[1].strip('/')
                    if blog_id.isdigit():
                        # Get the text
                        text = link.get_text(strip=True)
                        
                        # Skip navigation links and very short text
                        if text and len(text) > 15 and 'Next' not in text and text != 'Blogs':
                            blog_links.append((href, text))
        
        logger.info(f"Subha {category}: Found {len(blog_links)} blog post links")
        
        # Remove duplicates (same URL might appear multiple times)
        seen_urls = set()
        for href, title in blog_links:
            if href in seen_urls:
                continue
            seen_urls.add(href)
            
            # Make absolute URL
            url = href if href.startswith('http') else urljoin(self.BASE_URL, href)
            
            article = ArticleMetadata(
                url=url,
                headline=title,
                category=category
            )
            articles.append(article)
        
        logger.info(f"Subha {category}: Extracted {len(articles)} unique articles from list page")
        return articles
    
    def parse_article_page(self, html: str, metadata: ArticleMetadata) -> Article:
        """Parse individual blog page and extract content."""
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Extract headline
            headline = metadata.headline
            headline_elem = soup.select_one('h1')
            if headline_elem:
                headline = headline_elem.get_text(strip=True)
            
            # Extract content
            content_elem = soup.select_one('.content, article, .blog-content, main')
            
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
            
            # If no paragraphs, get all text
            if not body_paragraphs:
                text = content_elem.get_text(strip=True)
                # Split into lines and filter
                lines = [line.strip() for line in text.split('\n') if len(line.strip()) > 30]
                if lines:
                    body_paragraphs = lines
            
            if not body_paragraphs:
                logger.warning(f"Minimal content for {metadata.url}")
                body_paragraphs = [headline]
            
            body = '\n\n'.join(body_paragraphs)
            
            # Calculate word count
            word_count = len(body.split())
            
            # Extract date
            date_str = datetime.now().strftime('%Y-%m-%d')
            date_elem = soup.select_one('time, .date, .publish-date, .published')
            if date_elem:
                date_text = date_elem.get('datetime') or date_elem.get_text(strip=True)
                if date_text:
                    try:
                        # Try to parse ISO format
                        date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_text)
                        if date_match:
                            date_str = date_match.group(0)
                        else:
                            # Try other date patterns
                            date_match = re.search(r'(\d{2})/(\d{2})/(\d{4})', date_text)
                            if date_match:
                                day, month, year = date_match.groups()
                                date_str = f"{year}-{month}-{day}"
                    except Exception as e:
                        logger.debug(f"Date parsing error: {e}")
            
            # Extract author
            author = None
            author_elem = soup.select_one('.author, .author-name, .post-author, [rel="author"]')
            if author_elem:
                author = author_elem.get_text(strip=True)
            
            # Extract tags/categories
            tags = [metadata.category]
            tag_elements = soup.select('.tag, .category, .blog-tag')
            for tag_elem in tag_elements:
                tag_text = tag_elem.get_text(strip=True)
                if tag_text and tag_text not in tags:
                    tags.append(tag_text)
            
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
            
        except Exception as e:
            logger.error(f"Error parsing blog {metadata.url}: {e}")
            raise
    
    def get_next_page_url(self, current_url: str, html: str, current_page: int) -> Optional[str]:
        """Extract URL for next page of blogs."""
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Look for "Next" link - manual search to avoid deprecated :contains selector
            next_link = None
            pagination_links = soup.select('a[href*="page="]')
            for link in pagination_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # Check if it's the next page or "Next" button
                if f'page={current_page + 1}' in href:
                    next_link = link
                    break
                
                if 'Next' in text or '»' in text:
                    next_link = link
                    break
            
            if next_link and next_link.get('href'):
                next_url = next_link.get('href')
                if not next_url.startswith('http'):
                    next_url = urljoin(self.BASE_URL, next_url)
                logger.info(f"Found next page URL: {next_url}")
                return next_url
            
            # Fallback:  construct next page URL manually
            # Check if we found any blog posts
            blog_links = soup.select('a[href*="/blogs/"]')
            if len(blog_links) < 5:
                logger.info(f"Only {len(blog_links)} blog links found, likely last page")
                return None
            
            # Construct next page URL
            next_page_num = current_page + 1
            base_url = current_url.split('?')[0]
            next_url = f"{base_url}?page={next_page_num}"
            logger.info(f"Constructed next page URL: {next_url}")
            return next_url
            
        except Exception as e:
            logger.error(f"Error extracting next page URL: {e}")
            return None
