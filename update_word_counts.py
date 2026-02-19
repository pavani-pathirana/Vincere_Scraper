"""
Retroactive Word Count Calculator for Vincere Corpus

Scans all existing JSON files and adds missing word_count fields.
This updates articles in-place so that analyze_corpus.py can show
complete word count statistics by site and category.
"""

import json
import os
from pathlib import Path
from typing import Dict, Tuple
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def calculate_word_count(text: str) -> int:
    """Calculate word count from text."""
    if not text:
        return 0
    return len(text.split())


def update_article_word_count(file_path: Path) -> Tuple[bool, int]:
    """
    Update word count in a single article JSON file.
    
    Returns:
        Tuple[bool, int]: (success, word_count)
    """
    try:
        # Read existing article
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            article = json.load(f)
        
        # Check if word_count already exists
        if article.get('word_count') and article['word_count'] > 0:
            return (True, article['word_count'])
        
        # Calculate word count from body
        body = article.get('body', '')
        word_count = calculate_word_count(body)
        
        # Update article data
        article['word_count'] = word_count
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(article, f, ensure_ascii=False, indent=2)
        
        return (True, word_count)
    
    except Exception as e:
        logger.error(f"Failed to update {file_path}: {e}")
        return (False, 0)


def process_corpus(corpus_dir: str = "vincere_corpus") -> Dict[str, Dict]:
    """
    Process entire corpus and update word counts.
    
    Returns:
        Dict with statistics per site
    """
    corpus_path = Path(corpus_dir)
    
    if not corpus_path.exists():
        logger.error(f"Corpus directory not found: {corpus_path}")
        return {}
    
    stats = {}
    total_processed = 0
    total_updated = 0
    total_failed = 0
    
    # Iterate through all site directories
    for site_dir in sorted(corpus_path.iterdir()):
        if not site_dir.is_dir():
            continue
        
        site_name = site_dir.name
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing site: {site_name}")
        logger.info(f"{'='*60}")
        
        site_stats = {
            'processed': 0,
            'updated': 0,
            'failed': 0,
            'total_words': 0,
            'categories': {}
        }
        
        # Iterate through category directories
        for category_dir in sorted(site_dir.iterdir()):
            if not category_dir.is_dir():
                continue
            
            category_name = category_dir.name
            category_stats = {
                'processed': 0,
                'updated': 0,
                'failed': 0,
                'total_words': 0
            }
            
            # Process all JSON files in category
            json_files = list(category_dir.glob('*.json'))
            logger.info(f"  {category_name}: {len(json_files)} articles")
            
            for json_file in json_files:
                success, word_count = update_article_word_count(json_file)
                
                category_stats['processed'] += 1
                site_stats['processed'] += 1
                total_processed += 1
                
                if success:
                    category_stats['updated'] += 1
                    category_stats['total_words'] += word_count
                    site_stats['updated'] += 1
                    site_stats['total_words'] += word_count
                    total_updated += 1
                else:
                    category_stats['failed'] += 1
                    site_stats['failed'] += 1
                    total_failed += 1
                
                # Progress indicator every 1000 articles
                if category_stats['processed'] % 1000 == 0:
                    logger.info(f"    Progress: {category_stats['processed']}/{len(json_files)}")
            
            site_stats['categories'][category_name] = category_stats
            
            # Category summary
            avg_words = category_stats['total_words'] / category_stats['updated'] if category_stats['updated'] > 0 else 0
            logger.info(f"    ✓ {category_stats['updated']} updated, avg {avg_words:.1f} words")
        
        stats[site_name] = site_stats
        
        # Site summary
        avg_words = site_stats['total_words'] / site_stats['updated'] if site_stats['updated'] > 0 else 0
        logger.info(f"\n  Site Total: {site_stats['updated']}/{site_stats['processed']} articles")
        logger.info(f"  Average: {avg_words:.1f} words/article")
        logger.info(f"  Total Words: {site_stats['total_words']:,}")
    
    # Overall summary
    logger.info(f"\n{'='*60}")
    logger.info(f"OVERALL SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"Total Articles Processed: {total_processed:,}")
    logger.info(f"Successfully Updated:     {total_updated:,}")
    logger.info(f"Failed:                   {total_failed:,}")
    
    if total_updated > 0:
        total_words = sum(s['total_words'] for s in stats.values())
        overall_avg = total_words / total_updated
        logger.info(f"Total Words in Corpus:    {total_words:,}")
        logger.info(f"Overall Average:          {overall_avg:.1f} words/article")
    
    return stats


if __name__ == "__main__":
    logger.info("Starting retroactive word count calculation...")
    logger.info("This may take several minutes for large corpora...\n")
    
    stats = process_corpus()
    
    if stats:
        logger.info("\n✓ Word count calculation complete!")
        logger.info("Run 'python analyze_corpus.py' to see updated statistics.")
    else:
        logger.error("\n✗ Failed to process corpus")
