"""
Vincere - High-Scale Sinhala News Scraping Framework

Main CLI entry point for orchestrating scraping operations across multiple
news websites with support for resumption, limiting, and graceful shutdown.

Usage:
    python main.py --site adaderana --category politics --limit 2000
    python main.py --site hirunews --category local --limit 5000
    python main.py --site all --limit 10000
    python main.py --resume
"""

import argparse
import logging
import signal
import sys
from typing import Dict, Optional, Type
from pathlib import Path

from core.session_manager import SessionManager
from core.base_scraper import BaseScraper
from storage.state_manager import StateManager
from storage.file_writer import FileWriter
from processors.sinhala_normalizer import TextProcessor

# Import concrete scrapers
from scrapers.adaderana_scraper import AdaDeranaScraper
from scrapers.hirunews_scraper import HiruNewsScraper
from scrapers.itn_scraper import ITNScraper
from scrapers.newsfirst_scraper import NewsFirstScraper
from scrapers.lankatruth_scraper import LankaTruthScraper
from scrapers.lankadeepa_scraper import LankadeepaScraper
from scrapers.silumina_scraper import SiluminaScraper
from scrapers.bbc_sinhala_scraper import BBCSinhalaScraper


# Global flag for graceful shutdown
shutdown_requested = False

# Store state manager globally for signal handler access
global_state_manager: Optional[StateManager] = None


def signal_handler(signum, frame):
    """
    Handle SIGINT (Ctrl+C) and SIGTERM for graceful shutdown.
    
    Saves pagination state to database before exiting.
    """
    global shutdown_requested, global_state_manager
    
    signal_name = signal.Signals(signum).name
    
    print(f"\n\n{'='*70}")
    print(f"  ⚠️  {signal_name} received - Initiating graceful shutdown...")
    print(f"{'='*70}")
    
    shutdown_requested = True
    
    # Save state
    if global_state_manager:
        print("  📦 Saving pagination state to database...")
        try:
            # State is automatically saved after each page by BaseScraper
            # But we can log statistics here
            stats = global_state_manager.get_statistics()
            print(f"  ✓ State saved:")
            print(f"    - Total URLs scraped: {stats['total_urls_scraped']}")
            print(f"    - Categories tracked: {stats['categories_with_pagination']}")
            print(f"  ✓ Safe to exit - progress preserved")
        except Exception as e:
            print(f"  ⚠️  Error during state save: {e}")
    
    print(f"{'='*70}\n")
    
    # Exit gracefully
    sys.exit(0)


def setup_logging(log_level: str = 'INFO', log_file: Optional[str] = None):
    """
    Configure logging with console and optional file output.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file path for log output
    """
    # Create formatters
    console_formatter = logging.Formatter(
        '%(levelname)-8s | %(name)-25s | %(message)s'
    )
    
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)  # Console always INFO or above
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Suppress overly verbose third-party loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)


def get_scraper_class(site_name: str) -> Type[BaseScraper]:
    """
    Get scraper class for specified site.
    
    Args:
        site_name: Name of the site (e.g., 'adaderana', 'hirunews')
    
    Returns:
        Scraper class
    
    Raises:
        ValueError: If site not supported
    """
    scrapers = {
        'adaderana': AdaDeranaScraper,
        'hirunews': HiruNewsScraper,
        'itn': ITNScraper,
        'newsfirst': NewsFirstScraper,
        'lankatruth': LankaTruthScraper,
        'lankadeepa': LankadeepaScraper,
        'silumina': SiluminaScraper,
        'bbc': BBCSinhalaScraper,
    }
    
    site_name_lower = site_name.lower()
    
    if site_name_lower not in scrapers:
        available = ', '.join(scrapers.keys())
        raise ValueError(f"Unsupported site '{site_name}'. Available: {available}")
    
    return scrapers[site_name_lower]


def initialize_scraper(
    site_name: str,
    session_manager: SessionManager,
    state_manager: StateManager,
    file_writer: FileWriter,
    text_processor: TextProcessor
) -> BaseScraper:
    """
    Initialize scraper instance for specified site.
    
    Args:
        site_name: Name of the site
        session_manager: Shared session manager
        state_manager: Shared state manager
        file_writer: Shared file writer
        text_processor: Shared text processor
    
    Returns:
        Initialized scraper instance
    """
    scraper_class = get_scraper_class(site_name)
    
    scraper = scraper_class(
        website_name=site_name,
        session_manager=session_manager,
        state_manager=state_manager,
        file_writer=file_writer,
        text_processor=text_processor
    )
    
    return scraper


def scrape_site(
    site_name: str,
    category: Optional[str],
    limit: Optional[int],
    resume: bool,
    session_manager: SessionManager,
    state_manager: StateManager,
    file_writer: FileWriter,
    text_processor: TextProcessor
) -> Dict[str, int]:
    """
    Scrape a single site with specified parameters.
    
    Args:
        site_name: Name of site to scrape
        category: Specific category or None for all
        limit: Maximum articles to scrape
        resume: Whether to resume from last state
        session_manager: SessionManager instance
        state_manager: StateManager instance
        file_writer: FileWriter instance
        text_processor: TextProcessor instance
    
    Returns:
        Dict with statistics (total_articles, total_pages, etc.)
    """
    global shutdown_requested
    
    logger = logging.getLogger(__name__)
    
    # Initialize scraper
    logger.info(f"Initializing scraper for: {site_name}")
    scraper = initialize_scraper(
        site_name,
        session_manager,
        state_manager,
        file_writer,
        text_processor
    )
    
    # Get categories
    categories = scraper.get_category_urls()
    
    # Filter to specific category if requested
    if category:
        if category not in categories:
            available = ', '.join(categories.keys())
            raise ValueError(f"Category '{category}' not found for {site_name}. Available: {available}")
        categories = {category: categories[category]}
    
    logger.info(f"Target categories for {site_name}: {', '.join(categories.keys())}")
    
    # Track overall stats
    total_stats = {
        'total_articles': 0,
        'total_pages': 0,
        'categories_completed': 0,
        'categories_failed': 0
    }
    
    # Scrape each category
    for cat_name, cat_url in categories.items():
        if shutdown_requested:
            logger.warning("Shutdown requested - stopping category iteration")
            break
        
        try:
            logger.info(f"\n{'='*70}")
            logger.info(f"  Scraping {site_name} - {cat_name}")
            logger.info(f"{'='*70}")
            
            # Calculate max pages from limit (if specified)
            max_pages = None
            if limit:
                # Estimate ~20 articles per page
                articles_per_page = 20
                remaining_limit = limit - total_stats['total_articles']
                
                if remaining_limit <= 0:
                    logger.info(f"Article limit ({limit}) reached - stopping")
                    break
                
                max_pages = max(1, remaining_limit // articles_per_page)
                logger.info(f"Max pages for this category: {max_pages} (to reach limit of {limit})")
            
            # Scrape category (resume is handled internally by BaseScraper)
            stats = scraper.scrape_category(
                category=cat_name,
                category_url=cat_url,
                max_pages=max_pages,
                resume=resume
            )
            
            # Update overall stats
            total_stats['total_articles'] += stats['articles_scraped']
            total_stats['total_pages'] += stats['pages_scraped']
            total_stats['categories_completed'] += 1
            
            logger.info(f"✓ Completed {cat_name}: {stats['articles_scraped']} articles, {stats['pages_scraped']} pages")
            
        except Exception as e:
            logger.error(f"✗ Failed to scrape {cat_name}: {e}", exc_info=True)
            total_stats['categories_failed'] += 1
            continue
    
    return total_stats


def main():
    """Main entry point for Vincere CLI."""
    global global_state_manager
    
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Vincere - High-Scale Sinhala News Scraping Framework',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape Ada Derana politics category (limit 2000 articles)
  python main.py --site adaderana --category politics --limit 2000
  
  # Scrape all Hiru News categories (limit 5000 articles total)
  python main.py --site hirunews --limit 5000
  
  # Scrape all sites, all categories (limit 10000 articles total)
  python main.py --site all --limit 10000
  
  # Resume all unfinished work across all sites
  python main.py --resume
  
  # Debug mode with detailed logging
  python main.py --site lankadeepa --limit 200
  python main.py --site adaderana --category sports --debug
        """
    )
    
    parser.add_argument(
        '--site',
        type=str,
        help='Site to scrape (adaderana, hirunews, or "all" for all sites)',
        default=None
    )
    
    parser.add_argument(
        '--category',
        type=str,
        help='Specific category to scrape (or omit for all categories)',
        default=None
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        help='Maximum number of articles to scrape (across all categories)',
        default=None
    )
    
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume unfinished work from last session'
    )
    
    parser.add_argument(
        '--db',
        type=str,
        help='Path to SQLite database (default: vincere_state.db)',
        default='vincere_state.db'
    )
    
    parser.add_argument(
        '--corpus-dir',
        type=str,
        help='Directory for corpus output (default: ./vincere_corpus)',
        default='./vincere_corpus'
    )
    
    parser.add_argument(
        '--rate-limit',
        type=int,
        help='Requests per minute (default: 20)',
        default=20
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        help='Log file path (default: vincere.log)',
        default='vincere.log'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.resume and not args.site:
        parser.error("Either --site or --resume must be specified")
    
    # Setup logging
    log_level = 'DEBUG' if args.debug else 'INFO'
    setup_logging(log_level=log_level, log_file=args.log_file)
    
    logger = logging.getLogger(__name__)
    
    # Print banner
    print("\n" + "="*70)
    print("  VINCERE - Sinhala News Scraping Framework")
    print("  High-Quality Corpus Builder for ML Training")
    print("="*70 + "\n")
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Signal handlers registered (Ctrl+C for graceful shutdown)")
    
    try:
        # Initialize shared components
        logger.info("Initializing components...")
        
        session_manager = SessionManager(requests_per_minute=args.rate_limit)
        logger.info(f"✓ SessionManager initialized (rate: {args.rate_limit} req/min)")
        
        state_manager = StateManager(args.db)
        global_state_manager = state_manager  # Store globally for signal handler
        logger.info(f"✓ StateManager initialized (db: {args.db})")
        
        file_writer = FileWriter(args.corpus_dir)
        logger.info(f"✓ FileWriter initialized (corpus: {args.corpus_dir})")
        
        text_processor = TextProcessor()
        logger.info(f"✓ TextProcessor initialized")
        
        # Determine which sites to scrape
        if args.resume:
            # Resume mode: scrape all sites with saved pagination state
            logger.info("Resume mode: Loading saved pagination states...")
            
            # Get all pagination states from database
            # For now, we'll scrape all supported sites
            sites_to_scrape = ['adaderana', 'hirunews', 'itn', 'newsfirst', 'lankatruth', 'lankadeepa']
            
            logger.info(f"Will attempt to resume: {', '.join(sites_to_scrape)}")
        
        elif args.site.lower() == 'all':
            sites_to_scrape = ['adaderana', 'hirunews', 'itn', 'newsfirst', 'lankatruth', 'lankadeepa']
            logger.info(f"Scraping all sites: {', '.join(sites_to_scrape)}")
        
        else:
            sites_to_scrape = [args.site]
            logger.info(f"Scraping single site: {args.site}")
        
        # Track global stats
        global_stats = {
            'total_articles': 0,
            'total_pages': 0,
            'sites_completed': 0,
            'sites_failed': 0
        }
        
        # Scrape each site
        for site_name in sites_to_scrape:
            if shutdown_requested:
                logger.warning("Shutdown requested - stopping site iteration")
                break
            
            try:
                logger.info(f"\n{'#'*70}")
                logger.info(f"  SITE: {site_name.upper()}")
                logger.info(f"{'#'*70}\n")
                
                site_stats = scrape_site(
                    site_name=site_name,
                    category=args.category,
                    limit=args.limit,
                    resume=args.resume,
                    session_manager=session_manager,
                    state_manager=state_manager,
                    file_writer=file_writer,
                    text_processor=text_processor
                )
                
                # Update global stats
                global_stats['total_articles'] += site_stats['total_articles']
                global_stats['total_pages'] += site_stats['total_pages']
                global_stats['sites_completed'] += 1
                
                logger.info(f"\n✓ Completed {site_name}:")
                logger.info(f"  - Articles: {site_stats['total_articles']}")
                logger.info(f"  - Pages: {site_stats['total_pages']}")
                logger.info(f"  - Categories completed: {site_stats['categories_completed']}")
                
                # Check if limit reached
                if args.limit and global_stats['total_articles'] >= args.limit:
                    logger.info(f"\nArticle limit ({args.limit}) reached - stopping")
                    break
                
            except Exception as e:
                logger.error(f"✗ Failed to scrape {site_name}: {e}", exc_info=True)
                global_stats['sites_failed'] += 1
                continue
        
        # Print final summary
        print("\n" + "="*70)
        print("  SCRAPING COMPLETE")
        print("="*70)
        print(f"  Total Articles Scraped: {global_stats['total_articles']}")
        print(f"  Total Pages Processed:  {global_stats['total_pages']}")
        print(f"  Sites Completed:        {global_stats['sites_completed']}")
        print(f"  Sites Failed:           {global_stats['sites_failed']}")
        print("="*70 + "\n")
        
        # Show corpus statistics
        logger.info("Corpus statistics:")
        corpus_stats = file_writer.get_corpus_stats()
        logger.info(f"  Total articles in corpus: {corpus_stats['total_articles']}")
        for website, website_data in corpus_stats.get('websites', {}).items():
            logger.info(f"  {website}: {website_data['total']} articles")
            for category, count in website_data.get('categories', {}).items():
                logger.info(f"    - {category}: {count} articles")
        
        logger.info(f"\n✓ Corpus saved to: {args.corpus_dir}")
        logger.info(f"✓ State saved to: {args.db}")
        logger.info(f"✓ Logs saved to: {args.log_file}")
        
    except KeyboardInterrupt:
        # Already handled by signal handler
        pass
    
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    
    finally:
        # Cleanup
        if session_manager:
            session_manager.close()
            logger.info("✓ SessionManager closed")


if __name__ == "__main__":
    main()
