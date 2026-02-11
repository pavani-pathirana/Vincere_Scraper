"""
SessionManager - HTTP session management with rate limiting and robustness features.

Handles HTTP requests with connection pooling, user-agent rotation, rate limiting,
and automatic retry logic for the Vincere scraper.
"""

import time
import random
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    after_log
)


# Configure logging
logger = logging.getLogger(__name__)


class UserAgentRotator:
    """
    Rotates User-Agent strings to mimic different browsers.
    
    Helps avoid being blocked by appearing as different legitimate browsers.
    """
    
    # Realistic, modern browser User-Agents
    USER_AGENTS = [
        # Chrome on Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        
        # Chrome on macOS
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        
        # Firefox on Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
        
        # Firefox on macOS
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
        
        # Safari on macOS
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        
        # Edge on Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
        
        # Chrome on Linux
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        
        # Firefox on Linux
        'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
    ]
    
    def __init__(self):
        """Initialize the rotator with shuffled user agents."""
        self.user_agents = self.USER_AGENTS.copy()
        random.shuffle(self.user_agents)
        self.current_index = 0
    
    def get_random(self) -> str:
        """Get a random User-Agent string."""
        return random.choice(self.user_agents)
    
    def get_next(self) -> str:
        """Get the next User-Agent in rotation (round-robin)."""
        ua = self.user_agents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.user_agents)
        return ua


class RateLimiter:
    """
    Token bucket rate limiter for per-domain request throttling.
    
    Ensures respectful scraping by limiting requests per minute per domain.
    """
    
    def __init__(self, requests_per_minute: int = 20, burst_size: int = 5):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests allowed per minute
            burst_size: Maximum burst capacity (tokens)
        """
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.tokens_per_second = requests_per_minute / 60.0
        
        # Per-domain state: {domain: {'tokens': float, 'last_update': datetime}}
        self.buckets: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'tokens': burst_size,
            'last_update': datetime.now()
        })
    
    def _refill_tokens(self, domain: str):
        """Refill tokens based on elapsed time since last refill."""
        bucket = self.buckets[domain]
        now = datetime.now()
        elapsed = (now - bucket['last_update']).total_seconds()
        
        # Add tokens based on elapsed time
        new_tokens = elapsed * self.tokens_per_second
        bucket['tokens'] = min(self.burst_size, bucket['tokens'] + new_tokens)
        bucket['last_update'] = now
    
    def acquire(self, domain: str, tokens: int = 1) -> float:
        """
        Acquire tokens for a request. Blocks if tokens not available.
        
        Args:
            domain: Domain to rate limit
            tokens: Number of tokens needed (usually 1)
        
        Returns:
            Wait time in seconds (0 if no wait needed)
        """
        self._refill_tokens(domain)
        bucket = self.buckets[domain]
        
        if bucket['tokens'] >= tokens:
            bucket['tokens'] -= tokens
            return 0.0
        
        # Not enough tokens, calculate wait time
        tokens_needed = tokens - bucket['tokens']
        wait_time = tokens_needed / self.tokens_per_second
        
        # Add small random jitter to avoid thundering herd
        jitter = random.uniform(0, 0.5)
        total_wait = wait_time + jitter
        
        logger.debug(f"Rate limit for {domain}: waiting {total_wait:.2f}s")
        time.sleep(total_wait)
        
        # Refill and consume
        self._refill_tokens(domain)
        bucket['tokens'] -= tokens
        
        return total_wait
    
    def set_rate_limit(self, domain: str, requests_per_minute: int):
        """
        Set custom rate limit for a specific domain.
        
        Args:
            domain: Domain to configure
            requests_per_minute: Custom rate limit
        """
        # This creates a new bucket if it doesn't exist
        if domain not in self.buckets:
            self.buckets[domain] = {
                'tokens': self.burst_size,
                'last_update': datetime.now()
            }


class SessionManager:
    """
    Manages HTTP sessions with connection pooling, rate limiting, and retry logic.
    
    Features:
    - Connection pooling for performance
    - Per-domain rate limiting
    - User-Agent rotation
    - Automatic retry with exponential backoff
    - Request/response logging
    - Timeout management
    """
    
    def __init__(
        self,
        requests_per_minute: int = 20,
        burst_size: int = 5,
        connect_timeout: float = 10.0,
        read_timeout: float = 30.0,
        max_retries: int = 3,
        backoff_factor: float = 2.0
    ):
        """
        Initialize SessionManager.
        
        Args:
            requests_per_minute: Default rate limit (requests/min)
            burst_size: Maximum burst capacity
            connect_timeout: Connection timeout in seconds
            read_timeout: Read timeout in seconds
            max_retries: Maximum retry attempts for failed requests
            backoff_factor: Exponential backoff multiplier
        """
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        
        # Initialize components
        self.ua_rotator = UserAgentRotator()
        self.rate_limiter = RateLimiter(requests_per_minute, burst_size)
        self.session = self._create_session()
        
        # Statistics
        self.stats = {
            'requests_made': 0,
            'requests_failed': 0,
            'total_wait_time': 0.0,
            'retry_count': 0
        }
        
        logger.info(f"SessionManager initialized: {requests_per_minute} req/min, "
                   f"timeout={connect_timeout}s/{read_timeout}s")
    
    def _create_session(self) -> requests.Session:
        """
        Create a requests.Session with connection pooling and retry strategy.
        
        Returns:
            Configured requests.Session
        """
        session = requests.Session()
        
        # Configure retry strategy for urllib3
        retry_strategy = Retry(
            total=0,  # We'll handle retries manually with tenacity
            connect=0,
            read=0,
            status_forcelist=[500, 502, 503, 504],  # Retry on server errors
            backoff_factor=self.backoff_factor
        )
        
        # Mount adapter with connection pooling
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20,
            pool_block=False
        )
        
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        # Set default headers (User-Agent will be set per request)
        session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,si;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        })
        
        return session
    
    def set_rate_limit(self, domain: str, requests_per_minute: int):
        """
        Set custom rate limit for a specific domain.
        
        Args:
            domain: Domain to configure (e.g., 'example.com')
            requests_per_minute: Custom rate limit
        """
        self.rate_limiter.set_rate_limit(domain, requests_per_minute)
        logger.info(f"Set rate limit for {domain}: {requests_per_minute} req/min")
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL for rate limiting."""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=30),
        retry=retry_if_exception_type((
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.ChunkedEncodingError
        )),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        after=after_log(logger, logging.DEBUG)
    )
    def _make_request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> requests.Response:
        """
        Make HTTP request with automatic retry on transient errors.
        
        Uses tenacity for exponential backoff retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Target URL
            **kwargs: Additional arguments for requests
        
        Returns:
            Response object
        
        Raises:
            requests.exceptions.RequestException: On persistent failures
        """
        response = self.session.request(method, url, **kwargs)
        
        # Raise on HTTP errors (4xx, 5xx)
        if response.status_code >= 400:
            if response.status_code == 429:  # Too Many Requests
                logger.warning(f"Rate limited (429) by {url}")
                self.stats['retry_count'] += 1
                raise requests.exceptions.ConnectionError("Rate limited")
            elif response.status_code >= 500:  # Server errors - retry
                logger.warning(f"Server error ({response.status_code}) from {url}")
                self.stats['retry_count'] += 1
                raise requests.exceptions.ConnectionError(f"Server error: {response.status_code}")
            elif response.status_code == 403:  # Forbidden - might be blocking
                logger.error(f"Access forbidden (403) for {url}")
                # Don't retry on 403 - might need different approach
                response.raise_for_status()
        
        return response
    
    def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        allow_redirects: bool = True,
        **kwargs
    ) -> requests.Response:
        """
        Perform GET request with rate limiting and retry logic.
        
        Args:
            url: Target URL
            headers: Additional headers (User-Agent auto-added)
            params: Query parameters
            allow_redirects: Follow redirects
            **kwargs: Additional arguments for requests
        
        Returns:
            Response object
        
        Raises:
            requests.exceptions.RequestException: On request failure
        """
        domain = self._extract_domain(url)
        
        # Apply rate limiting
        wait_time = self.rate_limiter.acquire(domain)
        if wait_time > 0:
            self.stats['total_wait_time'] += wait_time
        
        # Prepare headers with rotated User-Agent
        request_headers = headers.copy() if headers else {}
        if 'User-Agent' not in request_headers:
            request_headers['User-Agent'] = self.ua_rotator.get_next()
        
        # Set timeout
        if 'timeout' not in kwargs:
            kwargs['timeout'] = (self.connect_timeout, self.read_timeout)
        
        # Make request with retry
        start_time = time.time()
        try:
            response = self._make_request_with_retry(
                'GET',
                url,
                headers=request_headers,
                params=params,
                allow_redirects=allow_redirects,
                **kwargs
            )
            
            elapsed = time.time() - start_time
            self.stats['requests_made'] += 1
            
            logger.debug(f"GET {url} → {response.status_code} ({elapsed:.2f}s)")
            
            return response
            
        except Exception as e:
            self.stats['requests_failed'] += 1
            logger.error(f"GET {url} failed after retries: {e}")
            raise
    
    def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> requests.Response:
        """
        Perform POST request with rate limiting and retry logic.
        
        Args:
            url: Target URL
            data: Form data
            json: JSON data
            headers: Additional headers
            **kwargs: Additional arguments
        
        Returns:
            Response object
        """
        domain = self._extract_domain(url)
        
        # Apply rate limiting
        wait_time = self.rate_limiter.acquire(domain)
        if wait_time > 0:
            self.stats['total_wait_time'] += wait_time
        
        # Prepare headers
        request_headers = headers.copy() if headers else {}
        if 'User-Agent' not in request_headers:
            request_headers['User-Agent'] = self.ua_rotator.get_next()
        
        # Set timeout
        if 'timeout' not in kwargs:
            kwargs['timeout'] = (self.connect_timeout, self.read_timeout)
        
        # Make request with retry
        start_time = time.time()
        try:
            response = self._make_request_with_retry(
                'POST',
                url,
                data=data,
                json=json,
                headers=request_headers,
                **kwargs
            )
            
            elapsed = time.time() - start_time
            self.stats['requests_made'] += 1
            
            logger.debug(f"POST {url} → {response.status_code} ({elapsed:.2f}s)")
            
            return response
            
        except Exception as e:
            self.stats['requests_failed'] += 1
            logger.error(f"POST {url} failed after retries: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get session statistics.
        
        Returns:
            Dict with requests_made, requests_failed, total_wait_time, retry_count
        """
        return self.stats.copy()
    
    def reset_stats(self):
        """Reset statistics counters."""
        self.stats = {
            'requests_made': 0,
            'requests_failed': 0,
            'total_wait_time': 0.0,
            'retry_count': 0
        }
        logger.info("Session statistics reset")
    
    def close(self):
        """Close the session and cleanup resources."""
        self.session.close()
        logger.info("SessionManager closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Demo usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 70)
    print("  SessionManager Test")
    print("=" * 70)
    
    # Test User-Agent rotation
    print("\n=== Testing User-Agent Rotation ===")
    rotator = UserAgentRotator()
    print(f"Random UA: {rotator.get_random()[:50]}...")
    print(f"Next UA 1: {rotator.get_next()[:50]}...")
    print(f"Next UA 2: {rotator.get_next()[:50]}...")
    
    # Test Rate Limiter
    print("\n=== Testing Rate Limiter ===")
    limiter = RateLimiter(requests_per_minute=60, burst_size=5)
    domain = "example.com"
    
    print("Making 5 burst requests (should be fast):")
    for i in range(5):
        wait = limiter.acquire(domain)
        print(f"  Request {i+1}: waited {wait:.3f}s")
    
    print("Making 6th request (should wait for refill):")
    wait = limiter.acquire(domain)
    print(f"  Request 6: waited {wait:.3f}s")
    
    # Test SessionManager
    print("\n=== Testing SessionManager ===")
    with SessionManager(requests_per_minute=30) as manager:
        try:
            # Test request to httpbin (echo service)
            url = "http://httpbin.org/get"
            print(f"Requesting: {url}")
            
            response = manager.get(url)
            print(f"✓ Status: {response.status_code}")
            print(f"✓ Response size: {len(response.content)} bytes")
            
            # Check User-Agent was sent
            import json
            data = json.loads(response.text)
            print(f"✓ User-Agent sent: {data['headers']['User-Agent'][:50]}...")
            
            # Get stats
            stats = manager.get_stats()
            print(f"\nSession stats:")
            print(f"  Requests made: {stats['requests_made']}")
            print(f"  Requests failed: {stats['requests_failed']}")
            print(f"  Total wait time: {stats['total_wait_time']:.2f}s")
            print(f"  Retries: {stats['retry_count']}")
            
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print("\n✓ SessionManager test completed!")
