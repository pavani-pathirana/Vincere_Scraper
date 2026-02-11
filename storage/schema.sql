-- Vincere Scraper Database Schema
-- Version: 1.0.0
-- Purpose: State persistence for idempotent, resumable news scraping

-- Track scraped URLs for idempotency and prevent duplicate scraping
CREATE TABLE IF NOT EXISTS scraped_urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL UNIQUE,  -- Unique constraint ensures idempotency
    website TEXT NOT NULL,  -- e.g., 'adaderana', 'hirunews'
    category TEXT,  -- e.g., 'politics', 'sports', 'local-news'
    article_id TEXT,  -- Generated hash-based ID for file naming
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT CHECK(status IN ('success', 'failed', 'skipped')) DEFAULT 'success',
    retry_count INTEGER DEFAULT 0,  -- Number of retry attempts
    error_message TEXT,  -- Store error details for failed scrapes
    content_checksum TEXT  -- MD5 hash of content for change detection
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_url ON scraped_urls(url);
CREATE INDEX IF NOT EXISTS idx_website_category ON scraped_urls(website, category);
CREATE INDEX IF NOT EXISTS idx_status ON scraped_urls(status);
CREATE INDEX IF NOT EXISTS idx_scraped_at ON scraped_urls(scraped_at);

-- Track pagination state for resumability across sessions
CREATE TABLE IF NOT EXISTS pagination_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    website TEXT NOT NULL,
    category TEXT NOT NULL,
    last_page_index INTEGER DEFAULT 1,  -- Last successfully scraped page number
    total_pages INTEGER,  -- Total pages if known
    last_scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_complete BOOLEAN DEFAULT 0,  -- Flag indicating category fully scraped
    UNIQUE(website, category)  -- One state record per website-category pair
);

CREATE INDEX IF NOT EXISTS idx_website_category_state ON pagination_state(website, category);

-- Track scraping sessions for audit trail and analytics
CREATE TABLE IF NOT EXISTS scrape_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,  -- UUID for session identification
    website TEXT,  -- Target website for this session
    category TEXT,  -- Target category (NULL for all categories)
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,  -- NULL if session still running/interrupted
    status TEXT CHECK(status IN ('running', 'completed', 'failed', 'interrupted')) DEFAULT 'running',
    articles_scraped INTEGER DEFAULT 0,  -- Successful scrapes count
    articles_failed INTEGER DEFAULT 0,  -- Failed scrapes count
    articles_skipped INTEGER DEFAULT 0  -- Already-scraped URLs count
);

CREATE INDEX IF NOT EXISTS idx_session_id ON scrape_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_session_status ON scrape_sessions(status);

-- Optional: Rate limiting state to track request windows per domain
CREATE TABLE IF NOT EXISTS rate_limit_state (
    domain TEXT PRIMARY KEY,
    last_request_at TIMESTAMP,
    request_count_current_window INTEGER DEFAULT 0,
    window_start_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Schema version tracking for future migrations
CREATE TABLE IF NOT EXISTS schema_version (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial schema version
INSERT OR IGNORE INTO schema_version (version) VALUES ('1.0.0');
