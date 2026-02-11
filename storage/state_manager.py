"""
StateManager - SQLite-based checkpoint and state persistence for Vincere scraper.

Provides idempotent URL tracking, pagination state management, and session tracking
for resumable, long-running scraping operations.
"""

import sqlite3
import hashlib
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from contextlib import contextmanager


class StateManager:
    """
    Manages scraper state persistence using SQLite.
    
    Features:
    - Idempotency: Tracks scraped URLs to prevent duplicate scraping
    - Resumability: Stores pagination state to resume after interruption
    - Session tracking: Audit trail for scraping sessions
    - Retry logic: Tracks failed URLs with retry counts
    """
    
    def __init__(self, db_path: str = "vincere_state.db"):
        """
        Initialize StateManager and create database schema.
        
        Args:
            db_path: Path to SQLite database file (created if doesn't exist)
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()
    
    def _initialize_database(self):
        """Create database schema from schema.sql file."""
        schema_path = Path(__file__).parent / "schema.sql"
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Read and execute schema file
            if schema_path.exists():
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema_sql = f.read()
                cursor.executescript(schema_sql)
            else:
                # Fallback: Create tables inline if schema.sql not found
                self._create_tables_inline(cursor)
            
            conn.commit()
    
    def _create_tables_inline(self, cursor):
        """Fallback method to create tables if schema.sql not found."""
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS scraped_urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL UNIQUE,
                website TEXT NOT NULL,
                category TEXT,
                article_id TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT CHECK(status IN ('success', 'failed', 'skipped')) DEFAULT 'success',
                retry_count INTEGER DEFAULT 0,
                error_message TEXT,
                content_checksum TEXT
            );
            
            CREATE INDEX IF NOT EXISTS idx_url ON scraped_urls(url);
            CREATE INDEX IF NOT EXISTS idx_website_category ON scraped_urls(website, category);
            CREATE INDEX IF NOT EXISTS idx_status ON scraped_urls(status);
            
            CREATE TABLE IF NOT EXISTS pagination_state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                website TEXT NOT NULL,
                category TEXT NOT NULL,
                last_page_index INTEGER DEFAULT 1,
                total_pages INTEGER,
                last_scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_complete BOOLEAN DEFAULT 0,
                UNIQUE(website, category)
            );
            
            CREATE INDEX IF NOT EXISTS idx_website_category_state ON pagination_state(website, category);
            
            CREATE TABLE IF NOT EXISTS scrape_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                website TEXT,
                category TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                status TEXT CHECK(status IN ('running', 'completed', 'failed', 'interrupted')) DEFAULT 'running',
                articles_scraped INTEGER DEFAULT 0,
                articles_failed INTEGER DEFAULT 0,
                articles_skipped INTEGER DEFAULT 0
            );
            
            CREATE INDEX IF NOT EXISTS idx_session_id ON scrape_sessions(session_id);
        """)
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections with proper cleanup."""
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()
    
    # ======================== URL Tracking (Idempotency) ========================
    
    def is_url_scraped(self, url: str, max_retries: int = 3) -> Tuple[bool, Optional[str]]:
        """
        Check if URL has been successfully scraped.
        
        Args:
            url: The URL to check
            max_retries: Maximum retry attempts allowed
        
        Returns:
            Tuple of (should_skip, reason):
            - (True, 'already_scraped') if successfully scraped
            - (True, 'max_retries_exceeded') if failed too many times
            - (False, None) if URL should be scraped
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT status, retry_count 
                FROM scraped_urls 
                WHERE url = ?
                """,
                (url,)
            )
            
            result = cursor.fetchone()
            
            if result is None:
                return False, None  # URL not seen before, should scrape
            
            status, retry_count = result['status'], result['retry_count']
            
            if status == 'success':
                return True, 'already_scraped'
            
            if status == 'failed' and retry_count >= max_retries:
                return True, 'max_retries_exceeded'
            
            # Status is 'failed' but retries available, or status is 'skipped'
            return False, None
    
    def mark_url_scraped(
        self,
        url: str,
        website: str,
        category: str,
        article_id: str,
        status: str = 'success',
        error_message: Optional[str] = None,
        content_checksum: Optional[str] = None
    ):
        """
        Mark a URL as scraped (success or failure).
        
        Args:
            url: The scraped URL
            website: Website name (e.g., 'adaderana')
            category: Article category (e.g., 'politics')
            article_id: Generated article ID
            status: 'success', 'failed', or 'skipped'
            error_message: Error details if status is 'failed'
            content_checksum: MD5 hash of article content
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if URL exists to increment retry_count
            cursor.execute("SELECT retry_count FROM scraped_urls WHERE url = ?", (url,))
            existing = cursor.fetchone()
            
            retry_count = 0
            if existing and status == 'failed':
                retry_count = existing['retry_count'] + 1
            
            cursor.execute(
                """
                INSERT INTO scraped_urls 
                (url, website, category, article_id, status, retry_count, error_message, content_checksum)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(url) DO UPDATE SET
                    status = excluded.status,
                    retry_count = excluded.retry_count,
                    error_message = excluded.error_message,
                    content_checksum = excluded.content_checksum,
                    scraped_at = CURRENT_TIMESTAMP
                """,
                (url, website, category, article_id, status, retry_count, error_message, content_checksum)
            )
            
            conn.commit()
    
    def get_failed_urls(self, website: Optional[str] = None, max_retries: int = 3) -> List[Dict]:
        """
        Get URLs that failed but can be retried.
        
        Args:
            website: Filter by website (None for all)
            max_retries: Maximum retry limit
        
        Returns:
            List of dict with url, website, category, retry_count, error_message
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT url, website, category, retry_count, error_message
                FROM scraped_urls
                WHERE status = 'failed' AND retry_count < ?
            """
            params = [max_retries]
            
            if website:
                query += " AND website = ?"
                params.append(website)
            
            cursor.execute(query, params)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_scraped_count(self, website: Optional[str] = None, category: Optional[str] = None) -> Dict[str, int]:
        """
        Get statistics on scraped URLs.
        
        Args:
            website: Filter by website
            category: Filter by category
        
        Returns:
            Dict with counts: {'success': N, 'failed': M, 'skipped': K, 'total': T}
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT status, COUNT(*) as count FROM scraped_urls WHERE 1=1"
            params = []
            
            if website:
                query += " AND website = ?"
                params.append(website)
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            query += " GROUP BY status"
            
            cursor.execute(query, params)
            
            counts = {'success': 0, 'failed': 0, 'skipped': 0, 'total': 0}
            for row in cursor.fetchall():
                counts[row['status']] = row['count']
                counts['total'] += row['count']
            
            return counts
    
    # ======================== Pagination State (Resumability) ========================
    
    def get_pagination_state(self, website: str, category: str) -> Optional[Dict]:
        """
        Get pagination state for a website-category pair.
        
        Args:
            website: Website name
            category: Category name
        
        Returns:
            Dict with last_page_index, total_pages, is_complete, last_scraped_at
            or None if no state exists
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT last_page_index, total_pages, is_complete, last_scraped_at
                FROM pagination_state
                WHERE website = ? AND category = ?
                """,
                (website, category)
            )
            
            result = cursor.fetchone()
            return dict(result) if result else None
    
    def update_pagination_state(
        self,
        website: str,
        category: str,
        last_page_index: int,
        total_pages: Optional[int] = None,
        is_complete: bool = False
    ):
        """
        Update or create pagination state.
        
        Args:
            website: Website name
            category: Category name
            last_page_index: Last successfully scraped page number
            total_pages: Total pages if known
            is_complete: Whether category is fully scraped
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO pagination_state 
                (website, category, last_page_index, total_pages, is_complete)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(website, category) DO UPDATE SET
                    last_page_index = excluded.last_page_index,
                    total_pages = excluded.total_pages,
                    is_complete = excluded.is_complete,
                    last_scraped_at = CURRENT_TIMESTAMP
                """,
                (website, category, last_page_index, total_pages, is_complete)
            )
            conn.commit()
    
    def reset_pagination_state(self, website: str, category: Optional[str] = None):
        """
        Reset pagination state (useful for fresh scraping).
        
        Args:
            website: Website name
            category: Category name (None to reset all categories for website)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if category:
                cursor.execute(
                    "DELETE FROM pagination_state WHERE website = ? AND category = ?",
                    (website, category)
                )
            else:
                cursor.execute("DELETE FROM pagination_state WHERE website = ?", (website,))
            
            conn.commit()
    
    def get_incomplete_categories(self, website: Optional[str] = None) -> List[Dict]:
        """
        Get categories that are not fully scraped.
        
        Args:
            website: Filter by website (None for all)
        
        Returns:
            List of dict with website, category, last_page_index
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT website, category, last_page_index, total_pages
                FROM pagination_state
                WHERE is_complete = 0
            """
            params = []
            
            if website:
                query += " AND website = ?"
                params.append(website)
            
            cursor.execute(query, params)
            
            return [dict(row) for row in cursor.fetchall()]
    
    # ======================== Session Management ========================
    
    def create_session(self, website: Optional[str] = None, category: Optional[str] = None) -> str:
        """
        Create a new scraping session.
        
        Args:
            website: Target website
            category: Target category
        
        Returns:
            Session ID (UUID)
        """
        session_id = str(uuid.uuid4())
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO scrape_sessions (session_id, website, category)
                VALUES (?, ?, ?)
                """,
                (session_id, website, category)
            )
            conn.commit()
        
        return session_id
    
    def update_session_stats(
        self,
        session_id: str,
        articles_scraped: Optional[int] = None,
        articles_failed: Optional[int] = None,
        articles_skipped: Optional[int] = None,
        status: Optional[str] = None
    ):
        """
        Update session statistics and status.
        
        Args:
            session_id: Session UUID
            articles_scraped: Increment successful scrapes count
            articles_failed: Increment failed scrapes count
            articles_skipped: Increment skipped scrapes count
            status: Update session status ('running', 'completed', 'failed', 'interrupted')
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if articles_scraped is not None:
                updates.append("articles_scraped = articles_scraped + ?")
                params.append(articles_scraped)
            
            if articles_failed is not None:
                updates.append("articles_failed = articles_failed + ?")
                params.append(articles_failed)
            
            if articles_skipped is not None:
                updates.append("articles_skipped = articles_skipped + ?")
                params.append(articles_skipped)
            
            if status:
                updates.append("status = ?")
                params.append(status)
                
                if status in ('completed', 'failed', 'interrupted'):
                    updates.append("completed_at = CURRENT_TIMESTAMP")
            
            if updates:
                params.append(session_id)
                query = f"UPDATE scrape_sessions SET {', '.join(updates)} WHERE session_id = ?"
                cursor.execute(query, params)
                conn.commit()
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """
        Get detailed session information.
        
        Args:
            session_id: Session UUID
        
        Returns:
            Dict with session details or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM scrape_sessions WHERE session_id = ?",
                (session_id,)
            )
            
            result = cursor.fetchone()
            return dict(result) if result else None
    
    def get_recent_sessions(self, limit: int = 10) -> List[Dict]:
        """
        Get recent scraping sessions.
        
        Args:
            limit: Maximum number of sessions to return
        
        Returns:
            List of session dicts ordered by start time (newest first)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM scrape_sessions
                ORDER BY started_at DESC
                LIMIT ?
                """,
                (limit,)
            )
            
            return [dict(row) for row in cursor.fetchall()]
    
    # ======================== Utility Methods ========================
    
    @staticmethod
    def generate_article_id(url: str) -> str:
        """
        Generate a unique article ID from URL using MD5 hash.
        
        Args:
            url: Article URL
        
        Returns:
            8-character hex string (first 8 chars of MD5 hash)
        """
        return hashlib.md5(url.encode('utf-8')).hexdigest()[:8]
    
    @staticmethod
    def generate_content_checksum(content: str) -> str:
        """
        Generate MD5 checksum of article content for change detection.
        
        Args:
            content: Article body text
        
        Returns:
            Full MD5 hash as hex string
        """
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def close(self):
        """Cleanup method (no-op for context manager pattern, but included for compatibility)."""
        pass


# Convenience function for quick testing
if __name__ == "__main__":
    # Demo usage
    manager = StateManager("test_vincere.db")
    
    # Create a session
    session_id = manager.create_session(website="adaderana", category="politics")
    print(f"Created session: {session_id}")
    
    # Check if URL is scraped
    test_url = "https://example.com/article1"
    is_scraped, reason = manager.is_url_scraped(test_url)
    print(f"URL scraped: {is_scraped}, Reason: {reason}")
    
    # Mark URL as scraped
    article_id = StateManager.generate_article_id(test_url)
    manager.mark_url_scraped(
        url=test_url,
        website="adaderana",
        category="politics",
        article_id=article_id,
        status="success"
    )
    print(f"Marked URL as scraped with ID: {article_id}")
    
    # Check again
    is_scraped, reason = manager.is_url_scraped(test_url)
    print(f"URL scraped now: {is_scraped}, Reason: {reason}")
    
    # Update pagination
    manager.update_pagination_state("adaderana", "politics", last_page_index=5)
    state = manager.get_pagination_state("adaderana", "politics")
    print(f"Pagination state: {state}")
    
    # Update session stats
    manager.update_session_stats(session_id, articles_scraped=1)
    session_info = manager.get_session_info(session_id)
    print(f"Session info: {session_info}")
    
    print("\n✓ StateManager test completed successfully!")
