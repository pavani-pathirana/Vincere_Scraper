"""
BaseScraper - Abstract base class for news site scrapers.

Defines the Strategy Pattern interface that all concrete scrapers must implement.
Provides common functionality for session management, error handling, and logging.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime

from core.session_manager import SessionManager
from storage.state_manager import StateManager
from storage.file_writer import FileWriter
from processors.sinhala_normalizer import TextProcessor


logger = logging.getLogger(__name__)


@dataclass
class ArticleMetadata:
    """
    Metadata for an article extracted from list page.
    
    Used to pass article information from list page parsing to article scraping.
    """
    url: str
    headline: str
    category: str
    date: Optional[str] = None
    excerpt: Optional[str] = None
    author: Optional[str] = None


@dataclass
class Article:
    """
    Complete article data ready for storage.
    
    Matches the JSON schema required by FileWriter.
    """
    headline: str
    body: str
    source: str
    category: str
    date: str
    url: str
    extraction_timestamp: str
    author: Optional[str] = None
    tags: Optional[List[str]] = None
    word_count: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = {
            'headline': self.headline,
            'body': self.body,
            'source': self.source,
            'category': self.category,
            'date': self.date,
            'url': self.url,
            'extraction_timestamp': self.extraction_timestamp
        }
        
        # Add optional fields if present
        if self.author:
            data['author'] = self.author
        if self.tags:
            data['tags'] = self.tags
        if self.word_count is not None:
            data['word_count'] = self.word_count
        
        return data


class BaseScraper(ABC):
    """
    Abstract base class for news site scrapers.
    
    Implements Strategy Pattern - each news site has a concrete implementation
    that defines site-specific extraction logic.
    
    Common functionality:
    - HTTP session management
    - State persistence (idempotency, resumability)
    - File writing
    - Text processing
    - Error handling
    - Logging
    
    Abstract methods (must be implemented by concrete scrapers):
    - get_category_urls(): Discover available categories
    - get_article_list_url(): Build URL for category article list
    - parse_article_list_page(): Extract article metadata from list page
    - parse_article_page(): Extract full article content
    - get_next_page_url(): Navigate pagination
    """
    
    def __init__(
        self,
        website_name: str,
        session_manager: SessionManager,
        state_manager: StateManager,
        file_writer: FileWriter,
        text_processor: Optional[TextProcessor] = None
    ):
        """
        Initialize base scraper.
        
        Args:
            website_name: Identifier for this website (e.g., 'adaderana')
            session_manager: HTTP session manager
            state_manager: State persistence manager
            file_writer: File writer for article storage
            text_processor: Text processor (created if not provided)
        """
        self.website_name = website_name
        self.session_manager = session_manager
        self.state_manager = state_manager
        self.file_writer = file_writer
        self.text_processor = text_processor or TextProcessor()
        
        # Statistics
        self.stats = {
            'articles_scraped': 0,
            'articles_failed': 0,
            'articles_skipped': 0,
            'pages_processed': 0
        }
        
        logger.info(f"Initialized {self.__class__.__name__} for {website_name}")
    
    # ==================== Abstract Methods (Strategy Pattern Interface) ====================
    
    @abstractmethod
    def get_category_urls(self) -> Dict[str, str]:
        """
        Get mapping of category names to their base URLs.
        
        Returns:
            Dict mapping category_name → category_url
            Example: {'politics': 'https://example.com/politics', ...}
        
        Note: This should scrape the site's navigation/homepage to discover
        available categories, or return a hardcoded mapping.
        """
        pass
    
    @abstractmethod
    def get_article_list_url(self, category_url: str, page: int = 1) -> str:
        """
        Build URL for a specific page of article list.
        
        Args:
            category_url: Base URL for category
            page: Page number (1-indexed)
        
        Returns:
            Full URL for article list page
            Example: 'https://example.com/politics?page=2'
        """
        pass
    
    @abstractmethod
    def parse_article_list_page(self, html: str, category: str) -> List[ArticleMetadata]:
        """
        Parse article list page and extract article metadata.
        
        Args:
            html: HTML content of list page
            category: Category name
        
        Returns:
            List of ArticleMetadata objects
        
        Raises:
            ValueError: If HTML structure is invalid/unexpected
        """
        pass
    
    @abstractmethod
    def parse_article_page(self, html: str, metadata: ArticleMetadata) -> Article:
        """
        Parse individual article page and extract full content.
        
        Args:
            html: HTML content of article page
            metadata: Metadata from list page
        
        Returns:
            Complete Article object
        
        Raises:
            ValueError: If HTML structure is invalid/unexpected
        """
        pass
    
    @abstractmethod
    def get_next_page_url(self, current_url: str, html: str, current_page: int) -> Optional[str]:
        """
        Extract URL for next page from current page HTML.
        
        Args:
            current_url: Current page URL
            html: HTML content of current page
            current_page: Current page number
        
        Returns:
            URL for next page, or None if no next page
        
        Note: Can parse 'Next' button, pagination links, or just increment page number.
        """
        pass
    
    # ==================== Common Functionality ====================
    
    def scrape_category(
        self,
        category: str,
        category_url: str,
        max_pages: Optional[int] = None,
        resume: bool = True
    ) -> Dict[str, Any]:
        """
        Scrape all articles from a category.
        
        High-level orchestration:
        1. Load pagination state (if resume=True)
        2. For each page:
           - Scrape article list
           - For each article:
             - Check if already scraped (idempotency)
             - Scrape article
             - Save to file
             - Update state
           - Update pagination state
        3. Return statistics
        
        Args:
            category: Category name
            category_url: Base URL for category
            max_pages: Maximum pages to scrape (None = all)
            resume: Resume from last pagination state
        
        Returns:
            Dict with statistics (scraped, failed, skipped counts)
        """
        logger.info(f"Starting category scrape: {self.website_name}/{category}")
        
        # Determine starting page
        start_page = 1
        if resume:
            state = self.state_manager.get_pagination_state(self.website_name, category)
            if state and not state['is_complete']:
                start_page = state['last_page_index'] + 1
                logger.info(f"Resuming from page {start_page}")
        
        # Create session
        session_id = self.state_manager.create_session(
            website=self.website_name,
            category=category
        )
        
        current_page = start_page
        articles_this_run = 0
        
        try:
            while True:
                # Check max pages limit
                if max_pages and current_page > start_page + max_pages - 1:
                    logger.info(f"Reached max_pages limit: {max_pages}")
                    break
                
                # Build list page URL
                list_url = self.get_article_list_url(category_url, current_page)
                
                logger.info(f"Scraping page {current_page}: {list_url}")
                
                try:
                    # Fetch list page
                    response = self.session_manager.get(list_url)
                    response.raise_for_status()
                    
                    # Parse article list
                    articles = self.parse_article_list_page(response.text, category)
                    
                    if not articles:
                        logger.info(f"No articles found on page {current_page}, ending scrape")
                        break
                    
                    logger.info(f"Found {len(articles)} articles on page {current_page}")
                    
                    # Scrape each article
                    for article_meta in articles:
                        try:
                            self._scrape_single_article(article_meta, session_id)
                            articles_this_run += 1
                        except Exception as e:
                            logger.error(f"Failed to scrape article {article_meta.url}: {e}")
                            self.stats['articles_failed'] += 1
                            self.state_manager.update_session_stats(session_id, articles_failed=1)
                    
                    # Update pagination state
                    self.state_manager.update_pagination_state(
                        self.website_name,
                        category,
                        last_page_index=current_page
                    )
                    
                    self.stats['pages_processed'] += 1
                    
                    # Check for next page
                    next_url = self.get_next_page_url(list_url, response.text, current_page)
                    if not next_url:
                        logger.info(f"No next page found, category complete")
                        self.state_manager.update_pagination_state(
                            self.website_name,
                            category,
                            last_page_index=current_page,
                            is_complete=True
                        )
                        break
                    
                    current_page += 1
                    
                except Exception as e:
                    logger.error(f"Failed to process page {current_page}: {e}")
                    # Save state and continue
                    self.state_manager.update_pagination_state(
                        self.website_name,
                        category,
                        last_page_index=current_page - 1  # Last successful page
                    )
                    raise
            
            # Mark session complete
            self.state_manager.update_session_stats(session_id, status='completed')
            
            logger.info(
                f"Category scrape complete: {self.website_name}/{category} - "
                f"{articles_this_run} articles this run"
            )
            
        except KeyboardInterrupt:
            logger.warning("Scraping interrupted by user")
            self.state_manager.update_session_stats(session_id, status='interrupted')
            raise
        
        except Exception as e:
            logger.error(f"Category scrape failed: {e}")
            self.state_manager.update_session_stats(session_id, status='failed')
            raise
        
        return self.stats.copy()
    
    def _scrape_single_article(self, metadata: ArticleMetadata, session_id: str):
        """
        Scrape a single article with idempotency check.
        
        Args:
            metadata: Article metadata from list page
            session_id: Current session ID
        """
        url = metadata.url
        
        # Check if already scraped (idempotency)
        is_scraped, reason = self.state_manager.is_url_scraped(url)
        if is_scraped:
            logger.debug(f"Skipping already scraped article: {url} ({reason})")
            self.stats['articles_skipped'] += 1
            self.state_manager.update_session_stats(session_id, articles_skipped=1)
            return
        
        try:
            # Fetch article page
            response = self.session_manager.get(url)
            response.raise_for_status()
            
            # Parse article
            article = self.parse_article_page(response.text, metadata)
            
            # Generate article ID
            article_id = StateManager.generate_article_id(url)
            
            # Write to file
            self.file_writer.write_article(
                article_data=article.to_dict(),
                website=self.website_name,
                category=metadata.category,
                article_id=article_id
            )
            
            # Mark as scraped (success)
            content_checksum = StateManager.generate_content_checksum(article.body)
            self.state_manager.mark_url_scraped(
                url=url,
                website=self.website_name,
                category=metadata.category,
                article_id=article_id,
                status='success',
                content_checksum=content_checksum
            )
            
            self.stats['articles_scraped'] += 1
            self.state_manager.update_session_stats(session_id, articles_scraped=1)
            
            logger.info(f"Scraped article: {article.headline[:50]}... ({article_id})")
            
        except Exception as e:
            # Mark as failed (will be retried later)
            article_id = StateManager.generate_article_id(url)
            self.state_manager.mark_url_scraped(
                url=url,
                website=self.website_name,
                category=metadata.category,
                article_id=article_id,
                status='failed',
                error_message=str(e)
            )
            
            logger.error(f"Failed to scrape article {url}: {e}")
            raise
    
    def scrape_all_categories(
        self,
        max_pages_per_category: Optional[int] = None,
        resume: bool = True
    ) -> Dict[str, Any]:
        """
        Scrape all categories for this website.
        
        Args:
            max_pages_per_category: Maximum pages per category
            resume: Resume from last state
        
        Returns:
            Dict with per-category statistics
        """
        categories = self.get_category_urls()
        logger.info(f"Found {len(categories)} categories for {self.website_name}")
        
        results = {}
        
        for category_name, category_url in categories.items():
            logger.info(f"Starting category: {category_name}")
            
            try:
                stats = self.scrape_category(
                    category=category_name,
                    category_url=category_url,
                    max_pages=max_pages_per_category,
                    resume=resume
                )
                results[category_name] = stats
                
            except Exception as e:
                logger.error(f"Failed to scrape category {category_name}: {e}")
                results[category_name] = {'error': str(e)}
        
        return results
    
    def retry_failed_articles(self, max_retries: int = 3) -> Dict[str, int]:
        """
        Retry scraping failed articles.
        
        Args:
            max_retries: Maximum retry attempts
        
        Returns:
            Dict with success/failure counts
        """
        failed_urls = self.state_manager.get_failed_urls(
            website=self.website_name,
            max_retries=max_retries
        )
        
        logger.info(f"Retrying {len(failed_urls)} failed articles")
        
        session_id = self.state_manager.create_session(website=self.website_name)
        
        success_count = 0
        failure_count = 0
        
        for failed in failed_urls:
            url = failed['url']
            category = failed['category']
            
            try:
                # Create metadata (minimal info for retry)
                metadata = ArticleMetadata(
                    url=url,
                    headline="",  # Will be extracted from article page
                    category=category
                )
                
                self._scrape_single_article(metadata, session_id)
                success_count += 1
                
            except Exception as e:
                logger.error(f"Retry failed for {url}: {e}")
                failure_count += 1
        
        self.state_manager.update_session_stats(session_id, status='completed')
        
        logger.info(f"Retry complete: {success_count} succeeded, {failure_count} failed")
        
        return {'success': success_count, 'failure': failure_count}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get scraper statistics."""
        return self.stats.copy()
    
    def reset_stats(self):
        """Reset scraper statistics."""
        self.stats = {
            'articles_scraped': 0,
            'articles_failed': 0,
            'articles_skipped': 0,
            'pages_processed': 0
        }


# Example concrete scraper (template for implementation)
class ExampleScraper(BaseScraper):
    """
    Example scraper implementation showing the required interface.
    
    This serves as a template for implementing concrete scrapers.
    """
    
    def get_category_urls(self) -> Dict[str, str]:
        """Return hardcoded category URLs for this example."""
        return {
            'politics': 'https://example.com/politics',
            'sports': 'https://example.com/sports',
            'local': 'https://example.com/local-news'
        }
    
    def get_article_list_url(self, category_url: str, page: int = 1) -> str:
        """Build paginated URL."""
        if page == 1:
            return category_url
        return f"{category_url}?page={page}"
    
    def parse_article_list_page(self, html: str, category: str) -> List[ArticleMetadata]:
        """Parse list page - IMPLEMENT WITH BEAUTIFULSOUP."""
        # Example implementation:
        # from bs4 import BeautifulSoup
        # soup = BeautifulSoup(html, 'lxml')
        # articles = []
        # for item in soup.select('.article-item'):
        #     articles.append(ArticleMetadata(
        #         url=item.select_one('a')['href'],
        #         headline=item.select_one('.headline').get_text(),
        #         category=category
        #     ))
        # return articles
        raise NotImplementedError("Implement with site-specific selectors")
    
    def parse_article_page(self, html: str, metadata: ArticleMetadata) -> Article:
        """Parse article page - IMPLEMENT WITH BEAUTIFULSOUP."""
        # Example implementation:
        # from bs4 import BeautifulSoup
        # soup = BeautifulSoup(html, 'lxml')
        # 
        # headline = soup.select_one('.article-headline').get_text()
        # body_html = soup.select_one('.article-body')
        # body = self.text_processor.process(str(body_html))
        # date = soup.select_one('.article-date').get_text()
        # 
        # return Article(
        #     headline=headline,
        #     body=body,
        #     source=self.website_name,
        #     category=metadata.category,
        #     date=date,
        #     url=metadata.url,
        #     extraction_timestamp=datetime.now().isoformat()
        # )
        raise NotImplementedError("Implement with site-specific selectors")
    
    def get_next_page_url(self, current_url: str, html: str, current_page: int) -> Optional[str]:
        """Extract next page URL - IMPLEMENT WITH BEAUTIFULSOUP."""
        # Example implementation:
        # from bs4 import BeautifulSoup
        # soup = BeautifulSoup(html, 'lxml')
        # next_link = soup.select_one('a.next-page')
        # return next_link['href'] if next_link else None
        raise NotImplementedError("Implement with site-specific pagination")


if __name__ == "__main__":
    print("=" * 70)
    print("  BaseScraper - Strategy Pattern Interface")
    print("=" * 70)
    print("\nThis is an abstract base class. See ExampleScraper for template.")
    print("\nConcrete scrapers must implement:")
    print("  - get_category_urls()")
    print("  - get_article_list_url()")
    print("  - parse_article_list_page()")
    print("  - parse_article_page()")
    print("  - get_next_page_url()")
    print("\nSee scrapers/ directory for concrete implementations.")
