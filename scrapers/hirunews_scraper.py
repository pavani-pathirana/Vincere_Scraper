"""
HiruNewsScraper - Concrete scraper for Hiru News Sinhala website.

Website: https://www.hirunews.lk
Pattern: Massive archive with segment/page-based pagination
Categories: Multiple categories with deep article listings
"""

import logging
import re
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urljoin, urlparse, parse_qs

from bs4 import BeautifulSoup

from core.base_scraper import BaseScraper, ArticleMetadata, Article


logger = logging.getLogger(__name__)


class HiruNewsScraper(BaseScraper):
    """
    Concrete scraper for Hiru News Sinhala website.
    
    URL Structure:
    - Homepage: https://www.hirunews.lk
    - Category: https://www.hirunews.lk/[category-slug]/
    - Pagination: https://www.hirunews.lk/[category-slug]/page/[page_num]/
    - Article: https://www.hirunews.lk/[article-id]/[article-slug].html
    
    Hiru News has a massive archive with:
    - Segment-based pagination (page/[num]/)
    - AJAX-based infinite scroll in some sections (fallback to page-based)
    - Category-specific layouts
    
    Main Categories:
    - Local News (දේශීය)
    - International (විදේශීය)
    - Sports (ක්‍රීඩා)
    - Business (ව්‍යාපාර)
    - Entertainment (විනෝදාස්වාදය)
    - Politics (දේශපාලන)
    - Crime (අපරාධ)
    - Features (විශේෂාංග)
    - Tech (තාක්ෂණය)
    - Health (සෞඛ්‍ය)
    """
    
    BASE_URL = 'https://www.hirunews.lk'
    
    # Category slug mapping (adjust based on actual site structure)
    CATEGORIES = {
        'local': {
            'slug': 'local-news',
            'name': 'දේශීය'
        },
        'international': {
            'slug': 'world',
            'name': 'විදේශීය'
        },
        'sports': {
            'slug': 'sports',
            'name': 'ක්‍රීඩා'
        },
        'business': {
            'slug': 'business',
            'name': 'ව්‍යාපාර'
        },
        'entertainment': {
            'slug': 'entertainment',
            'name': 'විනෝදාස්වාදය'
        },
        'politics': {
            'slug': 'politics',
            'name': 'දේශපාලන'
        },
        'crime': {
            'slug': 'crime',
            'name': 'අපරාධ'
        },
        'features': {
            'slug': 'features',
            'name': 'විශේෂාංග'
        },
        'tech': {
            'slug': 'technology',
            'name': 'තාක්ෂණය'
        },
        'health': {
            'slug': 'health',
            'name': 'සෞඛ්‍ය'
        }
    }
    
    def get_category_urls(self) -> Dict[str, str]:
        """
        Get mapping of category names to their URLs.
        
        Returns:
            Dict mapping category_name → category_url
        """
        category_urls = {}
        
        for category_key, category_info in self.CATEGORIES.items():
            slug = category_info['slug']
            url = f"{self.BASE_URL}/{slug}/"
            category_urls[category_key] = url
        
        logger.info(f"Hiru News: Found {len(category_urls)} categories")
        return category_urls
    
    def get_article_list_url(self, category_url: str, page: int = 1) -> str:
        """
        Build URL for a specific page of article list.
        
        Hiru News uses segment-based pagination: /[category]/page/[num]/
        
        Args:
            category_url: Base URL for category (e.g., /local-news/)
            page: Page number (1-indexed)
        
        Returns:
            Full URL for article list page
        """
        if page == 1:
            # First page is the category URL itself
            return category_url
        
        # Ensure category_url ends with /
        if not category_url.endswith('/'):
            category_url += '/'
        
        # Remove trailing slash temporarily
        base = category_url.rstrip('/')
        
        # Add page segment: /page/[num]/
        paginated_url = f"{base}/page/{page}/"
        
        return paginated_url
    
    def parse_article_list_page(self, html: str, category: str) -> List[ArticleMetadata]:
        """
        Parse article list page and extract article metadata.
        
        Hiru News structure (typical patterns):
        - Articles in <article class="post"> or <div class="news-item">
        - Link: <a href="/[id]/[slug].html">
        - Headline: <h2 class="entry-title"> or <h3>
        - Date: <time> or <span class="date">
        - Excerpt: <div class="entry-excerpt"> or <p>
        
        Args:
            html: HTML content of list page
            category: Category name
        
        Returns:
            List of ArticleMetadata objects
        """
        soup = BeautifulSoup(html, 'lxml')
        articles = []
        
        # Try multiple selectors for Hiru News
        article_containers = (
            soup.select('article.post') or
            soup.select('article.news-item') or
            soup.select('div.post') or
            soup.select('div.news-item') or
            soup.select('article') or
            soup.select('div[class*="post"]')
        )
        
        if not article_containers:
            logger.warning(f"No article containers found in Hiru News {category} list page")
            # Fallback: look for any links ending with .html
            content_area = soup.select_one('main') or soup.select_one('.content') or soup
            article_containers = content_area.select('a[href$=".html"]')
        
        for container in article_containers:
            try:
                # Extract article link
                if container.name == 'a':
                    link_elem = container
                else:
                    link_elem = container.select_one('a[href$=".html"]') or container.select_one('a')
                
                if not link_elem:
                    continue
                
                article_url = link_elem.get('href', '')
                
                # Make absolute URL
                if article_url.startswith('/'):
                    article_url = urljoin(self.BASE_URL, article_url)
                elif not article_url.startswith('http'):
                    article_url = urljoin(self.BASE_URL, article_url)
                
                # Skip if not an article URL (should end with .html)
                if not article_url.endswith('.html'):
                    continue
                
                # Extract headline
                headline_elem = (
                    container.select_one('h2.entry-title') or
                    container.select_one('h2') or
                    container.select_one('h3') or
                    container.select_one('.title') or
                    container.select_one('.headline') or
                    link_elem
                )
                
                headline = headline_elem.get_text(strip=True) if headline_elem else 'Untitled'
                
                # Skip if headline is empty or too short (minimum 10 chars)
                if len(headline) < 10:
                    continue
                
                # Extract date (optional)
                date_elem = (
                    container.select_one('time') or
                    container.select_one('.date') or
                    container.select_one('.published') or
                    container.select_one('span[class*="date"]') or
                    container.select_one('.entry-date')
                )
                
                date_str = None
                if date_elem:
                    # Try datetime attribute first
                    date_str = date_elem.get('datetime') or date_elem.get_text(strip=True)
                
                # Extract excerpt (optional)
                excerpt_elem = (
                    container.select_one('.entry-excerpt') or
                    container.select_one('.excerpt') or
                    container.select_one('p')
                )
                
                excerpt = excerpt_elem.get_text(strip=True) if excerpt_elem else None
                
                # Create metadata
                metadata = ArticleMetadata(
                    url=article_url,
                    headline=self.text_processor.process_headline(headline),
                    category=category,
                    date=date_str,
                    excerpt=excerpt
                )
                
                articles.append(metadata)
                
            except Exception as e:
                logger.warning(f"Failed to parse article container in Hiru News list: {e}")
                continue
        
        logger.info(f"Hiru News {category}: Extracted {len(articles)} articles from list page")
        
        return articles
    
    def parse_article_page(self, html: str, metadata: ArticleMetadata) -> Article:
        """
        Parse individual article page and extract full content.
        
        Hiru News article structure (typical):
        - Headline: <h1 class="entry-title"> or <h1>
        - Body: <div class="entry-content"> or <article class="content">
        - Date: <time class="entry-date"> or <span class="date">
        - Author: <span class="author"> or <a rel="author">
        
        Args:
            html: HTML content of article page
            metadata: Metadata from list page
        
        Returns:
            Complete Article object
        
        Raises:
            ValueError: If article structure is invalid/unexpected
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # Extract headline
        headline_elem = (
            soup.select_one('h1.entry-title') or
            soup.select_one('article h1') or
            soup.select_one('.article-title h1') or
            soup.select_one('h1')
        )
        
        if not headline_elem:
            # Fallback to metadata headline
            headline = metadata.headline
            logger.warning(f"Headline not found in article page, using metadata: {headline[:50]}...")
        else:
            headline = self.text_processor.process_headline(headline_elem.get_text())
        
        # Extract body (main content)
        body_elem = (
            soup.select_one('div.entry-content') or
            soup.select_one('div.article-content') or
            soup.select_one('article .content') or
            soup.select_one('.post-content') or
            soup.select_one('#content')
        )
        
        if not body_elem:
            raise ValueError(f"Article body not found for: {metadata.url}")
        
        # Remove unwanted elements (ads, related articles, social buttons)
        for unwanted in body_elem.select('.advertisement, .ad, .related-posts, .social-share, script, style'):
            unwanted.decompose()
        
        # Get HTML content and process
        body_html = str(body_elem)
        body = self.text_processor.process(body_html)
        
        if len(body) < 100:
            raise ValueError(f"Article body too short ({len(body)} chars): {metadata.url}")
        
        # Extract date
        date_elem = (
            soup.select_one('time.entry-date') or
            soup.select_one('time') or
            soup.select_one('.published') or
            soup.select_one('.date') or
            soup.select_one('[class*="date"]')
        )
        
        if date_elem:
            # Try datetime attribute first (ISO format)
            date_str = date_elem.get('datetime') or date_elem.get_text(strip=True)
            date_str = self.text_processor.process_headline(date_str)
        else:
            date_str = metadata.date or datetime.now().strftime('%Y-%m-%d')
        
        # Extract author (optional)
        author_elem = (
            soup.select_one('a[rel="author"]') or
            soup.select_one('.author') or
            soup.select_one('.by-author') or
            soup.select_one('[class*="author"]')
        )
        
        author = author_elem.get_text(strip=True) if author_elem else None
        if author:
            author = self.text_processor.process_headline(author)
        
        # Extract tags (from category, meta keywords, or tag links)
        tags = [metadata.category]
        
        # Try to get tags from article (common in Hiru News)
        tag_links = soup.select('a[rel="tag"]') or soup.select('.tags a')
        if tag_links:
            tags.extend([self.text_processor.process_headline(tag.get_text()) for tag in tag_links[:5]])
        
        # Fallback to meta keywords
        if len(tags) == 1:  # Only category
            meta_keywords = soup.select_one('meta[name="keywords"]')
            if meta_keywords and meta_keywords.get('content'):
                keywords = meta_keywords['content'].split(',')
                tags.extend([k.strip() for k in keywords[:5]])
        
        # Calculate word count
        word_count = len(body.split())
        
        # Create Article object
        article = Article(
            headline=headline,
            body=body,
            source=self.website_name,
            category=metadata.category,
            date=date_str,
            url=metadata.url,
            extraction_timestamp=datetime.now().isoformat(),
            author=author,
            tags=tags if len(tags) > 1 else None,
            word_count=word_count
        )
        
        logger.debug(f"Parsed Hiru News article: {headline[:50]}... ({word_count} words)")
        
        return article
    
    def get_next_page_url(self, current_url: str, html: str, current_page: int) -> Optional[str]:
        """
        Extract URL for next page from current page HTML.
        
        Hiru News pagination patterns:
        - Segment-based: /page/[num]/
        - <a class="next"> or <a rel="next">
        - Numbered pagination with links
        - Check for articles to determine if more pages exist
        
        Args:
            current_url: Current page URL
            html: HTML content of current page
            current_page: Current page number
        
        Returns:
            URL for next page, or None if no next page
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # Method 1: Find explicit "Next" link
        next_link = (
            soup.select_one('a.next') or
            soup.select_one('a[rel="next"]') or
            soup.select_one('.pagination a[aria-label="Next"]') or
            soup.select_one('a:-soup-contains("Next")') or
            soup.select_one('a:-soup-contains("මීළඟ")')  # "Next" in Sinhala
        )
        
        if next_link and next_link.get('href'):
            next_url = next_link['href']
            
            # Make absolute URL
            if next_url.startswith('/'):
                next_url = urljoin(self.BASE_URL, next_url)
            elif not next_url.startswith('http'):
                next_url = urljoin(current_url, next_url)
            
            logger.debug(f"Hiru News: Found next page link: {next_url}")
            return next_url
        
        # Method 2: Look for numbered pagination
        pagination_area = soup.select_one('.pagination') or soup.select_one('nav.pagination')
        
        if pagination_area:
            # Look for link with next page number
            next_page_num = current_page + 1
            next_page_link = pagination_area.select_one(f'a:-soup-contains("{next_page_num}")')
            
            if next_page_link and next_page_link.get('href'):
                next_url = urljoin(self.BASE_URL, next_page_link['href'])
                logger.debug(f"Hiru News: Found next page in pagination: {next_url}")
                return next_url
        
        # Method 3: Check if current page has articles (if yes and not too deep, construct next URL)
        # Hiru News has massive archive, but set reasonable limit (e.g., 500 pages per category)
        if current_page < 500:
            articles = soup.select('article.post') or soup.select('a[href$=".html"]')
            
            if len(articles) >= 8:  # If we found at least 8 articles, likely more pages exist
                # Parse current URL to extract category
                parsed = urlparse(current_url)
                path_parts = parsed.path.strip('/').split('/')
                
                # Remove 'page' and page number if present
                if 'page' in path_parts:
                    page_idx = path_parts.index('page')
                    category_parts = path_parts[:page_idx]
                else:
                    category_parts = path_parts
                
                # Reconstruct category path
                category_path = '/'.join(category_parts)
                
                # Build next page URL
                next_page_num = current_page + 1
                next_url = f"{self.BASE_URL}/{category_path}/page/{next_page_num}/"
                
                logger.debug(f"Hiru News: Constructed next page URL: {next_url}")
                return next_url
        
        # No next page found
        logger.info(f"Hiru News: No next page found after page {current_page}")
        return None


# Convenience function for testing
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    from core.session_manager import SessionManager
    from storage.state_manager import StateManager
    from storage.file_writer import FileWriter
    from processors.sinhala_normalizer import TextProcessor
    
    print("=" * 70)
    print("  Hiru News Scraper Test")
    print("=" * 70)
    
    # Initialize components
    session_mgr = SessionManager(requests_per_minute=20)
    state_mgr = StateManager("test_hirunews.db")
    file_writer = FileWriter("./test_corpus_hirunews")
    text_processor = TextProcessor()
    
    # Create scraper
    scraper = HiruNewsScraper(
        website_name='hirunews',
        session_manager=session_mgr,
        state_manager=state_mgr,
        file_writer=file_writer,
        text_processor=text_processor
    )
    
    print("\n--- Categories ---")
    categories = scraper.get_category_urls()
    for cat_name, cat_url in categories.items():
        print(f"  {cat_name}: {cat_url}")
    
    print(f"\n✓ Found {len(categories)} categories")
    print("\nTo scrape:")
    print("  stats = scraper.scrape_category('local', categories['local'], max_pages=2)")
    print("\nOr use main.py:")
    print("  python main.py --site hirunews --category local --limit 100")
