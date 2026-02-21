"""
TechNews.LK Scraper

Scraper for TechNews.LK Sinhala technology news website (https://technews.lk/).
"""

import logging
import re
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from core.base_scraper import BaseScraper, ArticleMetadata, Article

logger = logging.getLogger(__name__)


class TechNewsScraper(BaseScraper):
    """
    Scraper for TechNews.LK Sinhala technology news website.
    
    Site structure:
    - Ghost CMS platform
    - Main news page: /news/
    - Techroom page: /techroom/
    - Pagination: /news/page/2/, /news/page/3/, etc.
    - Article URLs: /{slug}/
    - Content in .post-content container
    """
    
    BASE_URL = "https://technews.lk"
    SITE_NAME = "technews"
    
    CATEGORIES = {
        'news': {
            'name': 'Tech News',
            'url': f'{BASE_URL}/news/',
            'slug': 'news'
        },
        'techroom': {
            'name': 'Techroom',
            'url': f'{BASE_URL}/techroom/',
            'slug': 'techroom'
        },
        # Tag-based categories
        'technology': {
            'name': 'Technology',
            'url': f'{BASE_URL}/tag/technology/',
            'slug': 'technology'
        },
        'mobile': {
            'name': 'Mobile',
            'url': f'{BASE_URL}/tag/mobile/',
            'slug': 'mobile'
        },
        'google': {
            'name': 'Google',
            'url': f'{BASE_URL}/tag/google/',
            'slug': 'google'
        },
        'apps': {
            'name': 'Apps',
            'url': f'{BASE_URL}/tag/apps-tag/',
            'slug': 'apps'
        },
        'social-media': {
            'name': 'Social Media',
            'url': f'{BASE_URL}/tag/social-media/',
            'slug': 'social-media'
        },
        'business': {
            'name': 'Business',
            'url': f'{BASE_URL}/tag/business/',
            'slug': 'business'
        },
        'android': {
            'name': 'Android',
            'url': f'{BASE_URL}/tag/android/',
            'slug': 'android'
        },
        'apple': {
            'name': 'Apple',
            'url': f'{BASE_URL}/tag/apple/',
            'slug': 'apple'
        },
        'security': {
            'name': 'Security',
            'url': f'{BASE_URL}/tag/security/',
            'slug': 'security'
        },
        'microsoft': {
            'name': 'Microsoft',
            'url': f'{BASE_URL}/tag/microsoft/',
            'slug': 'microsoft'
        },
        'internet': {
            'name': 'Internet',
            'url': f'{BASE_URL}/tag/internet/',
            'slug': 'internet'
        },
        'softwares': {
            'name': 'Softwares',
            'url': f'{BASE_URL}/tag/softwares/',
            'slug': 'softwares'
        },
        'gaming': {
            'name': 'Gaming',
            'url': f'{BASE_URL}/tag/gaming/',
            'slug': 'gaming'
        },
        'leaks': {
            'name': 'Leaks',
            'url': f'{BASE_URL}/tag/leaks/',
            'slug': 'leaks'
        },
        'ai': {
            'name': 'Artificial Intelligence',
            'url': f'{BASE_URL}/tag/artificial-intelligence/',
            'slug': 'ai'
        },
        'gadgets': {
            'name': 'Gadgets',
            'url': f'{BASE_URL}/tag/gadgets/',
            'slug': 'gadgets'
        },
        'communication': {
            'name': 'Communication',
            'url': f'{BASE_URL}/tag/communication/',
            'slug': 'communication'
        },
        'entertainment': {
            'name': 'Entertainment',
            'url': f'{BASE_URL}/tag/entertainment/',
            'slug': 'entertainment'
        },
        'ios': {
            'name': 'iOS',
            'url': f'{BASE_URL}/tag/ios/',
            'slug': 'ios'
        },
        'events': {
            'name': 'Events',
            'url': f'{BASE_URL}/tag/events/',
            'slug': 'events'
        },
        'tips-tricks': {
            'name': 'Tips & Tricks',
            'url': f'{BASE_URL}/tag/tips-tricks/',
            'slug': 'tips-tricks'
        },
        'covid-19': {
            'name': 'COVID-19',
            'url': f'{BASE_URL}/tag/covid-19/',
            'slug': 'covid-19'
        },
        'youtube': {
            'name': 'YouTube',
            'url': f'{BASE_URL}/tag/youtube/',
            'slug': 'youtube'
        },
        'legal': {
            'name': 'Legal',
            'url': f'{BASE_URL}/tag/legal/',
            'slug': 'legal'
        },
        'computing': {
            'name': 'Computing',
            'url': f'{BASE_URL}/tag/computing/',
            'slug': 'computing'
        },
        'oneplus': {
            'name': 'OnePlus',
            'url': f'{BASE_URL}/tag/oneplus/',
            'slug': 'oneplus'
        },
        'windows': {
            'name': 'Windows',
            'url': f'{BASE_URL}/tag/windows/',
            'slug': 'windows'
        },
        'education': {
            'name': 'Education',
            'url': f'{BASE_URL}/tag/education/',
            'slug': 'education'
        },
        'science': {
            'name': 'Science',
            'url': f'{BASE_URL}/tag/science/',
            'slug': 'science'
        },
        'open-source': {
            'name': 'Open Source',
            'url': f'{BASE_URL}/tag/open-source/',
            'slug': 'open-source'
        },
        'reviews': {
            'name': 'Reviews',
            'url': f'{BASE_URL}/tag/reviews/',
            'slug': 'reviews'
        },
        'samsung': {
            'name': 'Samsung',
            'url': f'{BASE_URL}/tag/samsung/',
            'slug': 'samsung'
        },
        'automotive': {
            'name': 'Automotive',
            'url': f'{BASE_URL}/tag/automotive/',
            'slug': 'automotive'
        },
        'cryptocurrency': {
            'name': 'Cryptocurrency',
            'url': f'{BASE_URL}/tag/cryptocurrency/',
            'slug': 'cryptocurrency'
        },
        'space': {
            'name': 'Space',
            'url': f'{BASE_URL}/tag/space/',
            'slug': 'space'
        },
        'huawei': {
            'name': 'Huawei',
            'url': f'{BASE_URL}/tag/huawei/',
            'slug': 'huawei'
        },
        'hall-of-fame': {
            'name': 'Hall of Fame',
            'url': f'{BASE_URL}/tag/hall-of-fame/',
            'slug': 'hall-of-fame'
        },
        'economy': {
            'name': 'Economy',
            'url': f'{BASE_URL}/tag/economy/',
            'slug': 'economy'
        },
        'health': {
            'name': 'Health',
            'url': f'{BASE_URL}/tag/health/',
            'slug': 'health'
        },
        'bitcoin': {
            'name': 'Bitcoin',
            'url': f'{BASE_URL}/tag/bitcoin/',
            'slug': 'bitcoin'
        },
        'tutorials': {
            'name': 'Tutorials',
            'url': f'{BASE_URL}/tag/tutorials/',
            'slug': 'tutorials'
        },
        'sports': {
            'name': 'Sports',
            'url': f'{BASE_URL}/tag/sports/',
            'slug': 'sports'
        },
        'blockchain': {
            'name': 'Blockchain',
            'url': f'{BASE_URL}/tag/blockchain/',
            'slug': 'blockchain'
        }
    }
    
    def get_category_urls(self) -> Dict[str, str]:
        """Get mapping of category names to their URLs."""
        category_urls = {}
        for category_key, category_info in self.CATEGORIES.items():
            category_urls[category_key] = category_info['url']
        
        logger.info(f"TechNews: Found {len(category_urls)} categories")
        return category_urls
    
    def get_article_list_url(self, category_url: str, page_number: int) -> str:
        """Construct URL for a specific page of article list."""
        if page_number == 1:
            return category_url
        else:
            # Ghost CMS pagination format
            return f"{category_url}page/{page_number}/"
    
    def parse_article_list_page(self, html: str, category: str) -> List[ArticleMetadata]:
        """Parse article list page and extract article metadata."""
        soup = BeautifulSoup(html, 'lxml')
        articles = []
        
        # Find all article containers (catches post-card, post-card-large, etc.)
        article_containers = soup.select('article[class*="post-card"]')
        
        logger.info(f"TechNews {category}: Found {len(article_containers)} article containers")
        
        for container in article_containers:
            try:
                # Get article link from .post-card-content-link
                link = container.select_one('.post-card-content-link, a[href]')
                if not link or not link.get('href'):
                    continue
                
                url = link.get('href')
                
                # Make absolute URL
                if not url.startswith('http'):
                    url = urljoin(self.BASE_URL, url)
                
                # Skip non-article URLs (category pages, pagination, etc.)
                if '/page/' in url or url.endswith('/news/') or url.endswith('/techroom/'):
                    continue
                
                # Get title from link aria-label or text
                title = link.get('aria-label') or link.get_text(strip=True)
                
                # Try to find title in header if not found
                if not title:
                    title_elem = container.select_one('h2, h3, .post-card-title')
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                
                if not title:
                    continue
                
                article = ArticleMetadata(
                    url=url,
                    headline=title,
                    category=category
                )
                articles.append(article)
                
            except Exception as e:
                logger.warning(f"Error parsing article container: {e}")
                continue
        
        logger.info(f"TechNews {category}: Extracted {len(articles)} articles from list page")
        return articles
    
    def parse_article_page(self, html: str, metadata: ArticleMetadata) -> Article:
        """Parse individual article page and extract content."""
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Extract headline
            headline = metadata.headline
            headline_elem = soup.select_one('h1, .post-title, .article-title')
            if headline_elem:
                headline = headline_elem.get_text(strip=True)
            
            # Extract content from .post-content or .post-full-content
            content_elem = soup.select_one('.post-content, .post-full-content, .gh-content')
            
            if not content_elem:
                raise ValueError(f"No content found for {metadata.url}")
            
            # Extract paragraphs
            paragraphs = content_elem.select('p')
            
            body_paragraphs = []
            for para in paragraphs:
                text = para.get_text(strip=True)
                # Skip short lines, ads, metadata
                if len(text) > 30:
                    body_paragraphs.append(text)
            
            if not body_paragraphs:
                # Fallback to all text
                text = content_elem.get_text(strip=True)
                if len(text) > 50:
                    body_paragraphs = [text]
            
            if not body_paragraphs:
                logger.warning(f"Minimal content for {metadata.url}")
                body_paragraphs = [headline]
            
            body = '\n\n'.join(body_paragraphs)
            
            # Calculate word count
            word_count = len(body.split())
            
            # Extract date from time element
            date_str = datetime.now().strftime('%Y-%m-%d')
            time_elem = soup.select_one('time')
            if time_elem:
                datetime_attr = time_elem.get('datetime')
                if datetime_attr:
                    try:
                        # Parse ISO format datetime (e.g., "2025-12-12")
                        parsed_date = datetime.fromisoformat(datetime_attr.split('T')[0])
                        date_str = parsed_date.strftime('%Y-%m-%d')
                    except Exception as e:
                        logger.debug(f"Date parsing error: {e}")
                        # Try parsing the text content
                        date_text = time_elem.get_text(strip=True)
                        # Format: "12 දෙසැම්බර් 2025"
                        date_match = re.search(r'(\d{1,2})\s+\S+\s+(\d{4})', date_text)
                        if date_match:
                            day, year = date_match.groups()
                            # For now, use the year-month from datetime attr if available
                            if datetime_attr:
                                try:
                                    date_str = datetime_attr.split('T')[0]
                                except:
                                    pass
            
            # Extract author
            author = None
            author_elem = soup.select_one('.author-name, [rel="author"], .post-author')
            if author_elem:
                author = author_elem.get_text(strip=True)
            
            # Generate tags from categories
            tags = [metadata.category]
            tag_elems = soup.select('.tag, .post-tag')
            for tag_elem in tag_elems[:5]:
                tag_text = tag_elem.get_text(strip=True)
                if tag_text and tag_text not in tags:
                    tags.append(tag_text)
            
            return Article(
                url=metadata.url,
                headline=headline,
                body=body,
                date=date_str,
                source=self.website_name,
                category=metadata.category,
                author=author,
                tags=tags,
                word_count=word_count,
                extraction_timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error parsing article {metadata.url}: {e}")
            raise
    
    def get_next_page_url(self, current_url: str, html: str, current_page: int) -> Optional[str]:
        """Extract URL for next page of articles."""
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Check for pagination navigation first
            pagination = soup.select_one('.pagination, nav[aria-label="pagination"]')
            if not pagination:
                return None
            
            # Look for "Next" link manually (BeautifulSoup doesn't support :-soup-contains)
            next_link = None
            for link in soup.select('a[href*="/page/"]'):
                text = link.get_text(strip=True)
                if 'Next' in text or '→' in text or 'ඊළඟ' in text:
                    next_link = link
                    break
            
            if next_link and next_link.get('href'):
                next_url = next_link.get('href')
                if not next_url.startswith('http'):
                    next_url = urljoin(self.BASE_URL, next_url)
                logger.info(f"Found next page URL: {next_url}")
                return next_url
            
            # Check if pagination has any next page button
            next_btn = pagination.select_one('a[href*="/page/"]')
            if next_btn and next_btn.get('href'):
                next_url = next_btn.get('href')
                if not next_url.startswith('http'):
                    next_url = urljoin(self.BASE_URL, next_url)
                logger.info(f"Found next page URL: {next_url}")
                return next_url
            
            logger.info("No next page URL found")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting next page URL: {e}")
            return None
