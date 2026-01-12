"""HTTP fetcher with async support."""

import asyncio
from typing import TYPE_CHECKING, Optional
from urllib.parse import urlparse

import aiohttp
import structlog

if TYPE_CHECKING:
    from yoink.rate_limiter import RateLimiter
    from yoink.robots import RobotsChecker

logger = structlog.get_logger()


class Fetcher:
    """Async HTTP client wrapper."""

    def __init__(
        self,
        user_agent: str = "yoink/0.1.0",
        timeout: int = 30,
        max_retries: int = 3,
        rate_limiter: Optional["RateLimiter"] = None,
        robots_checker: Optional["RobotsChecker"] = None,
    ):
        self.user_agent = user_agent
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.rate_limiter = rate_limiter
        self.robots_checker = robots_checker
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Create session on context enter."""
        self._session = aiohttp.ClientSession(
            headers={"User-Agent": self.user_agent},
            timeout=self.timeout,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close session on context exit."""
        if self._session:
            await self._session.close()

    async def fetch(self, url: str) -> tuple[str, int]:
        """
        Fetch a URL and return (content, status_code).

        Args:
            url: The URL to fetch

        Returns:
            Tuple of (HTML content, HTTP status code)

        Raises:
            aiohttp.ClientError: On request failure after retries
        """
        if not self._session:
            raise RuntimeError("Fetcher must be used as async context manager")

        # Apply rate limiting if configured
        if self.rate_limiter:
            domain = urlparse(url).netloc
            crawl_delay = None
            if self.robots_checker:
                crawl_delay = await self.robots_checker.get_crawl_delay(domain)
            await self.rate_limiter.acquire(domain, crawl_delay)

        for attempt in range(self.max_retries):
            try:
                async with self._session.get(url) as response:
                    content = await response.text()
                    logger.info(
                        "fetched_url",
                        url=url,
                        status=response.status,
                        size=len(content),
                    )
                    return content, response.status

            except asyncio.TimeoutError:
                logger.warning("timeout", url=url, attempt=attempt + 1)
                if attempt == self.max_retries - 1:
                    raise

            except aiohttp.ClientError as e:
                logger.error("fetch_error", url=url, error=str(e), attempt=attempt + 1)
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(2**attempt)  # Exponential backoff

        raise RuntimeError("Unreachable code")
