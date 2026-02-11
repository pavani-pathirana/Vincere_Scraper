# Vincere - Sinhala News Scraping Framework

A production-grade, ML-ready news scraper for building high-quality Sinhala text corpora.

## Project Structure

```
Vincere_Scraper/
├── config/              # Configuration files
├── core/                # Base scraper classes and session management
├── scrapers/            # Site-specific scraper implementations
├── storage/             # State persistence and file writing
│   ├── schema.sql       # SQLite database schema
│   └── state_manager.py # CheckpointManager implementation
├── processors/          # Text cleaning and Sinhala preprocessing
├── utils/               # Utility functions
└── __init__.py
```

## Phase 1 Complete ✓

### Implemented Components

#### 1. **StateManager (CheckpointManager)**

Location: `storage/state_manager.py`

A comprehensive SQLite-based state persistence system providing:

**Idempotency:**

- Tracks all scraped URLs to prevent duplicates
- Returns skip status if URL already successfully scraped
- Supports retry logic for failed URLs with configurable max retries

**Resumability:**

- Stores pagination state (website, category, last_page_index)
- Can resume from exact point after interruption
- Tracks completion status per category

**Session Tracking:**

- Creates audit trail with unique session IDs
- Tracks statistics (articles scraped/failed/skipped)
- Supports multiple concurrent or sequential sessions

#### 2. **Database Schema**

Location: `storage/schema.sql`

**Tables:**

```sql
scraped_urls          # Idempotency tracking
├── url (UNIQUE)      # Prevents duplicate scraping
├── website, category # Categorization
├── article_id        # Generated hash-based ID
├── status            # success, failed, skipped
├── retry_count       # For retry logic
└── content_checksum  # Change detection

pagination_state      # Resumability
├── website, category (UNIQUE)
├── last_page_index   # Resume from this page
├── total_pages       # If known
└── is_complete       # Fully scraped flag

scrape_sessions       # Audit trail
├── session_id (UUID)
├── website, category
├── started_at, completed_at
├── status            # running, completed, failed, interrupted
└── articles_scraped/failed/skipped counts
```

**Indexes:**

- Fast URL lookups (O(log n) vs O(n))
- Efficient website-category queries
- Status-based filtering for retry logic

### Key Features Implemented

✓ **Idempotent URL Tracking**

```python
manager = StateManager("vincere_state.db")

# Check before scraping
is_scraped, reason = manager.is_url_scraped(url)
if is_scraped:
    print(f"Skipping: {reason}")
else:
    # Scrape article...
    manager.mark_url_scraped(url, website, category, article_id, status='success')
```

✓ **Pagination State Persistence**

```python
# Save state after each page
manager.update_pagination_state("adaderana", "politics", last_page_index=5)

# Resume later
state = manager.get_pagination_state("adaderana", "politics")
start_page = state['last_page_index'] + 1 if state else 1
```

✓ **Session Management**

```python
# Create session
session_id = manager.create_session(website="adaderana", category="politics")

# Update stats during scraping
manager.update_session_stats(session_id, articles_scraped=1)

# Mark session complete
manager.update_session_stats(session_id, status='completed')
```

✓ **Retry Logic**

```python
# Get failed URLs that can be retried
failed = manager.get_failed_urls(website="adaderana", max_retries=3)
for item in failed:
    print(f"Retry: {item['url']} (attempt {item['retry_count'] + 1})")
```

✓ **Statistics**

```python
# Get scraping statistics
stats = manager.get_scraped_count(website="adaderana", category="politics")
print(f"Success: {stats['success']}, Failed: {stats['failed']}, Total: {stats['total']}")
```

## Testing Phase 1

### Quick Test

Run the built-in test:

```powershell
cd "e:\DEGREE 1ST YEAR\RESEARCH\Bulk Scraper\Vincere_Scraper"
python storage/state_manager.py
```

Expected output:

```
Created session: <uuid>
URL scraped: False, Reason: None
Marked URL as scraped with ID: <hash>
URL scraped now: True, Reason: already_scraped
Pagination state: {'last_page_index': 5, ...}
Session info: {'articles_scraped': 1, ...}

✓ StateManager test completed successfully!
```

### Manual Testing

```python
from storage.state_manager import StateManager

# Initialize
manager = StateManager("test_vincere.db")

# Test idempotency
url = "https://sinhala.adaderana.lk/news/123456"
article_id = StateManager.generate_article_id(url)

# First scrape
is_scraped, _ = manager.is_url_scraped(url)
assert not is_scraped, "New URL should not be scraped"

manager.mark_url_scraped(url, "adaderana", "politics", article_id, status='success')

# Second attempt
is_scraped, reason = manager.is_url_scraped(url)
assert is_scraped, "URL should be marked as scraped"
assert reason == 'already_scraped', "Reason should be 'already_scraped'"

print("✓ Idempotency test passed!")

# Test pagination
manager.update_pagination_state("adaderana", "politics", 10)
state = manager.get_pagination_state("adaderana", "politics")
assert state['last_page_index'] == 10, "Page index should be 10"

# Update again
manager.update_pagination_state("adaderana", "politics", 15)
state = manager.get_pagination_state("adaderana", "politics")
assert state['last_page_index'] == 15, "Page index should update to 15"

print("✓ Pagination state test passed!")

# Test retry logic
retry_url = "https://example.com/fail"
manager.mark_url_scraped(retry_url, "adaderana", "politics", "test123", status='failed', error_message="Timeout")

# Should allow retry
is_scraped, _ = manager.is_url_scraped(retry_url, max_retries=3)
assert not is_scraped, "Failed URL with retries available should be retryable"

# Mark failed 3 times
for i in range(3):
    manager.mark_url_scraped(retry_url, "adaderana", "politics", "test123", status='failed')

# Should not retry anymore
is_scraped, reason = manager.is_url_scraped(retry_url, max_retries=3)
assert is_scraped, "Failed URL exceeding max retries should be skipped"
assert reason == 'max_retries_exceeded'

print("✓ Retry logic test passed!")

print("\n✓ All StateManager tests passed!")
```

### Database Inspection

View the database contents:

```powershell
# Install SQLite browser or use command line
sqlite3 vincere_state.db

# View scraped URLs
.headers on
.mode column
SELECT * FROM scraped_urls;

# View pagination state
SELECT * FROM pagination_state;

# View sessions
SELECT * FROM scrape_sessions;

.quit
```

## Design Decisions

### Why SQLite?

- **Single-file database**: Easy deployment, no server needed
- **ACID compliance**: Safe for crash recovery
- **Performance**: Fast for single-threaded scraping (100K+ articles)
- **SQL queries**: Easy analytics and debugging
- **Python stdlib**: No external dependencies

### Why Individual JSON Files?

Per specification: `./vincere_corpus/[website]/[category]/[article_id].json`

- **Incremental processing**: Process files as they arrive
- **Fault tolerance**: Partial failures don't corrupt entire dataset
- **Distributed storage**: Easy to shard across drives
- **ML pipeline friendly**: Many ML tools expect one-sample-per-file

### Article ID Generation

Using MD5 hash (first 8 chars) of URL:

- **Unique**: Collision probability negligible for 100K articles
- **Deterministic**: Same URL → same ID (useful for deduplication)
- **Filesystem safe**: Only hex characters [0-9a-f]
- **Compact**: 8 chars vs full URL in filename

## Next Steps (Phase 2)

1. **SessionManager** (`core/session_manager.py`)
   - HTTP session with connection pooling
   - Rate limiting (token bucket algorithm)
   - User-agent rotation
   - Retry logic with exponential backoff

2. **BaseScraper** (`core/base_scraper.py`)
   - Abstract base class defining scraper interface
   - Strategy pattern foundation

3. **Text Processors** (`processors/`)
   - Sinhala normalizer (Unicode NFC)
   - Text cleaner (HTML stripping, whitespace)

4. **FileWriter** (`storage/file_writer.py`)
   - Atomic JSON writes
   - Directory structure creation
   - Schema validation

5. **Configuration** (`config/settings.py`, `config/site_configs.py`)
   - Global settings
   - Site-specific CSS selectors

Let me know when you're ready to proceed with Phase 2!

## Troubleshooting

### Database Locked Error

If you see "database is locked":

- Only run one scraper instance at a time (SQLite limitation)
- Or use WAL mode: `PRAGMA journal_mode=WAL;`

### File Not Found: schema.sql

The StateManager has fallback logic to create tables inline if schema.sql is missing. Ensure schema.sql is in the same directory as state_manager.py.

### Unicode Errors

Ensure all file operations use UTF-8:

```python
with open(file, 'r', encoding='utf-8') as f:
    content = f.read()
```

## License

Research project - All rights reserved.
