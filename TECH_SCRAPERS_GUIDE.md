# Tech News Scrapers - Usage Guide

## Overview
Added 6 new scrapers for Sinhala technology news websites to expand the corpus with tech-focused content.

## New Scrapers

### 1. AluthSL (aluthsl)
- **URL**: https://aluthsl.com/
- **Platform**: WordPress
- **Category**: `tech-news`
- **Usage**: 
  ```bash
  python main.py --site aluthsl --category tech-news --limit 500
  ```

### 2. PC Guide LK (pcguide)
- **URL**: https://www.pcguide.lk/
- **Platform**: WordPress
- **Category**: `tech-news`
- **Usage**: 
  ```bash
  python main.py --site pcguide --category tech-news --limit 1000
  ```

### 3. Tecroom (tecroom)
- **URL**: https://tecroom.lk/
- **Platform**: WordPress (SmartMag theme)
- **Category**: `all`
- **Usage**: 
  ```bash
  python main.py --site tecroom --category all --limit 2000
  ```

### 4. Android Wedakarayo (androidwedakarayo)
- **URL**: https://androidwedakarayo.com/
- **Platform**: WordPress (Tailwind CSS)
- **Category**: `all`
- **Usage**: 
  ```bash
  python main.py --site androidwedakarayo --category all --limit 1000
  ```

### 5. The Tech Cyclone (techcyclone)
- **URL**: https://thetechcyclone.com/
- **Platform**: WordPress (Kadence theme)
- **Category**: `all`
- **Usage**: 
  ```bash
  python main.py --site techcyclone --category all --limit 500
  ```

### 6. Tech Sayura (techsayura)
- **URL**: https://www.techsayura.com/
- **Platform**: Blogger/Blogspot
- **Category**: `all`
- **Usage**: 
  ```bash
  python main.py --site techsayura --category all --limit 1000
  ```

## Word Count Feature

All new scrapers automatically calculate and save word counts for each article. This ensures:
- Analytics reports show accurate word count statistics
- No need to run retroactive updates
- Consistent data quality across all new articles

**Word count calculation**: `len(body.split())` - simple whitespace-based word counting

## Testing the Scrapers

### Quick Test (5 articles each)
```bash
# Test all scrapers with small samples
python main.py --site aluthsl --category tech-news --limit 5
python main.py --site pcguide --category tech-news --limit 5
python main.py --site tecroom --category all --limit 5
python main.py --site androidwedakarayo --category all --limit 5
python main.py --site techcyclone --category all --limit 5
python main.py --site techsayura --category all --limit 5
```

### Full Scraping
```bash
# Scrape all tech sites (recommended limits)
python main.py --site aluthsl --category tech-news --limit 500
python main.py --site pcguide --category tech-news --limit 1000
python main.py --site tecroom --limit 2000
python main.py --site androidwedakarayo --limit 1000
python main.py --site techcyclone --limit 500
python main.py --site techsayura --limit 1000
```

**Expected total**: ~6,000 new tech articles

## Viewing Results

### Corpus Statistics
```bash
# View complete corpus statistics including tech news sites
python analyze_corpus.py
```

### Check Specific Site
```bash
# Count articles for a specific site
Get-ChildItem "vincere_corpus\tecroom" -Recurse -File | Measure-Object
```

## Implementation Details

### File Structure
```
scrapers/
├── aluthsl_scraper.py          # AluthSL scraper
├── pcguide_scraper.py          # PC Guide LK scraper
├── tecroom_scraper.py          # Tecroom scraper
├── androidwedakarayo_scraper.py # Android Wedakarayo scraper
├── techcyclone_scraper.py      # The Tech Cyclone scraper
├── techsayura_scraper.py       # Tech Sayura scraper (Blogger)
└── __init__.py                  # Updated with new imports
```

### Registration
- **main.py**: Lines 45-50 (imports), Lines 164-169 (scraper registration)
- **scrapers/__init__.py**: Lines 24-29 (imports), Lines 44-49 (__all__ list)

## Platform Differences

### WordPress Sites (5 sites)
- Standard pagination: `/page/N/`
- Common selectors: `.entry-content`, `h1.entry-title`, `time`
- Similar scraping logic across all WordPress sites

### Blogger Site (techsayura)
- Blogger-specific pagination (continuation tokens)
- URL pattern: `/YYYY/MM/post-slug.html`
- Different selectors: `.blog-post`, `.hentry`, `.post-body`
- Custom date parsing for Blogger format

## Content Gap Analysis

### Current Tech Coverage
- ada/technology: 388 articles (0.5% of corpus)
- vidusara (science): 101 articles (0.1% of corpus)
- **Total current**: ~489 articles (0.6%)

### Expected After Tech Scrapers
- Current corpus: 75,977 articles
- New tech articles: ~6,000 articles
- **New total**: ~82,000 articles
- **Tech coverage**: 4-8% of corpus

## Notes

1. All scrapers include word_count calculation in the Article object
2. Pagination is automatic for all sites except androidwedakarayo (manual fallback included)
3. Rate limiting: 20 requests/minute (configured in SessionManager)
4. Articles are deduplicated automatically by URL hash
5. State is saved in `vincere_state.db` to resume interrupted scraping

## Troubleshooting

### If scraper fails:
1. Check site is accessible: `curl -I <site_url>`
2. Verify selectors haven't changed (sites update their HTML)
3. Check logs in `vincere.log`
4. Reduce limit if rate-limited: `--limit 100`

### Common issues:
- **No articles found**: Site structure changed, update selectors
- **Timeout errors**: Increase timeout in config or reduce rate
- **Encoding errors**: Should be handled by `errors='ignore'` in file operations
- **Duplicate articles**: Normal - deduplication happens automatically

## Future Enhancements

Potential improvements for these scrapers:
1. Add category detection for sites using `all` category
2. Implement retry logic for failed article fetches
3. Add image URL extraction for multimedia content
4. Include publication date validation
5. Add article quality metrics (reading level, etc.)
