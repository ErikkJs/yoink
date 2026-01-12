"""Factory for creating fetcher instances."""

import warnings
from typing import TYPE_CHECKING, Union

from yoink.fetcher import Fetcher as HttpFetcher
from yoink.models import CrawlConfig

if TYPE_CHECKING:
    from yoink.playwright_fetcher import PlaywrightFetcher
    from yoink.rate_limiter import RateLimiter
    from yoink.robots import RobotsChecker


def create_fetcher(
    config: CrawlConfig,
    rate_limiter: "RateLimiter" = None,
    robots_checker: "RobotsChecker" = None,
) -> Union["HttpFetcher", "PlaywrightFetcher"]:
    """
    Create appropriate fetcher based on configuration.

    Args:
        config: Crawl configuration
        rate_limiter: Optional rate limiter instance
        robots_checker: Optional robots checker instance

    Returns:
        Fetcher instance (HTTP or Playwright based on config.render_js)
    """
    if config.render_js:
        from yoink.playwright_fetcher import PlaywrightFetcher, is_playwright_available

        if not is_playwright_available():
            warnings.warn(
                "JavaScript rendering requested but playwright is not installed. "
                "Falling back to HTTP fetcher. Install with: pip install 'yoink[browser]'",
                UserWarning,
                stacklevel=2,
            )
            return HttpFetcher(
                user_agent=config.user_agent,
                timeout=config.timeout,
                rate_limiter=rate_limiter,
                robots_checker=robots_checker,
            )

        return PlaywrightFetcher(
            user_agent=config.user_agent,
            timeout=config.timeout,
            headless=config.headless,
            wait_strategy=config.wait_strategy,
            wait_selector=config.wait_selector,
            browser_type=config.browser_type,
            screenshot_dir=config.screenshot_dir,
            pool_size=config.browser_pool_size,
            rate_limiter=rate_limiter,
            robots_checker=robots_checker,
        )

    return HttpFetcher(
        user_agent=config.user_agent,
        timeout=config.timeout,
        rate_limiter=rate_limiter,
        robots_checker=robots_checker,
    )
