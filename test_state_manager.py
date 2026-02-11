"""
Test script to verify StateManager functionality.

This script demonstrates the key features of the StateManager:
1. Idempotency (URL deduplication)
2. Pagination state persistence
3. Session tracking
4. Retry logic
"""

import os
from pathlib import Path
from storage.state_manager import StateManager

# Clean up old test database before running tests
TEST_DB = "test_vincere.db"
if os.path.exists(TEST_DB):
    os.remove(TEST_DB)
    print(f"✓ Cleaned up old test database: {TEST_DB}\n")

def test_idempotency():
    """Test that URLs are not scraped twice."""
    print("\n=== Testing Idempotency ===")
    manager = StateManager("test_vincere.db")
    
    url = "https://sinhala.adaderana.lk/news/123456"
    article_id = StateManager.generate_article_id(url)
    
    # First check - should not be scraped
    is_scraped, reason = manager.is_url_scraped(url)
    print(f"✓ New URL check: is_scraped={is_scraped}, reason={reason}")
    assert not is_scraped, "New URL should not be marked as scraped"
    
    # Mark as scraped
    manager.mark_url_scraped(url, "adaderana", "politics", article_id, status='success')
    print(f"✓ Marked URL as scraped with article_id: {article_id}")
    
    # Second check - should be scraped
    is_scraped, reason = manager.is_url_scraped(url)
    print(f"✓ Second check: is_scraped={is_scraped}, reason={reason}")
    assert is_scraped and reason == 'already_scraped', "URL should be marked as already scraped"
    
    print("✓ Idempotency test PASSED!")


def test_pagination():
    """Test pagination state save and resume."""
    print("\n=== Testing Pagination State ===")
    manager = StateManager("test_vincere.db")
    
    # Initial state - should be None
    state = manager.get_pagination_state("hirunews", "sports")
    print(f"✓ Initial state: {state}")
    assert state is None, "New category should have no state"
    
    # Save state after scraping page 5
    manager.update_pagination_state("hirunews", "sports", last_page_index=5)
    print(f"✓ Saved state: page 5")
    
    # Resume - should get page 5
    state = manager.get_pagination_state("hirunews", "sports")
    print(f"✓ Retrieved state: {state}")
    assert state['last_page_index'] == 5, "Should retrieve saved page index"
    
    # Update to page 10
    manager.update_pagination_state("hirunews", "sports", last_page_index=10, total_pages=50)
    state = manager.get_pagination_state("hirunews", "sports")
    print(f"✓ Updated state: page 10 of 50")
    assert state['last_page_index'] == 10 and state['total_pages'] == 50
    
    # Mark as complete
    manager.update_pagination_state("hirunews", "sports", last_page_index=50, 
                                   total_pages=50, is_complete=True)
    state = manager.get_pagination_state("hirunews", "sports")
    print(f"✓ Marked complete: {state['is_complete']}")
    assert state['is_complete'] == 1, "Should be marked as complete"
    
    print("✓ Pagination state test PASSED!")


def test_retry_logic():
    """Test retry logic for failed URLs."""
    print("\n=== Testing Retry Logic ===")
    manager = StateManager("test_vincere.db")
    
    url = "https://example.com/timeout"
    article_id = StateManager.generate_article_id(url)
    
    # Mark as failed
    manager.mark_url_scraped(url, "adaderana", "politics", article_id, 
                            status='failed', error_message="Connection timeout")
    print(f"✓ Marked URL as failed (attempt 1)")
    
    # Should allow retry (retry_count=1, max=3)
    is_scraped, reason = manager.is_url_scraped(url, max_retries=3)
    print(f"✓ Retry check 1: is_scraped={is_scraped}, reason={reason}")
    assert not is_scraped, "Failed URL should be retryable"
    
    # Fail again
    manager.mark_url_scraped(url, "adaderana", "politics", article_id, 
                            status='failed', error_message="Connection timeout")
    print(f"✓ Marked URL as failed (attempt 2)")
    
    # Still retryable
    is_scraped, reason = manager.is_url_scraped(url, max_retries=3)
    assert not is_scraped, "Failed URL should still be retryable"
    
    # Fail third time
    manager.mark_url_scraped(url, "adaderana", "politics", article_id, 
                            status='failed', error_message="Connection timeout")
    print(f"✓ Marked URL as failed (attempt 3)")
    
    # Still retryable (retry_count=2, max=3)
    is_scraped, reason = manager.is_url_scraped(url, max_retries=3)
    assert not is_scraped, "Should still be retryable after 3 attempts"
    
    # Fail fourth time (this is the 3rd retry, so retry_count becomes 3)
    manager.mark_url_scraped(url, "adaderana", "politics", article_id, 
                            status='failed', error_message="Connection timeout")
    print(f"✓ Marked URL as failed (attempt 4 - 3rd retry)")
    
    # Should NOT retry anymore (retry_count=3, max=3)
    is_scraped, reason = manager.is_url_scraped(url, max_retries=3)
    print(f"✓ Retry check 2: is_scraped={is_scraped}, reason={reason}")
    assert is_scraped and reason == 'max_retries_exceeded', "Should exceed max retries after 3 retries"
    
    # Get failed URLs
    failed = manager.get_failed_urls(max_retries=3)
    print(f"✓ Found {len(failed)} failed URLs with retries available")
    
    print("✓ Retry logic test PASSED!")


def test_session_tracking():
    """Test session creation and statistics tracking."""
    print("\n=== Testing Session Tracking ===")
    manager = StateManager("test_vincere.db")
    
    # Create session
    session_id = manager.create_session(website="newsfirst", category="local")
    print(f"✓ Created session: {session_id}")
    
    # Get initial info
    info = manager.get_session_info(session_id)
    print(f"✓ Initial stats: scraped={info['articles_scraped']}, failed={info['articles_failed']}")
    assert info['articles_scraped'] == 0, "Should start at 0"
    
    # Update stats
    manager.update_session_stats(session_id, articles_scraped=5)
    manager.update_session_stats(session_id, articles_failed=2)
    manager.update_session_stats(session_id, articles_skipped=3)
    print(f"✓ Updated stats: +5 scraped, +2 failed, +3 skipped")
    
    # Verify
    info = manager.get_session_info(session_id)
    print(f"✓ Current stats: scraped={info['articles_scraped']}, "
          f"failed={info['articles_failed']}, skipped={info['articles_skipped']}")
    assert info['articles_scraped'] == 5 and info['articles_failed'] == 2
    
    # Complete session
    manager.update_session_stats(session_id, status='completed')
    info = manager.get_session_info(session_id)
    print(f"✓ Session status: {info['status']}, completed_at: {info['completed_at']}")
    assert info['status'] == 'completed', "Should be marked as completed"
    
    # Get recent sessions
    recent = manager.get_recent_sessions(limit=5)
    print(f"✓ Found {len(recent)} recent sessions")
    assert len(recent) > 0, "Should have at least one session"
    
    print("✓ Session tracking test PASSED!")


def test_statistics():
    """Test scraping statistics aggregation."""
    print("\n=== Testing Statistics ===")
    manager = StateManager("test_vincere.db")
    
    # Get overall stats
    stats = manager.get_scraped_count()
    print(f"✓ Overall stats: {stats}")
    
    # Get stats for specific website
    stats = manager.get_scraped_count(website="adaderana")
    print(f"✓ Adaderana stats: {stats}")
    
    # Get stats for website+category
    stats = manager.get_scraped_count(website="adaderana", category="politics")
    print(f"✓ Adaderana politics stats: {stats}")
    
    print("✓ Statistics test PASSED!")


def main():
    """Run all tests."""
    print("=" * 70)
    print("  Vincere StateManager - Comprehensive Test Suite")
    print("=" * 70)
    
    try:
        test_idempotency()
        test_pagination()
        test_retry_logic()
        test_session_tracking()
        test_statistics()
        
        print("\n" + "=" * 70)
        print("  ✓ ALL TESTS PASSED!")
        print("=" * 70)
        print("\nStateManager is ready for production use.")
        print("Database: test_vincere.db")
        print("\nNext steps:")
        print("  1. Implement SessionManager (HTTP client, rate limiting)")
        print("  2. Create BaseScraper abstract class")
        print("  3. Build text processors for Sinhala normalization")
        print("  4. Implement FileWriter for JSON storage")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        raise


if __name__ == "__main__":
    main()
