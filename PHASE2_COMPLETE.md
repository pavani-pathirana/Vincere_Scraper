# Phase 2 Implementation Complete ✓

## Overview

Phase 2: Core Engine & Text Processing - February 10, 2026

All 4 components implemented and tested successfully.

---

## Components Implemented

### 1. SessionManager (`core/session_manager.py`) ✓

**HTTP Client with Robustness Features**

**Classes:**

- `SessionManager` - Main HTTP client (600+ lines)
- `UserAgentRotator` - Rotates 15+ realistic browser UAs
- `RateLimiter` - Token bucket rate limiting per domain

**Features:**

- ✓ Connection pooling via `requests.Session`
- ✓ Token bucket rate limiting (default: 20 req/min, configurable per domain)
- ✓ User-Agent rotation (15 browser profiles: Chrome, Firefox, Safari, Edge)
- ✓ Exponential backoff retry with `tenacity` library
- ✓ Automatic retry on transient errors (timeouts, 5xx, 429)
- ✓ Configurable timeouts (connect: 10s, read: 30s)
- ✓ Request/response logging
- ✓ Session statistics tracking

**Usage Example:**

```python
from core import SessionManager

with SessionManager(requests_per_minute=30) as session:
    # Custom rate limit for specific domain
    session.set_rate_limit('adaderana.lk', requests_per_minute=20)

    # Make request (auto rate-limited, retried, with rotated UA)
    response = session.get('https://sinhala.adaderana.lk/news/123456')

    # Get stats
    stats = session.get_stats()
    print(f"Requests: {stats['requests_made']}, Failed: {stats['requests_failed']}")
```

**Retry Logic:**

- Transient errors: 3 retries with exponential backoff (2s, 4s, 8s + jitter)
- HTTP 429 (Rate Limited): Auto-retry with backoff
- HTTP 5xx (Server Error): Auto-retry
- HTTP 403 (Forbidden): No retry (likely blocking)

---

### 2. Sinhala Text Processors (`processors/sinhala_normalizer.py`) ✓

**ML-Ready Text Processing for Sinhala**

**Classes:**

- `SinhalaNormalizer` - Unicode NFC normalization
- `TextCleaner` - HTML stripping & whitespace normalization
- `TextProcessor` - Combined pipeline

**Features:**

**SinhalaNormalizer:**

- ✓ Unicode NFC normalization (canonical composition)
- ✓ Preserves ZWJ (U+200D) and ZWNJ (U+200C) for correct Sinhala rendering
- ✓ Removes invisible chars (ZWSP, BOM, etc.)
- ✓ Whitespace normalization (collapse multiple spaces/newlines)
- ✓ Sinhala detection & ratio calculation
- ✓ Mojibake fixing with `ftfy` library

**Why NFC Normalization is Critical:**
Sinhala uses combining characters (vowel signs, repaya, rakaransaya). Different websites may use NFD (decomposed) or NFC (composed) forms. ML models need consistency:

- NFD: Base char + combining mark (2 codepoints)
- NFC: Single composed char (1 codepoint)
- **Solution:** Always normalize to NFC

**TextCleaner:**

- ✓ HTML tag removal (preserves <p> structure as paragraphs)
- ✓ <script> and <style> removal
- ✓ HTML entity decoding (&nbsp; → space, &#3458; → ඒ)
- ✓ Advertisement text removal
- ✓ Whitespace normalization
- ✓ Paragraph extraction (min length filtering)

**Usage Example:**

```python
from processors import TextProcessor

processor = TextProcessor(
    preserve_zwj=True,      # Keep ZWJ for correct rendering
    remove_ads=True,        # Remove ad text
    fix_mojibake=True       # Fix encoding issues
)

# Process article body
html = "<div><p>පළමු පරිච්ඡේදය</p><p>දෙවන&nbsp;පරිච්ඡේදය</p></div>"
clean_text = processor.process(html)
# Output: "පළමු පරිච්ඡේදය\n\nදෙවන පරිච්ඡේදය"

# Process headline (single line)
headline_html = "<h1>ශ්‍රී   ලංකා   පුවත්</h1>"
headline = processor.process_headline(headline_html)
# Output: "ශ්‍රී ලංකා පුවත්"
```

**Text Quality Features:**

- `has_sinhala(text)` - Detect Sinhala content
- `get_sinhala_ratio(text)` - Calculate Sinhala % (filter low-quality)
- `extract_paragraphs(text)` - Split into paragraphs with min length

---

### 3. FileWriter (`storage/file_writer.py`) ✓

**Atomic JSON File Writer**

**Features:**

- ✓ Atomic writes (temp file → rename) for crash safety
- ✓ Directory structure: `./vincere_corpus/{website}/{category}/{article_id}.json`
- ✓ Schema validation (required fields: headline, body, source, category, date, extraction_timestamp)
- ✓ UTF-8 encoding enforcement
- ✓ Automatic directory creation
- ✓ Path component sanitization (filesystem-safe)
- ✓ Corpus statistics & listing

**JSON Schema:**

```json
{
  "headline": "ශ්‍රී ලංකා පුවත්",
  "body": "පළමු පරිච්ඡේදය...",
  "source": "adaderana",
  "category": "politics",
  "date": "2026-02-10",
  "extraction_timestamp": "2026-02-10T21:30:45.123456",
  "url": "https://...",
  "author": "කතෘ නාමය",
  "word_count": 150,
  "tags": ["politics", "economy"]
}
```

**Usage Example:**

```python
from storage import FileWriter, StateManager

writer = FileWriter(base_dir="./vincere_corpus", validate_schema=True)

# Write article
article_id = StateManager.generate_article_id(url)
file_path = writer.write_article(
    article_data={
        'headline': headline,
        'body': body,
        'source': 'adaderana',
        'category': 'politics',
        'date': '2026-02-10',
        'extraction_timestamp': datetime.now().isoformat()
    },
    website='adaderana',
    category='politics',
    article_id=article_id
)

# Read article
article = writer.read_article('adaderana', 'politics', article_id)

# Check existence
exists = writer.article_exists('adaderana', 'politics', article_id)

# Get stats
stats = writer.get_corpus_stats()
print(f"Total: {stats['total_articles']} articles, {stats['total_size_mb']} MB")
```

**Atomic Write Process:**

1. Write to temp file in same directory
2. Flush and sync to disk (`fsync`)
3. Atomic rename (replaces target file)
4. Result: File never in partial/corrupted state

---

### 4. BaseScraper (`core/base_scraper.py`) ✓

**Abstract Strategy Pattern Interface**

**Data Classes:**

- `ArticleMetadata` - Article info from list page
- `Article` - Complete article with all fields

**BaseScraper Abstract Methods:**

```python
@abstractmethod
def get_category_urls() -> Dict[str, str]
    # Return {'politics': 'https://...', 'sports': 'https://...'}

@abstractmethod
def get_article_list_url(category_url: str, page: int) -> str
    # Build URL for page N of article list

@abstractmethod
def parse_article_list_page(html: str, category: str) -> List[ArticleMetadata]
    # Extract article links/metadata from list page

@abstractmethod
def parse_article_page(html: str, metadata: ArticleMetadata) -> Article
    # Extract full article content

@abstractmethod
def get_next_page_url(current_url: str, html: str, current_page: int) -> Optional[str]
    # Find next page link or return None if last page
```

**Common Functionality (Implemented in Base Class):**

- ✓ `scrape_category()` - Orchestrate category scraping with pagination
- ✓ `scrape_all_categories()` - Scrape entire website
- ✓ `retry_failed_articles()` - Retry previously failed URLs
- ✓ Idempotency checking (skip already-scraped URLs)
- ✓ State persistence (save pagination state after each page)
- ✓ Session management (track statistics)
- ✓ Error handling (mark failures, continue scraping)
- ✓ Logging (progress tracking)

**Usage Example (Concrete Scraper):**

```python
from core import BaseScraper, SessionManager
from storage import StateManager, FileWriter
from processors import TextProcessor
from bs4 import BeautifulSoup

class AdaDeranaScraperclass AdaDeranaScraperclass AdaDeranaScraperclass AdaDeranaScraperclass AdaDeranaScraper(BaseScraper):
    def get_category_urls(self):
        return {
            'politics': 'https://sinhala.adaderana.lk/politics',
            'sports': 'https://sinhala.adaderana.lk/sports'
        }

    def parse_article_list_page(self, html, category):
        soup = BeautifulSoup(html, 'lxml')
        articles = []
        for item in soup.select('.news-item'):
            articles.append(ArticleMetadata(
                url=item.select_one('a')['href'],
                headline=item.select_one('.headline').get_text(),
                category=category,
                date=item.select_one('.date').get_text()
            ))
        return articles

    # ... implement other abstract methods ...

# Use scraper
session_mgr = SessionManager()
state_mgr = StateManager()
file_writer = FileWriter()

scraper = AdaDeranaScraper('adaderana', session_mgr, state_mgr, file_writer)
stats = scraper.scrape_category('politics', 'https://...', max_pages=10, resume=True)
```

**Orchestration Flow:**

```
scrape_category()
  ├─ Load pagination state (resume)
  ├─ Create session
  ├─ For each page:
  │   ├─ Fetch list page
  │   ├─ Parse article metadata
  │   ├─ For each article:
  │   │   ├─ Check idempotency (skip if scraped)
  │   │   ├─ Fetch article page
  │   │   ├─ Parse article content
  │   │   ├─ Process text (clean, normalize)
  │   │   ├─ Write to file
  │   │   └─ Mark as scraped in DB
  │   ├─ Update pagination state
  │   └─ Find next page URL
  └─ Mark session complete
```

---

## Dependencies (requirements.txt) ✓

```
requests>=2.31.0           # HTTP client
beautifulsoup4>=4.12.0     # HTML parsing
lxml>=5.1.0                # Fast parser
tenacity>=8.2.0            # Exponential backoff
ftfy>=6.1.0                # Fix mojibake
python-dateutil>=2.8.2     # Date parsing
```

**Install:**

```bash
pip install -r requirements.txt
```

---

## Testing

### Phase 2 Integration Test (`test_phase2.py`) ✓

**Tests All Components:**

1. SessionManager - Rate limiting, retry logic, UA rotation
2. SinhalaNormalizer - Unicode NFC, whitespace normalization
3. TextCleaner - HTML removal, entity decoding
4. TextProcessor - Full pipeline
5. FileWriter - Atomic writes, schema validation
6. BaseScraper - Data classes, interface
7. Integration - All components working together

**Run Test:**

```bash
python test_phase2.py
```

**Test Results:**

```
✓ SessionManager tests passed
✓ Sinhala text processing tests passed
✓ FileWriter tests passed
✓ BaseScraper interface validated
✓ Integration test completed successfully!

✓ ALL TESTS PASSED!
```

**Test Created:**

- Database: `test_phase2_state.db`
- Corpus: `./test_corpus_phase2/`
- Articles: 2 test articles written

---

## Architecture Summary

### Component Interaction Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                     BaseScraper                              │
│  (Orchestrates scraping with common functionality)          │
└───────┬──────────────────┬──────────────────┬───────────────┘
        │                  │                  │
        ▼                  ▼                  ▼
┌───────────────┐  ┌──────────────┐  ┌──────────────────┐
│SessionManager │  │StateManager  │  │  FileWriter      │
│- Rate limit   │  │- Idempotency │  │- Atomic writes   │
│- Retry logic  │  │- Pagination  │  │- Schema validate │
│- UA rotation  │  │- Sessions    │  │- Directory mgmt  │
└───────────────┘  └──────────────┘  └──────────────────┘
        │                                      │
        ▼                                      ▼
┌───────────────┐                     ┌──────────────────┐
│  HTTP Fetch   │                     │ TextProcessor    │
│  (with retry) │                     │- HTML clean      │
└───────────────┘                     │- Sinhala NFC     │
                                      │- Whitespace      │
                                      └──────────────────┘
```

### Data Flow

```
1. Category URL → SessionManager.get()
2. HTML → parse_article_list_page() → [ArticleMetadata]
3. For each article:
   a. Check StateManager.is_url_scraped() → skip if true
   b. Article URL → SessionManager.get()
   c. HTML → parse_article_page() → Article
   d. Article.body → TextProcessor.process() → Clean text
   e. Article → FileWriter.write_article() → JSON file
   f. URL → StateManager.mark_url_scraped()
4. Page complete → StateManager.update_pagination_state()
```

---

## Key Design Decisions

### 1. **Token Bucket Rate Limiting**

- **Why:** Allows burst requests (better than fixed delay)
- **Implementation:** Per-domain buckets, configurable rates
- **Benefit:** Respectful scraping, avoids 429 errors

### 2. **Unicode NFC Normalization**

- **Why:** Sinhala has combining characters (vowel signs, etc.)
- **Problem:** Websites may use NFD (decomposed) vs NFC (composed)
- **Solution:** Always normalize to NFC for ML consistency
- **Example:** කා (NFD: ක + ා) → කා (NFC: single codepoint)

### 3. **ZWJ/ZWNJ Preservation**

- **Why:** Zero-Width Joiner controls Sinhala ligatures
- **Example:** ක‍්‍ෂ (ksha) requires ZWJ for correct rendering
- **Decision:** Preserve by default (can disable if needed)

### 4. **Atomic File Writes**

- **Why:** Prevent corruption if scraper crashes mid-write
- **Method:** Write to temp file → fsync → rename (atomic on POSIX/Windows)
- **Benefit:** Files always complete or absent, never partial

### 5. **Strategy Pattern for Scrapers**

- **Why:** Each website has unique HTML structure
- **Solution:** Abstract base class + concrete implementations
- **Benefit:** Add new sites without modifying core code (Open/Closed Principle)

### 6. **Exponential Backoff Retry**

- **Why:** Transient errors (network hiccups) often resolve quickly
- **Implementation:** tenacity library, 3 retries (2s, 4s, 8s + jitter)
- **Benefit:** Robust against temporary failures, avoids hammering servers

---

## File Structure After Phase 2

```
Vincere_Scraper/
├── config/
│   └── __init__.py
├── core/
│   ├── __init__.py            ✓ Updated
│   ├── session_manager.py     ✓ NEW (600+ lines)
│   └── base_scraper.py        ✓ NEW (500+ lines)
├── processors/
│   ├── __init__.py            ✓ Updated
│   └── sinhala_normalizer.py ✓ NEW (500+ lines)
├── scrapers/
│   └── __init__.py
├── storage/
│   ├── __init__.py            ✓ Updated
│   ├── schema.sql             ✓ Phase 1
│   ├── state_manager.py       ✓ Phase 1
│   └── file_writer.py         ✓ NEW (400+ lines)
├── utils/
│   └── __init__.py
├── __init__.py
├── requirements.txt           ✓ NEW
├── test_phase2.py             ✓ NEW
├── test_state_manager.py      ✓ Phase 1
├── README.md                  ✓ Phase 1
├── PHASE1_COMPLETE.md         ✓ Phase 1
└── PHASE2_COMPLETE.md         ✓ NEW (this file)
```

**Lines of Code:**

- Phase 2 Total: ~2000+ lines
- SessionManager: 600+ lines
- BaseScraper: 500+ lines
- SinhalaNormalizer: 500+ lines
- FileWriter: 400+ lines

---

## Performance Characteristics

### SessionManager

- **Rate Limiting:** 20 req/min default (configurable per domain)
- **Connection Pooling:** 10 connections, 20 max size
- **Retry:** 3 attempts max, exponential backoff (2-8s)
- **Timeout:** 10s connect, 30s read

### Text Processing

- **HTML Cleaning:** O(n) where n = HTML size
- **Unicode Normalization:** O(n) where n = text length
- **Regex Operations:** Optimized with pre-compiled patterns

### File Writing

- **Atomic Write:** O(n) where n = article size
- **Directory Creation:** O(1) (cached by OS after first create)
- **JSON Serialization:** O(n) with pretty-print (indent=2)

### Expected Throughput

- **Single-threaded:** ~20-60 articles/minute (depends on rate limit & article size)
- **100K articles:** ~30-80 hours (1-3 days) at 20-60 articles/min
- **Storage:** ~500KB/article average → 50GB for 100K articles

---

## Next Steps: Phase 3

### Implement Concrete Scrapers

**Priority Scrapers (as specified):**

1. **Ada Derana** (adaderana.lk/sinhala)
2. **ITN Sri Lanka** (itn.lk/sinhala)
3. **Hiru News** (hirunews.lk)
4. **News First** (newsfirst.lk/sinhala)
5. **Lanka Truth** (lankatruth.com/sinhala)

**For Each Scraper:**

1. Inspect website HTML structure
2. Identify CSS selectors for:
   - Navigation/categories
   - Article list items
   - Article headline, body, date, author
   - Pagination (next page link)
3. Implement 5 abstract methods
4. Test with `max_pages=2` first
5. Add site-specific configurations

**Template:**

```python
class AdaDeranaScraper(BaseScraper):
    BASE_URL = 'https://sinhala.adaderana.lk'

    def get_category_urls(self):
        # Scrape homepage navigation or return hardcoded
        return {...}

    def get_article_list_url(self, category_url, page):
        # Build paginated URL
        return f"{category_url}?page={page}"

    def parse_article_list_page(self, html, category):
        soup = BeautifulSoup(html, 'lxml')
        # Extract using CSS selectors
        return [ArticleMetadata(...)]

    def parse_article_page(self, html, metadata):
        soup = BeautifulSoup(html, 'lxml')
        # Extract article content
        return Article(...)

    def get_next_page_url(self, current_url, html, current_page):
        soup = BeautifulSoup(html, 'lxml')
        # Find next page link
        next_link = soup.select_one('.pagination .next')
        return next_link['href'] if next_link else None
```

### Main Entry Point (Phase 3)

Create `main.py` for CLI:

```bash
python main.py --website adaderana --category politics --max-pages 10 --resume
python main.py --website all --max-pages 50 --resume
python main.py --retry-failed
```

---

## Phase 2 Status: ✓ COMPLETE

**All deliverables implemented:**

- ✓ SessionManager with rate limiting & exponential backoff
- ✓ SinhalaNormalizer with Unicode NFC & ZWJ preservation
- ✓ TextCleaner with HTML stripping & whitespace normalization
- ✓ FileWriter with atomic writes & schema validation
- ✓ BaseScraper abstract Strategy Pattern interface
- ✓ requirements.txt with all dependencies
- ✓ Comprehensive integration test
- ✓ Documentation

**Test Results:** ✓ ALL TESTS PASSED

**Ready for Phase 3:** Concrete scraper implementations

---

**Implementation Date:** February 10, 2026  
**Total Development Time:** Single session integration  
**Code Quality:** Production-ready with full error handling
