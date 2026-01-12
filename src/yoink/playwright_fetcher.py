"""Playwright-based fetcher for JavaScript rendering."""

import asyncio
import hashlib
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Optional

import structlog

from yoink.models import WaitStrategy

if TYPE_CHECKING:
    from yoink.rate_limiter import RateLimiter
    from yoink.robots import RobotsChecker

logger = structlog.get_logger()

# Lazy import check for optional dependency
_playwright_available: Optional[bool] = None


def is_playwright_available() -> bool:
    """Check if playwright is installed."""
    global _playwright_available
    if _playwright_available is None:
        try:
            import playwright  # noqa: F401

            _playwright_available = True
        except ImportError:
            _playwright_available = False
    return _playwright_available


class PlaywrightFetcher:
    """
    Browser-based fetcher using Playwright for JavaScript rendering.

    This fetcher uses a real browser to render pages, enabling crawling
    of JavaScript-heavy SPAs and dynamic content.
    """

    def __init__(
        self,
        user_agent: str = "yoink/0.1.0",
        timeout: int = 30,
        max_retries: int = 3,
        headless: bool = True,
        wait_strategy: WaitStrategy = WaitStrategy.NETWORKIDLE,
        wait_selector: Optional[str] = None,
        wait_timeout: int = 10000,
        browser_type: Literal["chromium", "firefox", "webkit"] = "chromium",
        screenshot_dir: Optional[str] = None,
        pool_size: int = 3,
        rate_limiter: Optional["RateLimiter"] = None,
        robots_checker: Optional["RobotsChecker"] = None,
    ):
        """
        Initialize Playwright fetcher.

        Args:
            user_agent: User agent string for browser
            timeout: Page load timeout in seconds
            max_retries: Maximum retry attempts on failure
            headless: Run browser in headless mode
            wait_strategy: Page load wait strategy
            wait_selector: Optional CSS selector to wait for
            wait_timeout: Timeout for wait_selector in milliseconds
            browser_type: Browser engine (chromium, firefox, webkit)
            screenshot_dir: Directory to save debug screenshots
            pool_size: Number of browser contexts to pool
            rate_limiter: Optional rate limiter
            robots_checker: Optional robots checker for crawl delay
        """
        self.user_agent = user_agent
        self.timeout = timeout * 1000  # Playwright uses milliseconds
        self.max_retries = max_retries
        self.headless = headless
        self.wait_strategy = wait_strategy
        self.wait_selector = wait_selector
        self.wait_timeout = wait_timeout
        self.browser_type = browser_type
        self.screenshot_dir = screenshot_dir
        self.pool_size = pool_size
        self.rate_limiter = rate_limiter
        self.robots_checker = robots_checker

        self._playwright = None
        self._browser = None
        self._context_pool: list = []
        self._context_lock = asyncio.Lock()

    async def __aenter__(self):
        """Initialize browser on context enter."""
        if not is_playwright_available():
            raise ImportError(
                "playwright is required for JavaScript rendering. "
                "Install with: pip install 'yoink[browser]' && playwright install chromium"
            )

        from playwright.async_api import async_playwright

        self._playwright = await async_playwright().start()
        browser_launcher = getattr(self._playwright, self.browser_type)
        self._browser = await browser_launcher.launch(headless=self.headless)

        # Pre-create browser contexts for pool
        for _ in range(self.pool_size):
            context = await self._create_context()
            self._context_pool.append(context)

        logger.info(
            "playwright_fetcher_started",
            browser=self.browser_type,
            headless=self.headless,
            pool_size=self.pool_size,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup browser on context exit."""
        # Close all contexts in pool
        for context in self._context_pool:
            try:
                await context.close()
            except Exception:
                pass
        self._context_pool.clear()

        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

        logger.info("playwright_fetcher_stopped")

    async def _create_context(self):
        """Create a new browser context with configured settings."""
        return await self._browser.new_context(
            user_agent=self.user_agent,
            viewport={"width": 1920, "height": 1080},
        )

    async def _acquire_context(self):
        """Acquire a context from the pool."""
        async with self._context_lock:
            if self._context_pool:
                return self._context_pool.pop()
            # Pool exhausted, create new context
            return await self._create_context()

    async def _release_context(self, context):
        """Return context to pool."""
        async with self._context_lock:
            try:
                # Clear cookies/storage before reuse
                await context.clear_cookies()
                self._context_pool.append(context)
            except Exception:
                # Context might be closed, create new one
                try:
                    new_context = await self._create_context()
                    self._context_pool.append(new_context)
                except Exception:
                    pass

    async def fetch(self, url: str) -> tuple[str, int]:
        """
        Fetch URL with JavaScript rendering.

        Args:
            url: The URL to fetch

        Returns:
            Tuple of (rendered HTML content, HTTP status code)

        Raises:
            RuntimeError: If fetcher not initialized as context manager
            Exception: On fetch failure after retries
        """
        if not self._browser:
            raise RuntimeError("PlaywrightFetcher must be used as async context manager")

        # Apply rate limiting if configured
        if self.rate_limiter:
            from urllib.parse import urlparse

            domain = urlparse(url).netloc
            crawl_delay = None
            if self.robots_checker:
                crawl_delay = await self.robots_checker.get_crawl_delay(domain)
            await self.rate_limiter.acquire(domain, crawl_delay)

        context = await self._acquire_context()
        page = None
        last_error = None

        try:
            for attempt in range(self.max_retries):
                try:
                    page = await context.new_page()
                    page.set_default_timeout(self.timeout)

                    # Navigate with configured wait strategy
                    response = await page.goto(
                        url,
                        wait_until=self.wait_strategy.value,
                        timeout=self.timeout,
                    )

                    # Additional wait for selector if specified
                    if self.wait_selector:
                        await page.wait_for_selector(
                            self.wait_selector,
                            timeout=self.wait_timeout,
                        )

                    # Get status code from response
                    status_code = response.status if response else 200

                    # Get rendered HTML
                    content = await page.content()

                    # Optional screenshot for debugging
                    if self.screenshot_dir:
                        await self._save_screenshot(page, url)

                    logger.info(
                        "playwright_fetched_url",
                        url=url,
                        status=status_code,
                        size=len(content),
                    )

                    return content, status_code

                except Exception as e:
                    last_error = e
                    logger.warning(
                        "playwright_fetch_error",
                        url=url,
                        error=str(e),
                        attempt=attempt + 1,
                    )
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(2**attempt)
                finally:
                    if page:
                        try:
                            await page.close()
                        except Exception:
                            pass
                        page = None

        finally:
            await self._release_context(context)

        # All retries exhausted
        raise last_error or RuntimeError(f"Failed to fetch {url}")

    async def _save_screenshot(self, page, url: str) -> None:
        """Save screenshot for debugging."""
        try:
            # Create safe filename from URL
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            filename = f"screenshot_{url_hash}.png"
            filepath = Path(self.screenshot_dir) / filename

            # Ensure directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)

            await page.screenshot(path=str(filepath))
            logger.debug("screenshot_saved", path=str(filepath), url=url)
        except Exception as e:
            logger.warning("screenshot_failed", url=url, error=str(e))
