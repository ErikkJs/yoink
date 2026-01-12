"""Rate limiter with per-domain token bucket algorithm."""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Optional

import structlog

logger = structlog.get_logger()


@dataclass
class DomainBucket:
    """Token bucket for a single domain."""

    tokens: float
    last_update: float
    rate: float  # tokens per second
    capacity: float  # max tokens


class RateLimiter:
    """
    Per-domain rate limiter using token bucket algorithm.

    Each domain gets its own token bucket that refills at a configurable rate.
    Requests consume tokens; if no tokens available, the caller waits.
    """

    def __init__(
        self,
        requests_per_second: float = 2.0,
        min_delay: float = 0.0,
        burst_size: int = 1,
    ):
        """
        Initialize rate limiter.

        Args:
            requests_per_second: Maximum requests per second per domain (default: 2.0)
            min_delay: Minimum delay between requests in seconds (default: 0)
            burst_size: Maximum burst capacity (default: 1)
        """
        if requests_per_second <= 0:
            raise ValueError("requests_per_second must be positive")
        if min_delay < 0:
            raise ValueError("min_delay must be non-negative")
        if burst_size < 1:
            raise ValueError("burst_size must be at least 1")

        self.requests_per_second = requests_per_second
        self.min_delay = min_delay
        self.burst_size = burst_size
        self._buckets: dict[str, DomainBucket] = {}
        self._lock = asyncio.Lock()

    def _get_bucket(self, domain: str) -> DomainBucket:
        """Get or create a token bucket for a domain."""
        if domain not in self._buckets:
            self._buckets[domain] = DomainBucket(
                tokens=float(self.burst_size),
                last_update=time.monotonic(),
                rate=self.requests_per_second,
                capacity=float(self.burst_size),
            )
        return self._buckets[domain]

    def _refill_bucket(self, bucket: DomainBucket) -> None:
        """Refill tokens based on elapsed time."""
        now = time.monotonic()
        elapsed = now - bucket.last_update
        bucket.tokens = min(bucket.capacity, bucket.tokens + elapsed * bucket.rate)
        bucket.last_update = now

    async def acquire(
        self, domain: str, crawl_delay: Optional[float] = None
    ) -> float:
        """
        Wait until a request can proceed for the given domain.

        Args:
            domain: The domain to rate limit
            crawl_delay: Optional crawl delay from robots.txt (overrides default rate)

        Returns:
            The time waited in seconds
        """
        async with self._lock:
            bucket = self._get_bucket(domain)

            # Override rate if crawl_delay specified and more restrictive
            if crawl_delay is not None and crawl_delay > 0:
                effective_rate = min(1.0 / crawl_delay, bucket.rate)
                if effective_rate < bucket.rate:
                    bucket.rate = effective_rate
                    logger.debug(
                        "rate_adjusted_for_crawl_delay",
                        domain=domain,
                        crawl_delay=crawl_delay,
                        new_rate=effective_rate,
                    )

            # Refill tokens based on elapsed time
            self._refill_bucket(bucket)

            wait_time = 0.0

            # Calculate wait time if no tokens available
            if bucket.tokens < 1.0:
                wait_time = (1.0 - bucket.tokens) / bucket.rate
                logger.debug(
                    "rate_limit_waiting",
                    domain=domain,
                    wait_time=wait_time,
                    tokens=bucket.tokens,
                )

            # Apply minimum delay floor
            wait_time = max(wait_time, self.min_delay)

        # Wait outside the lock to allow other domains to proceed
        if wait_time > 0:
            await asyncio.sleep(wait_time)

        # Consume token after waiting
        async with self._lock:
            bucket = self._get_bucket(domain)
            self._refill_bucket(bucket)
            bucket.tokens -= 1.0

        return wait_time

    async def set_domain_rate(self, domain: str, rate: float) -> None:
        """
        Set a custom rate for a specific domain.

        Args:
            domain: The domain to configure
            rate: New rate in requests per second
        """
        if rate <= 0:
            raise ValueError("rate must be positive")

        async with self._lock:
            bucket = self._get_bucket(domain)
            bucket.rate = rate
            logger.info("domain_rate_set", domain=domain, rate=rate)

    def get_stats(self) -> dict[str, dict]:
        """Get current rate limiter statistics."""
        stats = {}
        for domain, bucket in self._buckets.items():
            stats[domain] = {
                "tokens": bucket.tokens,
                "rate": bucket.rate,
                "capacity": bucket.capacity,
            }
        return stats

    def clear(self) -> None:
        """Clear all domain buckets."""
        self._buckets.clear()
