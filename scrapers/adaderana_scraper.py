"""
AdaDeranaScraper - Concrete scraper for Ada Derana Sinhala news website.

Website: https://sinhala.adaderana.lk
Pattern: Category URLs use ?id=[cat_id]&page=[page]
Categories: 8 major categories including Politics, Sports, Entertainment, etc.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urljoin, urlparse, parse_qs

from bs4 import BeautifulSoup

from core.base_scraper import BaseScraper, ArticleMetadata, Article


logger = logging.getLogger(__name__)


class AdaDeranaScraper(BaseScraper):
    """
    Concrete scraper for Ada Derana Sinhala news website.
    
    URL Structure:
    - Homepage: https://sinhala.adaderana.lk
    - Category: https://sinhala.adaderana.lk/news.php?id=[cat_id]
    - Pagination: https://sinhala.adaderana.lk/news.php?id=[cat_id]&page=[page]
    - Article: https://sinhala.adaderana.lk/news/[article_id]/[slug]
    
    Categories (8 major):
    - Politics (id=1)
    - Sports (id=2)
    - Business (id=3)
    - Entertainment (id=4)
    - Local News (id=5)
    - International (id=6)
    - Features (id=7)
    - Crime (id=8)
    """
    
    BASE_URL = 'https://sinhala.adaderana.lk'
    
    # Category ID mapping
    CATEGORIES = {
        'politics': {'id': '1', 'name': 'දේශපාලන'},
        'sports': {'id': '2', 'name': 'ක්‍රීඩා'},
        'business': {'id': '3', 'name': 'ව්‍යාපාර'},
        'entertainment': {'id': '4', 'name': 'විනෝදාස්වාදය'},
        'local': {'id': '5', 'name': 'දේශීය'},
        'international': {'id': '6', 'name': 'ජාත්‍යන්තර'},
        'features': {'id': '7', 'name': 'විශේෂාංග'},
        'crime': {'id': '8', 'name': 'අපරාධ'}
    }
    
    def get_category_urls(self) -> Dict[str, str]:
        """
        Get mapping of category names to their URLs.
        
        Returns:
            Dict mapping category_name → category_url
        """
        category_urls = {}
        
        for category_key, category_info in self.CATEGORIES.items():
            cat_id = category_info['id']
            url = f"{self.BASE_URL}/news.php?id={cat_id}"
            category_urls[category_key] = url
            
        logger.info(f"Ada Derana: Found {len(category_urls)} categories")
        return category_urls
    
    def get_article_list_url(self, category_url: str, page: int = 1) -> str:
        """
        Build URL for a specific page of article list.
        
        Args:
            category_url: Base URL for category (e.g., ...news.php?id=1)
            page: Page number (1-indexed)
        
        Returns:
            Full URL for article list page
        """
        if page == 1:
            # First page doesn't need &page parameter
            return category_url
        
        # Subsequent pages: add &page=[page]
        return f"{category_url}&page={page}"
    
    def parse_article_list_page(self, html: str, category: str) -> List[ArticleMetadata]:
        """
        Parse article list page and extract article metadata.
        
        Ada Derana structure (typical patterns):
        - Articles in <div class="news-item"> or <div class="news-story">
        - Link: <a href="/news/[id]/[slug]">
        - Headline: <h2> or <h3> or <div class="headline">
        - Date: <span class="date"> or <div class="time">
        - Excerpt: <p class="excerpt">
        
        Args:
            html: HTML content of list page
            category: Category name
        
        Returns:
            List of ArticleMetadata objects
        """
        soup = BeautifulSoup(html, 'lxml')
        articles = []
        
        # Try multiple selectors (Ada Derana may use different classes)
        # Common patterns: .news-item, .news-story, .news-block, article
        article_containers = (
            soup.select('div.news-item') or
            soup.select('div.news-story') or
            soup.select('div.news-block') or
            soup.select('article.news') or
            soup.select('div[class*="news"]')  # Any div with "news" in class
        )
        
        if not article_containers:
            logger.warning(f"No article containers found in Ada Derana {category} list page")
            # Try fallback: all links in main content area
            content_area = soup.select_one('#content') or soup.select_one('.content') or soup
            article_containers = content_area.select('a[href*="/news/"]')
        
        for container in article_containers:
            try:
                # Extract article link
                link_elem = container if container.name == 'a' else container.select_one('a[href*="/news/"]')
                
                if not link_elem:
                    continue
                
                article_url = link_elem.get('href', '')
                
                # Make absolute URL
                if article_url.startswith('/'):
                    article_url = urljoin(self.BASE_URL, article_url)
                elif not article_url.startswith('http'):
                    article_url = urljoin(self.BASE_URL, article_url)
                
                # Skip if not a news article URL
                if '/news/' not in article_url:
                    continue
                
                # Extract headline
                headline_elem = (
                    container.select_one('h2') or
                    container.select_one('h3') or
                    container.select_one('.headline') or
                    container.select_one('.title') or
                    link_elem
                )
                
                headline = headline_elem.get_text(strip=True) if headline_elem else 'Untitled'
                
                # Skip if headline is empty or too short
                if len(headline) < 10:
                    continue
                
                # Extract date (optional)
                date_elem = (
                    container.select_one('.date') or
                    container.select_one('.time') or
                    container.select_one('span[class*="date"]') or
                    container.select_one('time')
                )
                
                date_str = date_elem.get_text(strip=True) if date_elem else None
                
                # Extract excerpt (optional)
                excerpt_elem = (
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
                logger.warning(f"Failed to parse article container in Ada Derana list: {e}")
                continue
        
        logger.info(f"Ada Derana {category}: Extracted {len(articles)} articles from list page")
        
        return articles
    
    def parse_article_page(self, html: str, metadata: ArticleMetadata) -> Article:
        """
        Parse individual article page and extract full content.
        
        Ada Derana article structure (typical):
        - Headline: <h1 class="article-title"> or <h1> in article
        - Body: <div class="article-content"> or <div class="article-body">
        - Date: <span class="date"> or <time>
        - Author: <span class="author"> or <div class="by-line">
        
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
            soup.select_one('h1.article-title') or
            soup.select_one('h1.news-title') or
            soup.select_one('article h1') or
            soup.select_one('.article-header h1') or
            soup.select_one('h1')
        )
        
        if not headline_elem:
            # Fallback to metadata headline if not found on page
            headline = metadata.headline
            logger.warning(f"Headline not found in article page, using metadata: {headline[:50]}...")
        else:
            headline = self.text_processor.process_headline(headline_elem.get_text())
        
        # Extract body (main content div)
        body_elem = (
            soup.select_one('div.article-content') or
            soup.select_one('div.article-body') or
            soup.select_one('div.news-content') or
            soup.select_one('div.news-body') or
            soup.select_one('article .content') or
            soup.select_one('#article-content')
        )
        
        if not body_elem:
            raise ValueError(f"Article body not found for: {metadata.url}")
        
        # Get HTML content and process
        body_html = str(body_elem)
        body = self.text_processor.process(body_html)
        
        if len(body) < 100:
            raise ValueError(f"Article body too short ({len(body)} chars): {metadata.url}")
        
        # Extract date
        date_elem = (
            soup.select_one('span.article-date') or
            soup.select_one('time') or
            soup.select_one('.date') or
            soup.select_one('.published-date') or
            soup.select_one('[class*="date"]')
        )
        
        if date_elem:
            date_str = date_elem.get_text(strip=True)
            # Clean up date string
            date_str = self.text_processor.process_headline(date_str)
        else:
            date_str = metadata.date or datetime.now().strftime('%Y-%m-%d')
        
        # Extract author (optional)
        author_elem = (
            soup.select_one('.author') or
            soup.select_one('.by-line') or
            soup.select_one('[class*="author"]')
        )
        
        author = author_elem.get_text(strip=True) if author_elem else None
        if author:
            author = self.text_processor.process_headline(author)
        
        # Extract tags (optional - from category or meta tags)
        tags = [metadata.category]
        
        # Try to get additional tags from meta keywords
        meta_keywords = soup.select_one('meta[name="keywords"]')
        if meta_keywords and meta_keywords.get('content'):
            keywords = meta_keywords['content'].split(',')
            tags.extend([k.strip() for k in keywords[:5]])  # Max 5 additional tags
        
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
            tags=tags if len(tags) > 1 else None,  # Only include if more than just category
            word_count=word_count
        )
        
        logger.debug(f"Parsed Ada Derana article: {headline[:50]}... ({word_count} words)")
        
        return article
    
    def get_next_page_url(self, current_url: str, html: str, current_page: int) -> Optional[str]:
        """
        Extract URL for next page from current page HTML.
        
        Ada Derana pagination patterns:
        - <a class="next"> or <a class="next-page">
        - <a> with text "මීළඟ" (Next in Sinhala)
        - Numbered pagination links
        - Or just increment &page parameter
        
        Args:
            current_url: Current page URL
            html: HTML content of current page
            current_page: Current page number
        
        Returns:
            URL for next page, or None if no next page
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # Method 1: Find "Next" link
        next_link = (
            soup.select_one('a.next') or
            soup.select_one('a.next-page') or
            soup.select_one('a[rel="next"]') or
            soup.select_one('a:-soup-contains("මීළඟ")') or  # "Next" in Sinhala
            soup.select_one('a:-soup-contains("Next")')
        )
        
        if next_link and next_link.get('href'):
            next_url = next_link['href']
            
            # Make absolute URL
            if next_url.startswith('/'):
                next_url = urljoin(self.BASE_URL, next_url)
            elif not next_url.startswith('http'):
                next_url = urljoin(current_url, next_url)
            
            logger.debug(f"Ada Derana: Found next page link: {next_url}")
            return next_url
        
        # Method 2: Check for numbered pagination and look for current_page + 1
        pagination_links = soup.select('.pagination a') or soup.select('a[href*="page="]')
        
        next_page_num = current_page + 1
        for link in pagination_links:
            href = link.get('href', '')
            if f'page={next_page_num}' in href:
                next_url = urljoin(self.BASE_URL, href)
                logger.debug(f"Ada Derana: Found next page in pagination: {next_url}")
                return next_url
        
        # Method 3: Check if current page has articles (if yes, assume next page exists)
        # Only up to a reasonable limit (e.g., 100 pages)
        if current_page < 100:
            articles = soup.select('div.news-item') or soup.select('a[href*="/news/"]')
            
            if len(articles) >= 10:  # If we found at least 10 articles, likely more pages exist
                # Parse current URL and add/increment page parameter
                parsed = urlparse(current_url)
                query_params = parse_qs(parsed.query)
                
                # Get category ID from current URL
                cat_id = query_params.get('id', [None])[0]
                
                if cat_id:
                    next_url = f"{self.BASE_URL}/news.php?id={cat_id}&page={next_page_num}"
                    logger.debug(f"Ada Derana: Constructed next page URL: {next_url}")
                    return next_url
        
        # No next page found
        logger.info(f"Ada Derana: No next page found after page {current_page}")
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
    print("  Ada Derana Scraper Test")
    print("=" * 70)
    
    # Initialize components
    session_mgr = SessionManager(requests_per_minute=20)
    state_mgr = StateManager("test_adaderana.db")
    file_writer = FileWriter("./test_corpus_adaderana")
    text_processor = TextProcessor()
    
    # Create scraper
    scraper = AdaDeranaScraper(
        website_name='adaderana',
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
    print("  stats = scraper.scrape_category('politics', categories['politics'], max_pages=2)")
    print("\nOr use main.py:")
    print("  python main.py --site adaderana --category politics --limit 50")
