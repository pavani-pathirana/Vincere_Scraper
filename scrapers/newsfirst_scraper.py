"""
NewsFirstScraper - Concrete scraper for NewsFirst Sinhala website.

Website: https://www.newsfirst.lk/sinhala
Pattern: Clean, high-density text articles with robust selectors
Focus: Quality journalism with well-structured content
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urljoin, urlparse, parse_qs

from bs4 import BeautifulSoup

from core.base_scraper import BaseScraper, ArticleMetadata, Article


logger = logging.getLogger(__name__)


class NewsFirstScraper(BaseScraper):
    """
    Concrete scraper for NewsFirst Sinhala website.
    
    URL Structure:
    - Homepage: https://www.newsfirst.lk/sinhala/
    - Category: https://www.newsfirst.lk/sinhala/[category]/
    - Pagination: https://www.newsfirst.lk/sinhala/[category]/page/[num]/
    - Article: https://www.newsfirst.lk/sinhala/[year]/[month]/[article-slug]/
    
    NewsFirst features:
    - Clean, modern layout with high-density text
    - Robust HTML structure with semantic tags
    - Well-formatted articles with clear content sections
    - Comprehensive category coverage
    
    Main Categories:
    - Local (දේශීය)
    - International (ලෝක)
    - Sports (ක්‍රීඩා)
    - Business (ව්‍යාපාර)
    - Entertainment (විනෝදාස්වාදය)
    - Politics (දේශපාලන)
    - Crime (අපරාධ)
    - Features (විශේෂාංග)
    """
    
    BASE_URL = 'https://www.newsfirst.lk'
    SINHALA_BASE = 'https://www.newsfirst.lk/sinhala'
    
    # Category mapping
    CATEGORIES = {
        'local': {
            'slug': 'local',
            'name': 'දේශීය'
        },
        'international': {
            'slug': 'world',
            'name': 'ලෝක'
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
            url = f"{self.SINHALA_BASE}/{slug}/"
            category_urls[category_key] = url
        
        logger.info(f"NewsFirst: Found {len(category_urls)} categories")
        return category_urls
    
    def get_article_list_url(self, category_url: str, page: int = 1) -> str:
        """
        Build URL for a specific page of article list.
        
        NewsFirst uses standard pagination: /[category]/page/[num]/
        
        Args:
            category_url: Base URL for category
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
        
        NewsFirst structure (clean, modern):
        - Articles in <article> or <div class="post-item">
        - Link: <a> with proper href structure
        - Headline: <h2> or <h3 class="entry-title">
        - Date: <time> with datetime attribute
        - Excerpt: <div class="excerpt"> or <p>
        
        Args:
            html: HTML content of list page
            category: Category name
        
        Returns:
            List of ArticleMetadata objects
        """
        soup = BeautifulSoup(html, 'lxml')
        articles = []
        
        # Try multiple selectors for NewsFirst
        article_containers = (
            soup.select('article.post') or
            soup.select('article') or
            soup.select('div.post-item') or
            soup.select('div.news-item') or
            soup.select('.post-list article') or
            soup.select('div[class*="post"]')
        )
        
        if not article_containers:
            logger.warning(f"No article containers found in NewsFirst {category} list page")
            # Fallback: look for links to sinhala articles
            content_area = soup.select_one('main') or soup.select_one('.content') or soup
            article_containers = content_area.select('a[href*="/sinhala/"]')
        
        for container in article_containers:
            try:
                # Extract article link
                if container.name == 'a':
                    link_elem = container
                else:
                    link_elem = container.select_one('a[href*="/sinhala/"]') or container.select_one('a')
                
                if not link_elem:
                    continue
                
                article_url = link_elem.get('href', '')
                
                # Make absolute URL
                if article_url.startswith('/'):
                    article_url = urljoin(self.BASE_URL, article_url)
                elif not article_url.startswith('http'):
                    article_url = urljoin(self.BASE_URL, article_url)
                
                # Skip if not a Sinhala article
                if '/sinhala/' not in article_url:
                    continue
                
                # Skip category pages and other non-article URLs
                if '/page/' in article_url or article_url.endswith(('/local/', '/world/', '/sports/')):
                    continue
                
                # Extract headline
                headline_elem = (
                    container.select_one('h2.entry-title') or
                    container.select_one('h3.entry-title') or
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
                    container.select_one('.entry-date') or
                    container.select_one('.post-date')
                )
                
                date_str = None
                if date_elem:
                    date_str = date_elem.get('datetime') or date_elem.get_text(strip=True)
                
                # Extract excerpt (optional)
                excerpt_elem = (
                    container.select_one('.excerpt') or
                    container.select_one('.entry-excerpt') or
                    container.select_one('.post-excerpt') or
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
                logger.warning(f"Failed to parse article container in NewsFirst list: {e}")
                continue
        
        logger.info(f"NewsFirst {category}: Extracted {len(articles)} articles from list page")
        
        return articles
    
    def parse_article_page(self, html: str, metadata: ArticleMetadata) -> Article:
        """
        Parse individual article page and extract full content.
        
        NewsFirst article structure (clean, semantic):
        - Headline: <h1 class="entry-title"> or <h1>
        - Body: <div class="entry-content"> or <article class="content">
        - Date: <time class="entry-date"> with datetime attribute
        - Author: <span class="author-name"> or <a rel="author">
        
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
            soup.select_one('h1.article-title') or
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
        
        # Extract body (main content) - NewsFirst has clean content divs
        body_elem = (
            soup.select_one('div.entry-content') or
            soup.select_one('div.article-content') or
            soup.select_one('div.post-content') or
            soup.select_one('div.content-body') or
            soup.select_one('article .content') or
            soup.select_one('.single-post-content') or
            soup.select_one('#article-body')
        )
        
        if not body_elem:
            raise ValueError(f"Article body not found for: {metadata.url}")
        
        # Remove unwanted elements (NewsFirst is usually clean, but be safe)
        for unwanted in body_elem.select('.ad, .advertisement, .related-posts, .social-share, .tags, script, style, iframe'):
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
            soup.select_one('time.post-date') or
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
            soup.select_one('.post-author') or
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
        
        # Fallback to meta keywords
        if len(tags) == 1:
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
        
        logger.debug(f"Parsed NewsFirst article: {headline[:50]}... ({word_count} words)")
        
        return article
    
    def get_next_page_url(self, current_url: str, html: str, current_page: int) -> Optional[str]:
        """
        Extract URL for next page from current page HTML.
        
        NewsFirst pagination patterns:
        - <a class="next"> or <a rel="next">
        - Numbered pagination with clear links
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
            soup.select_one('.pagination-next a') or
            soup.select_one('a.next-page') or
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
            
            logger.debug(f"NewsFirst: Found next page link: {next_url}")
            return next_url
        
        # Method 2: Look for numbered pagination
        pagination_area = soup.select_one('.pagination') or soup.select_one('nav.pagination') or soup.select_one('.page-numbers')
        
        if pagination_area:
            next_page_num = current_page + 1
            # Look for link containing next page number
            for link in pagination_area.select('a'):
                link_text = link.get_text(strip=True)
                if link_text.isdigit() and int(link_text) == next_page_num:
                    next_url = urljoin(self.BASE_URL, link['href'])
                    logger.debug(f"NewsFirst: Found next page in pagination: {next_url}")
                    return next_url
        
        # Method 3: Construct next URL if articles found (reasonable limit: 300 pages)
        if current_page < 300:
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
                
                logger.debug(f"NewsFirst: Constructed next page URL: {next_url}")
                return next_url
        
        # No next page found
        logger.info(f"NewsFirst: No next page found after page {current_page}")
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
    print("  NewsFirst Scraper Test")
    print("=" * 70)
    
    # Initialize components
    session_mgr = SessionManager(requests_per_minute=20)
    state_mgr = StateManager("test_newsfirst.db")
    file_writer = FileWriter("./test_corpus_newsfirst")
    text_processor = TextProcessor()
    
    # Create scraper
    scraper = NewsFirstScraper(
        website_name='newsfirst',
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
    print("  python main.py --site newsfirst --category local --limit 100")
