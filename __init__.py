"""
Vincere - High-scale Sinhala News Scraping Framework

A production-grade, resumable news scraper for building ML-ready Sinhala text corpora.

Features:
- Distributed JSON file storage by website/category/article_id
- SQLite-based checkpoint system for idempotency and resumability
- Strategy pattern for multi-site support
- Sinhala-specific text preprocessing (Unicode NFC normalization)
- Robust error handling with retry logic
- Rate limiting and user-agent rotation
"""

__version__ = '1.0.0'
__author__ = 'Vincere Research Team'

__all__ = []
