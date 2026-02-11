"""
Corpus Analytics Utility for Vincere Framework

Analyzes the scraped corpus to provide statistics on:
- Total article counts by site and category
- Average word counts per article
- Progress toward the 100,000 article goal
- Data density metrics

Usage:
    python analyze_corpus.py
    python analyze_corpus.py --corpus-dir ./vincere_corpus
    python analyze_corpus.py --export stats.json
"""

import argparse
import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, Tuple, List
from datetime import datetime


class CorpusAnalyzer:
    """
    Analyzes the Vincere corpus and generates statistics.
    """
    
    def __init__(self, corpus_dir: str = './vincere_corpus'):
        """
        Initialize corpus analyzer.
        
        Args:
            corpus_dir: Path to corpus directory
        """
        self.corpus_dir = Path(corpus_dir)
        
        if not self.corpus_dir.exists():
            raise ValueError(f"Corpus directory not found: {corpus_dir}")
        
        # Statistics storage
        self.site_stats = defaultdict(lambda: defaultdict(int))  # site -> category -> count
        self.word_counts = defaultdict(lambda: defaultdict(list))  # site -> category -> [word_counts]
        self.total_articles = 0
        self.total_words = 0
    
    def analyze(self) -> Dict:
        """
        Scan corpus and collect statistics.
        
        Returns:
            Dict containing all statistics
        """
        print("🔍 Scanning corpus directory...")
        print(f"📁 Path: {self.corpus_dir.absolute()}\n")
        
        # Walk through site directories
        for site_dir in self.corpus_dir.iterdir():
            if not site_dir.is_dir():
                continue
            
            site_name = site_dir.name
            print(f"  Scanning: {site_name}...")
            
            # Walk through category directories
            for category_dir in site_dir.iterdir():
                if not category_dir.is_dir():
                    continue
                
                category_name = category_dir.name
                
                # Count JSON files (articles) in this category
                article_files = list(category_dir.glob('*.json'))
                article_count = len(article_files)
                
                if article_count > 0:
                    self.site_stats[site_name][category_name] = article_count
                    self.total_articles += article_count
                    
                    # Read articles to get word counts
                    for article_file in article_files:
                        try:
                            with open(article_file, 'r', encoding='utf-8') as f:
                                article_data = json.load(f)
                                word_count = article_data.get('word_count', 0)
                                
                                if word_count > 0:
                                    self.word_counts[site_name][category_name].append(word_count)
                                    self.total_words += word_count
                        
                        except Exception as e:
                            print(f"    ⚠️  Error reading {article_file.name}: {e}")
                            continue
        
        print(f"\n✓ Scan complete: {self.total_articles} articles found\n")
        
        return self._generate_report()
    
    def _generate_report(self) -> Dict:
        """
        Generate comprehensive statistics report.
        
        Returns:
            Dict with all statistics
        """
        report = {
            'scan_timestamp': datetime.now().isoformat(),
            'corpus_path': str(self.corpus_dir.absolute()),
            'total_articles': self.total_articles,
            'total_words': self.total_words,
            'average_words_per_article': self.total_words / self.total_articles if self.total_articles > 0 else 0,
            'goal': 100000,
            'progress_percent': (self.total_articles / 100000) * 100,
            'remaining': 100000 - self.total_articles,
            'sites': {}
        }
        
        # Per-site statistics
        for site_name, categories in self.site_stats.items():
            site_total = sum(categories.values())
            site_words = sum(sum(counts) for counts in self.word_counts[site_name].values())
            site_avg_words = site_words / site_total if site_total > 0 else 0
            
            report['sites'][site_name] = {
                'total_articles': site_total,
                'total_words': site_words,
                'average_words': site_avg_words,
                'categories': {}
            }
            
            # Per-category statistics
            for category_name, count in categories.items():
                category_words = self.word_counts[site_name][category_name]
                avg_words = sum(category_words) / len(category_words) if category_words else 0
                
                report['sites'][site_name]['categories'][category_name] = {
                    'article_count': count,
                    'total_words': sum(category_words),
                    'average_words': avg_words
                }
        
        return report
    
    def print_report(self, report: Dict):
        """
        Print formatted report to console.
        
        Args:
            report: Statistics report dict
        """
        print("=" * 80)
        print("  VINCERE CORPUS ANALYTICS REPORT")
        print("=" * 80)
        print(f"  Generated: {report['scan_timestamp']}")
        print(f"  Corpus Path: {report['corpus_path']}")
        print("=" * 80 + "\n")
        
        # Overall statistics
        print("📊 OVERALL STATISTICS")
        print("-" * 80)
        print(f"  Total Articles:           {report['total_articles']:,}")
        print(f"  Total Words:              {report['total_words']:,}")
        print(f"  Average Words/Article:    {report['average_words_per_article']:.1f}")
        print(f"\n  Goal:                     {report['goal']:,} articles")
        print(f"  Progress:                 {report['progress_percent']:.2f}%")
        print(f"  Remaining:                {report['remaining']:,} articles")
        print("-" * 80 + "\n")
        
        # Per-site breakdown
        print("🌐 BY SITE")
        print("-" * 80)
        
        # Table header
        print(f"{'Site':<20} {'Articles':<12} {'Total Words':<15} {'Avg Words':<12}")
        print("-" * 80)
        
        # Sort sites by article count (descending)
        sites_sorted = sorted(
            report['sites'].items(),
            key=lambda x: x[1]['total_articles'],
            reverse=True
        )
        
        for site_name, site_data in sites_sorted:
            print(
                f"{site_name:<20} "
                f"{site_data['total_articles']:<12,} "
                f"{site_data['total_words']:<15,} "
                f"{site_data['average_words']:<12,.1f}"
            )
        
        print("-" * 80 + "\n")
        
        # Per-category breakdown (detailed)
        print("📁 BY SITE AND CATEGORY")
        print("-" * 80)
        
        for site_name, site_data in sites_sorted:
            print(f"\n  {site_name.upper()}")
            print("  " + "-" * 76)
            
            # Table header
            print(f"  {'Category':<25} {'Articles':<12} {'Total Words':<15} {'Avg Words':<12}")
            print("  " + "-" * 76)
            
            # Sort categories by article count (descending)
            categories_sorted = sorted(
                site_data['categories'].items(),
                key=lambda x: x[1]['article_count'],
                reverse=True
            )
            
            for category_name, category_data in categories_sorted:
                print(
                    f"  {category_name:<25} "
                    f"{category_data['article_count']:<12,} "
                    f"{category_data['total_words']:<15,} "
                    f"{category_data['average_words']:<12,.1f}"
                )
            
            print("  " + "-" * 76)
            print(
                f"  {'TOTAL':<25} "
                f"{site_data['total_articles']:<12,} "
                f"{site_data['total_words']:<15,} "
                f"{site_data['average_words']:<12,.1f}"
            )
        
        print("\n" + "=" * 80)
        
        # Data quality insights
        print("\n💡 DATA QUALITY INSIGHTS")
        print("-" * 80)
        
        avg_words = report['average_words_per_article']
        
        if avg_words >= 400:
            quality = "Excellent"
            emoji = "🟢"
        elif avg_words >= 250:
            quality = "Good"
            emoji = "🟡"
        else:
            quality = "Low (consider filtering short articles)"
            emoji = "🔴"
        
        print(f"  {emoji} Average article length: {avg_words:.1f} words - {quality}")
        
        # Progress toward goal
        progress = report['progress_percent']
        
        if progress >= 100:
            milestone = "🎉 Goal achieved!"
        elif progress >= 75:
            milestone = "🚀 Almost there!"
        elif progress >= 50:
            milestone = "💪 Halfway to goal"
        elif progress >= 25:
            milestone = "📈 Making good progress"
        else:
            milestone = "🌱 Just getting started"
        
        print(f"  {milestone} ({progress:.1f}% of 100K target)")
        
        # Recommendations
        print("\n📋 RECOMMENDATIONS")
        print("-" * 80)
        
        if report['total_articles'] < 100000:
            remaining = report['remaining']
            
            # Estimate based on current distribution
            num_sites = len(report['sites'])
            per_site = remaining // num_sites if num_sites > 0 else remaining
            
            print(f"  • Need {remaining:,} more articles to reach 100K goal")
            print(f"  • Suggested: ~{per_site:,} articles per site")
            
            if avg_words < 250:
                print(f"  • Consider filtering articles with <150 words to improve quality")
        else:
            print(f"  • ✓ Goal achieved! Total: {report['total_articles']:,} articles")
            print(f"  • Consider data cleaning and deduplication before model training")
        
        print("-" * 80 + "\n")
    
    def export_json(self, report: Dict, output_path: str):
        """
        Export report as JSON file.
        
        Args:
            report: Statistics report dict
            output_path: Path to output JSON file
        """
        output_file = Path(output_path)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Report exported to: {output_file.absolute()}")


def main():
    """Main entry point for corpus analysis utility."""
    parser = argparse.ArgumentParser(
        description='Analyze Vincere corpus statistics',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze default corpus directory
  python analyze_corpus.py
  
  # Analyze custom corpus directory
  python analyze_corpus.py --corpus-dir ./my_corpus
  
  # Export statistics to JSON
  python analyze_corpus.py --export stats.json
  
  # Both
  python analyze_corpus.py --corpus-dir ./vincere_corpus --export stats.json
        """
    )
    
    parser.add_argument(
        '--corpus-dir',
        type=str,
        default='./vincere_corpus',
        help='Path to corpus directory (default: ./vincere_corpus)'
    )
    
    parser.add_argument(
        '--export',
        type=str,
        help='Export statistics to JSON file'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize analyzer
        analyzer = CorpusAnalyzer(corpus_dir=args.corpus_dir)
        
        # Run analysis
        report = analyzer.analyze()
        
        # Print report
        analyzer.print_report(report)
        
        # Export if requested
        if args.export:
            analyzer.export_json(report, args.export)
        
    except ValueError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
