"""
Scrapers module for Vincere scraper.

Contains concrete scraper implementations for each news website.
"""

from scrapers.adaderana_scraper import AdaDeranaScraper
from scrapers.hirunews_scraper import HiruNewsScraper
from scrapers.itn_scraper import ITNScraper
from scrapers.newsfirst_scraper import NewsFirstScraper
from scrapers.lankatruth_scraper import LankaTruthScraper
from scrapers.lankadeepa_scraper import LankadeepaScraper
from scrapers.silumina_scraper import SiluminaScraper
from scrapers.bbc_sinhala_scraper import BBCSinhalaScraper
from scrapers.divaina_scraper import DivainaScraper
from scrapers.ada_lk_scraper import AdaLkScraper

__all__ = [
    'AdaDeranaScraper',
    'HiruNewsScraper',
    'ITNScraper',
    'NewsFirstScraper',
    'LankaTruthScraper',
    'LankadeepaScraper',
    'SiluminaScraper',
    'BBCSinhalaScraper',
    'DivainaScraper',
    'AdaLkScraper',
]
