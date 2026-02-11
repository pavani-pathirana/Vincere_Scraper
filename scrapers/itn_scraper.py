"""
ITNScraper - Concrete scraper for ITN News Sinhala website.

Website: https://www.itnnews.lk
Pattern: Standard news categories with simple HTML structure
Focus: Clean, straightforward scraping for ITN's well-structured pages
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urljoin, urlparse, parse_qs

from bs4 import BeautifulSoup

from core.base_scraper import BaseScraper, ArticleMetadata, Article


logger = logging.getLogger(__name__)


class ITNScraper(BaseScraper):
    """
    Concrete scraper for ITN News Sinhala website.
    
    URL Structure:
    - Homepage: https://www.itnnews.lk
    - Category: https://www.itnnews.lk/category/[category-name]/
    - Pagination: https://www.itnnews.lk/category/[category-name]/page/[num]/
    - Article: https://www.itnnews.lk/[year]/[month]/[day]/[article-slug]/
    
    ITN has a simple, clean HTML structure with:
    - Standard WordPress-style categories
    - Straightforward article listings
    - Clear content divs with consistent naming
    
    Main Categories:
    - Local News (දේශීය පුවත්)
    - International (විදේශ)
    - Sports (ක්‍රීඩා)
    - Business (ව්‍යාපාර)
    - Entertainment (විනෝදාස්වාදය)
    - Politics (දේශපාලන)
    - Economy (ආර්ථික)
    """
    
    BASE_URL = 'https://www.itnnews.lk'
    
    # Category mapping (adjust based on actual site structure)
    CATEGORIES = {
        'local': {
            'slug': 'local-news',
            'name': 'දේශීය පුවත්'
        },
        'international': {
            'slug': 'international',
            'name': 'විදේශ'
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
        'economy': {
            'slug': 'economy',
            'name': 'ආර්ථික'
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
            url = f"{self.BASE_URL}/category/{slug}/"
            category_urls[category_key] = url
        
        logger.info(f"ITN News: Found {len(category_urls)} categories")
        return category_urls
    
    def get_article_list_url(self, category_url: str, page: int = 1) -> str:
        """
        Build URL for a specific page of article list.
        
        ITN uses WordPress-style pagination: /category/[name]/page/[num]/
        
        Args:
            category_url: Base URL for category (e.g., /category/local-news/)
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
        
        ITN structure (simple WordPress pattern):
        - Articles in <article> tags or <div class="post">
        - Link: <a> with href to article
        - Headline: <h2 class="entry-title"> or similar
        - Date: <time> or <span class="date">
        - Excerpt: <div class="excerpt"> or <p>
        
        Args:
            html: HTML content of list page
            category: Category name
        
        Returns:
            List of ArticleMetadata objects
        """
        soup = BeautifulSoup(html, 'lxml')
        articles = []
        
        # Try multiple selectors for ITN News
        article_containers = (
            soup.select('article') or
            soup.select('div.post') or
            soup.select('div.news-item') or
            soup.select('div[class*="post-"]') or
            soup.select('.posts-container article')
        )
        
        if not article_containers:
            logger.warning(f"No article containers found in ITN {category} list page")
            # Fallback: look for any article links
            content_area = soup.select_one('main') or soup.select_one('.content') or soup
            # ITN articles typically have date-based URLs
            article_containers = content_area.select('a[href*="/2024/"], a[href*="/2025/"], a[href*="/2026/"]')
        
        for container in article_containers:
            try:
                # Extract article link
                if container.name == 'a':
                    link_elem = container
                else:
                    link_elem = container.select_one('a')
                
                if not link_elem:
                    continue
                
                article_url = link_elem.get('href', '')
                
                # Make absolute URL
                if article_url.startswith('/'):
                    article_url = urljoin(self.BASE_URL, article_url)
                elif not article_url.startswith('http'):
                    article_url = urljoin(self.BASE_URL, article_url)
                
                # Skip if not an article URL (should contain date format)
                # ITN articles: /2024/01/15/article-title/
                if not any(year in article_url for year in ['/2024/', '/2025/', '/2026/', '/2027/']):
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
                
                # Skip if headline is empty or too short
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
                    date_str = date_elem.get('datetime') or date_elem.get_text(strip=True)
                
                # Extract excerpt (optional)
                excerpt_elem = (
                    container.select_one('.excerpt') or
                    container.select_one('.entry-excerpt') or
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
                logger.warning(f"Failed to parse article container in ITN list: {e}")
                continue
        
        logger.info(f"ITN {category}: Extracted {len(articles)} articles from list page")
        
        return articles
    
    def parse_article_page(self, html: str, metadata: ArticleMetadata) -> Article:
        """
        Parse individual article page and extract full content.
        
        ITN article structure (WordPress standard):
        - Headline: <h1 class="entry-title"> or <h1>
        - Body: <div class="entry-content"> or <div class="article-content">
        - Date: <time class="entry-date">
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
            soup.select_one('h1.post-title') or
            soup.select_one('article h1') or
            soup.select_one('.article-header h1') or
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
            soup.select_one('div.post-content') or
            soup.select_one('article .content') or
            soup.select_one('.single-content') or
            soup.select_one('#content')
        )
        
        if not body_elem:
            raise ValueError(f"Article body not found for: {metadata.url}")
        
        # Remove unwanted elements (ads, related articles, social buttons)
        for unwanted in body_elem.select('.ad, .advertisement, .related, .share, script, style, iframe'):
            unwanted.decompose()
        
        # Get HTML content and process
        body_html = str(body_elem)
        body = self.text_processor.process(body_html)
        
        if len(body) < 100:
            raise ValueError(f"Article body too short ({len(body)} chars): {metadata.url}")
        
        # Extract date
        date_elem = (
            soup.select_one('time.entry-date') or
            soup.select_one('time.published') or
            soup.select_one('time') or
            soup.select_one('.date') or
            soup.select_one('.published-date')
        )
        
        if date_elem:
            date_str = date_elem.get('datetime') or date_elem.get_text(strip=True)
            date_str = self.text_processor.process_headline(date_str)
        else:
            date_str = metadata.date or datetime.now().strftime('%Y-%m-%d')
        
        # Extract author (optional)
        author_elem = (
            soup.select_one('a[rel="author"]') or
            soup.select_one('.author-name') or
            soup.select_one('.by-author') or
            soup.select_one('[class*="author"]')
        )
        
        author = author_elem.get_text(strip=True) if author_elem else None
        if author:
            author = self.text_processor.process_headline(author)
        
        # Extract tags
        tags = [metadata.category]
        
        # Try to get tags from article
        tag_links = soup.select('a[rel="tag"]') or soup.select('.tags a') or soup.select('.post-tags a')
        if tag_links:
            tags.extend([self.text_processor.process_headline(tag.get_text()) for tag in tag_links[:5]])
        
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
        
        logger.debug(f"Parsed ITN article: {headline[:50]}... ({word_count} words)")
        
        return article
    
    def get_next_page_url(self, current_url: str, html: str, current_page: int) -> Optional[str]:
        """
        Extract URL for next page from current page HTML.
        
        ITN pagination patterns (WordPress standard):
        - <a class="next"> or <a rel="next">
        - Numbered pagination links
        - /page/[num]/ segment pattern
        
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
            soup.select_one('.pagination a[aria-label*="Next"]') or
            soup.select_one('a:-soup-contains("Next")') or
            soup.select_one('a:-soup-contains("මීළඟ")')
        )
        
        if next_link and next_link.get('href'):
            next_url = next_link['href']
            
            # Make absolute URL
            if next_url.startswith('/'):
                next_url = urljoin(self.BASE_URL, next_url)
            elif not next_url.startswith('http'):
                next_url = urljoin(current_url, next_url)
            
            logger.debug(f"ITN: Found next page link: {next_url}")
            return next_url
        
        # Method 2: Look for numbered pagination
        pagination_area = soup.select_one('.pagination') or soup.select_one('nav.pagination') or soup.select_one('.nav-links')
        
        if pagination_area:
            next_page_num = current_page + 1
            # Look for link containing next page number
            for link in pagination_area.select('a'):
                link_text = link.get_text(strip=True)
                if link_text.isdigit() and int(link_text) == next_page_num:
                    next_url = urljoin(self.BASE_URL, link['href'])
                    logger.debug(f"ITN: Found next page in pagination: {next_url}")
                    return next_url
        
        # Method 3: Construct next URL if articles found (reasonable limit: 200 pages)
        if current_page < 200:
            articles = soup.select('article') or soup.select('.post')
            
            if len(articles) >= 5:  # If we found at least 5 articles, likely more pages exist
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
                
                logger.debug(f"ITN: Constructed next page URL: {next_url}")
                return next_url
        
        # No next page found
        logger.info(f"ITN: No next page found after page {current_page}")
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
    print("  ITN News Scraper Test")
    print("=" * 70)
    
    # Initialize components
    session_mgr = SessionManager(requests_per_minute=20)
    state_mgr = StateManager("test_itn.db")
    file_writer = FileWriter("./test_corpus_itn")
    text_processor = TextProcessor()
    
    # Create scraper
    scraper = ITNScraper(
        website_name='itn',
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
    print("  python main.py --site itn --category local --limit 100")
