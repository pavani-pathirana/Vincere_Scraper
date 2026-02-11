"""
Core module for Vincere scraper.

Contains base scraper classes, session management, and strategy pattern implementation.
"""

from .session_manager import SessionManager, UserAgentRotator, RateLimiter
from .base_scraper import BaseScraper, Article, ArticleMetadata

__all__ = [
    'SessionManager',
    'UserAgentRotator',
    'RateLimiter',
    'BaseScraper',
    'Article',
    'ArticleMetadata'
]
