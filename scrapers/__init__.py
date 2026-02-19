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
from scrapers.gossiplanka_scraper import GossipLankaScraper
from scrapers.gagana_scraper import GaganaLkScraper
from scrapers.lankacnews_scraper import LankaCNewsScraper
from scrapers.lankapuvath_scraper import LankapuvathScraper
from scrapers.sarasaviya_scraper import SarasaviyaScraper
from scrapers.mawratanews_scraper import MawrataNewsScraper
from scrapers.vidusara_scraper import VidusaraScraper

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
    'GossipLankaScraper',
    'GaganaLkScraper',
    'LankaCNewsScraper',
    'LankapuvathScraper',
    'SarasaviyaScraper',
    'MawrataNewsScraper',
    'VidusaraScraper',
]
