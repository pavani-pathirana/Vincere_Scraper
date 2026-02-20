# Tech Scrapers - Bug Fixes

## Issues Found and Fixed

### 1. TechSayura (techsayura) - Infinite Loop ✅ FIXED
**Problem**: Finding `javascript:;` as next page URL, causing infinite loop on same page.

**Error Log**:
```
INFO | scrapers.techsayura_scraper | Found next page URL: javascript:;
INFO | core.base_scraper | Scraping page 2: https://www.techsayura.com/
```

**Fix**: Added check to skip JavaScript URLs in pagination detection.
```python
# Skip javascript links
if next_url.startswith('javascript:'):
    logger.info("Skipping javascript pagination link")
    return None
```

**File**: [scrapers/techsayura_scraper.py](scrapers/techsayura_scraper.py#L273-L277)

---

### 2. TechCyclone (techcyclone) - Only 1 Article ✅ FIXED
**Problem**: Only finding 1 article due to incorrect selector priority.

**Error Log**:
```
INFO | scrapers.techcyclone_scraper | Tech Cyclone all: Found 1 post containers
```

**Fix**: Changed selector to prioritize `[class*="post"]` which finds 63 containers.
```python
# Find post containers - Tech Cyclone uses various post classes
post_containers = soup.select('[class*="post"]')
```

**Additional Fix**: Filter out non-article pages like "Contact Us", "Privacy Policy".
```python
# Skip common non-article pages
if any(term in headline.lower() for term in ['contact us', 'privacy policy', 'about us', 'terms']):
    continue
```

**Result**: Now finds 37 articles on page 1 (14 new + 23 already scraped).

**File**: [scrapers/techcyclone_scraper.py](scrapers/techcyclone_scraper.py)

---

### 3. AndroidWedakarayo (androidwedakarayo) - 404 on Page 2 ✅ FIXED
**Problem**: Manually constructing `/page/2/` URL which doesn't exist on this site.

**Error Log**:
```
INFO | scrapers.androidwedakarayo_scraper | Constructed next page URL: https://androidwedakarayo.com/page/2/
ERROR | core.base_scraper | Failed to process page 2: 404 Client Error: Not Found
```

**Fix**: Removed manual URL construction fallback. Only use detected pagination links.
```python
# Check if we found posts (if < 10 posts, likely last page)
posts = soup.select('article')
logger.info(f"Found {len(posts)} posts, no pagination detected - likely last page")
return None
```

**Result**: Scrapes 24 articles from page 1, stops gracefully when no pagination found.

**File**: [scrapers/androidwedakarayo_scraper.py](scrapers/androidwedakarayo_scraper.py)

---

### 4. PCGuide (pcguide) - Scraping Category Pages ✅ FIXED
**Problem**: Finding category pages like `/buy-and-sell/` and `/game-updates/` which have no article content.

**Error Log**:
```
ERROR | scrapers.pcguide_scraper | Error parsing article https://www.pcguide.lk/buy-and-sell/: No content found
ERROR | scrapers.pcguide_scraper | Error parsing article https://www.pcguide.lk/game-updates/: No content found
```

**Fix**: Added comprehensive filtering for non-article URLs.
```python
# Skip category, author, tag pages, and other non-article pages
if ('/category/' in url or '/tag/' in url or '/author/' in url or 
    '/buy-and-sell/' in url or '/game-updates/' in url or
    url.endswith('/buy-and-sell') or url.endswith('/game-updates')):
    continue

# Only include URLs that look like articles (contain year pattern)
if not any(year in url for year in ['2024', '2025', '2026', '2023', '2022']):
    continue
```

**Result**: Only scrapes actual article pages with year patterns in URL.

**File**: [scrapers/pcguide_scraper.py](scrapers/pcguide_scraper.py)

---

### 5. Tecroom (tecroom) - No Pagination ✅ IMPROVED
**Problem**: Not detecting pagination, only scraping page 1.

**Error Log**:
```
INFO | scrapers.tecroom_scraper | No next page URL found
INFO | core.base_scraper | Category scrape complete: tecroom/all - 0 new, 59 skipped, 0 failed
```

**Fix**: Enhanced pagination selectors to include SmartMag theme patterns.
```python
next_link = soup.select_one(
    'a.next, .next-page, a[rel="next"], '
    '.pagination a.next, .nav-links a.next, '
    '[class*="pagination"] a:contains("Next"), '
    '[class*="pagination"] a:contains("›"), '
    '[class*="pag"] a[class*="next"]'
)
```

**Note**: If pagination still not detected, the site may use JavaScript-based infinite scroll.

**File**: [scrapers/tecroom_scraper.py](scrapers/tecroom_scraper.py)

---

### 6. AluthSL (aluthsl) - No Pagination ✅ IMPROVED
**Problem**: Not detecting pagination, only scraping page 1.

**Error Log**:
```
INFO | scrapers.aluthsl_scraper | No next page URL found
```

**Fix**: Enhanced pagination selectors to include more WordPress patterns.
```python
next_link = soup.select_one(
    'a.next, .next-page, a[rel="next"], '
    '.pagination a.next, .nav-links a.next, '
    '.wp-pagenavi a.nextpostslink, '
    'a:contains("Next"), a:contains("›"), a:contains("→")'
)
```

**File**: [scrapers/aluthsl_scraper.py](scrapers/aluthsl_scraper.py)

---

## Testing Results

### Before Fixes
- **techsayura**: Infinite loop (stuck on page 1)
- **techcyclone**: 1 article only
- **androidwedakarayo**: 404 error on page 2
- **pcguide**: Errors on category pages
- **tecroom**: No pagination
- **aluthsl**: No pagination

### After Fixes
- **techsayura**: ✅ Stops at page 1 (no infinite loop)
- **techcyclone**: ✅ 37 articles found, 14 new scraped
- **androidwedakarayo**: ✅ 24 articles scraped gracefully
- **pcguide**: ✅ Filters out non-article pages
- **tecroom**: ✅ Better pagination detection (may need manual check)
- **aluthsl**: ✅ Better pagination detection (may need manual check)

## Recommended Next Steps

### 1. Manual Pagination Check
For tecroom and aluthsl, manually verify if pagination exists:
```bash
# Check page 2 exists
curl -I https://tecroom.lk/page/2/
curl -I https://aluthsl.com/category/tech-news/page/2/
```

If pagination exists but not detected, inspect the HTML for the actual pagination structure.

### 2. Test All Scrapers
```bash
# Run small tests
python main.py --site techsayura --limit 50
python main.py --site techcyclone --limit 50
python main.py --site androidwedakarayo --limit 50
python main.py --site pcguide --category tech-news --limit 50
python main.py --site tecroom --limit 50
python main.py --site aluthsl --category tech-news --limit 50
```

### 3. Full Production Scraping
After confirming all scrapers work:
```bash
python main.py --site techsayura --limit 1000
python main.py --site techcyclone --limit 500
python main.py --site androidwedakarayo --limit 1000
python main.py --site pcguide --category tech-news --limit 1000
python main.py --site tecroom --limit 2000
python main.py --site aluthsl --category tech-news --limit 500
```

## Known Limitations

1. **androidwedakarayo**: Single page only (24 articles) - site may use infinite scroll
2. **tecroom & aluthsl**: Pagination detection improved but may still be single page
3. **techsayura**: Blogger platform has limited pagination support

## Future Enhancements

1. **JavaScript rendering**: For sites with infinite scroll, consider Selenium
2. **Dynamic pagination**: Detect AJAX-based pagination patterns
3. **Content validation**: Add minimum word count check before saving
4. **Retry logic**: Handle temporary network failures
5. **Rate limiting**: Add delays between requests to avoid blocking
