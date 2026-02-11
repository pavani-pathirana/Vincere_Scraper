"""
Scrapers module for Vincere scraper.

Contains concrete scraper implementations for each news website.
"""

from scrapers.adaderana_scraper import AdaDeranaScraper
from scrapers.hirunews_scraper import HiruNewsScraper
from scrapers.itn_scraper import ITNScraper
from scrapers.newsfirst_scraper import NewsFirstScraper
from scrapers.lankatruth_scraper import LankaTruthScraper

__all__ = [
    'AdaDeranaScraper',
    'HiruNewsScraper',
    'ITNScraper',
    'NewsFirstScraper',
    'LankaTruthScraper',
]
