"""Tests for rate limiter."""

import asyncio
import time

import pytest

from yoink.rate_limiter import RateLimiter, DomainBucket


class TestDomainBucket:
    """Test DomainBucket dataclass."""

    def test_create_bucket(self):
        """Test creating a domain bucket."""
        bucket = DomainBucket(
            tokens=5.0,
            last_update=time.monotonic(),
            rate=2.0,
            capacity=5.0,
        )
        assert bucket.tokens == 5.0
        assert bucket.rate == 2.0
        assert bucket.capacity == 5.0


class TestRateLimiterInit:
    """Test RateLimiter initialization."""

    def test_default_values(self):
        """Test default initialization values."""
        limiter = RateLimiter()
        assert limiter.requests_per_second == 2.0
        assert limiter.min_delay == 0.0
        assert limiter.burst_size == 1

    def test_custom_values(self):
        """Test custom initialization values."""
        limiter = RateLimiter(
            requests_per_second=5.0,
            min_delay=0.5,
            burst_size=3,
        )
        assert limiter.requests_per_second == 5.0
        assert limiter.min_delay == 0.5
        assert limiter.burst_size == 3

    def test_invalid_requests_per_second(self):
        """Test that invalid requests_per_second raises error."""
        with pytest.raises(ValueError, match="requests_per_second must be positive"):
            RateLimiter(requests_per_second=0)

        with pytest.raises(ValueError, match="requests_per_second must be positive"):
            RateLimiter(requests_per_second=-1)

    def test_invalid_min_delay(self):
        """Test that negative min_delay raises error."""
        with pytest.raises(ValueError, match="min_delay must be non-negative"):
            RateLimiter(min_delay=-0.1)

    def test_invalid_burst_size(self):
        """Test that invalid burst_size raises error."""
        with pytest.raises(ValueError, match="burst_size must be at least 1"):
            RateLimiter(burst_size=0)


@pytest.mark.asyncio
class TestRateLimiterAcquire:
    """Test RateLimiter.acquire() method."""

    async def test_first_request_immediate(self):
        """Test that first request proceeds immediately."""
        limiter = RateLimiter(requests_per_second=10.0)

        start = time.monotonic()
        await limiter.acquire("example.com")
        elapsed = time.monotonic() - start

        # First request should be nearly instant
        assert elapsed < 0.1

    async def test_rate_limiting_enforced(self):
        """Test that rate limiting delays subsequent requests."""
        limiter = RateLimiter(requests_per_second=2.0, burst_size=1)

        # First request
        await limiter.acquire("example.com")

        # Second request should be delayed
        start = time.monotonic()
        await limiter.acquire("example.com")
        elapsed = time.monotonic() - start

        # Should wait approximately 0.5 seconds (1/2 req/sec)
        assert elapsed >= 0.4  # Allow some tolerance

    async def test_per_domain_isolation(self):
        """Test that rate limits are per-domain."""
        limiter = RateLimiter(requests_per_second=1.0, burst_size=1)

        # Consume token for domain A
        await limiter.acquire("a.com")

        # Domain B should proceed immediately
        start = time.monotonic()
        await limiter.acquire("b.com")
        elapsed = time.monotonic() - start

        assert elapsed < 0.1

    async def test_burst_capacity(self):
        """Test that burst allows multiple immediate requests."""
        limiter = RateLimiter(requests_per_second=1.0, burst_size=3)

        start = time.monotonic()

        # All 3 should proceed quickly due to burst
        await limiter.acquire("example.com")
        await limiter.acquire("example.com")
        await limiter.acquire("example.com")

        elapsed = time.monotonic() - start

        # Should be relatively fast for burst
        assert elapsed < 0.5

    async def test_min_delay_enforced(self):
        """Test that minimum delay is enforced."""
        limiter = RateLimiter(
            requests_per_second=100.0,  # Very high rate
            min_delay=0.2,  # But enforce minimum delay
            burst_size=5,
        )

        # First request
        await limiter.acquire("example.com")

        # Second request should have min_delay
        start = time.monotonic()
        await limiter.acquire("example.com")
        elapsed = time.monotonic() - start

        assert elapsed >= 0.15  # Allow some tolerance

    async def test_crawl_delay_override(self):
        """Test that crawl_delay overrides default rate when more restrictive."""
        limiter = RateLimiter(requests_per_second=10.0)  # 10 req/sec

        # First request
        await limiter.acquire("example.com", crawl_delay=0.5)  # 2 req/sec

        # Second request should respect crawl_delay
        start = time.monotonic()
        await limiter.acquire("example.com")
        elapsed = time.monotonic() - start

        # Should wait approximately 0.5 seconds
        assert elapsed >= 0.4

    async def test_crawl_delay_ignored_when_less_restrictive(self):
        """Test that crawl_delay is ignored when less restrictive than default."""
        limiter = RateLimiter(requests_per_second=1.0)  # 1 req/sec

        # First request with less restrictive crawl_delay
        await limiter.acquire("example.com", crawl_delay=0.1)  # 10 req/sec

        # Second request should still use default rate
        start = time.monotonic()
        await limiter.acquire("example.com")
        elapsed = time.monotonic() - start

        # Should wait approximately 1.0 seconds (default rate wins)
        assert elapsed >= 0.8


@pytest.mark.asyncio
class TestRateLimiterConcurrency:
    """Test RateLimiter with concurrent access."""

    async def test_concurrent_different_domains(self):
        """Test concurrent requests to different domains."""
        limiter = RateLimiter(requests_per_second=1.0)

        async def acquire_domain(domain: str):
            await limiter.acquire(domain)
            return domain

        start = time.monotonic()
        results = await asyncio.gather(
            acquire_domain("a.com"),
            acquire_domain("b.com"),
            acquire_domain("c.com"),
        )
        elapsed = time.monotonic() - start

        # All should complete quickly (different domains)
        assert elapsed < 0.5
        assert set(results) == {"a.com", "b.com", "c.com"}

    async def test_concurrent_same_domain(self):
        """Test concurrent requests to same domain are serialized."""
        limiter = RateLimiter(requests_per_second=2.0, burst_size=1)

        results = []

        async def acquire_with_timestamp():
            await limiter.acquire("example.com")
            results.append(time.monotonic())

        start = time.monotonic()
        await asyncio.gather(
            acquire_with_timestamp(),
            acquire_with_timestamp(),
            acquire_with_timestamp(),
        )
        elapsed = time.monotonic() - start

        # With burst_size=1 and 2 req/sec, 3 requests need ~1 second
        # But due to concurrent lock contention, may be faster
        # At minimum, should take at least 0.4 seconds (not instant)
        assert elapsed >= 0.4


@pytest.mark.asyncio
class TestRateLimiterMethods:
    """Test other RateLimiter methods."""

    async def test_set_domain_rate(self):
        """Test setting custom rate for domain."""
        limiter = RateLimiter(requests_per_second=10.0)

        await limiter.acquire("example.com")
        await limiter.set_domain_rate("example.com", 1.0)

        start = time.monotonic()
        await limiter.acquire("example.com")
        elapsed = time.monotonic() - start

        # Should now wait ~1 second
        assert elapsed >= 0.8

    async def test_set_domain_rate_invalid(self):
        """Test that invalid rate raises error."""
        limiter = RateLimiter()

        with pytest.raises(ValueError, match="rate must be positive"):
            await limiter.set_domain_rate("example.com", 0)

    async def test_get_stats(self):
        """Test getting rate limiter statistics."""
        limiter = RateLimiter(requests_per_second=5.0, burst_size=2)

        await limiter.acquire("a.com")
        await limiter.acquire("b.com")

        stats = limiter.get_stats()

        assert "a.com" in stats
        assert "b.com" in stats
        assert stats["a.com"]["rate"] == 5.0
        assert stats["a.com"]["capacity"] == 2.0

    async def test_clear(self):
        """Test clearing all buckets."""
        limiter = RateLimiter()

        await limiter.acquire("a.com")
        await limiter.acquire("b.com")

        assert len(limiter._buckets) == 2

        limiter.clear()

        assert len(limiter._buckets) == 0
