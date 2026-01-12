"""Tests for fetcher factory."""

import warnings

import pytest
from unittest.mock import patch

from yoink.models import CrawlConfig
from yoink.fetcher import Fetcher as HttpFetcher
from yoink.fetcher_factory import create_fetcher
from yoink.playwright_fetcher import is_playwright_available


class TestFetcherFactory:
    """Test fetcher factory."""

    def test_create_http_fetcher_by_default(self):
        """Factory returns HTTP fetcher when render_js is False."""
        config = CrawlConfig(render_js=False)
        fetcher = create_fetcher(config)
        assert isinstance(fetcher, HttpFetcher)

    def test_http_fetcher_has_correct_settings(self):
        """HTTP fetcher has settings from config."""
        config = CrawlConfig(
            render_js=False,
            user_agent="test-agent",
            timeout=60,
        )
        fetcher = create_fetcher(config)
        assert fetcher.user_agent == "test-agent"
        assert fetcher.timeout.total == 60

    @pytest.mark.skipif(
        not is_playwright_available(),
        reason="playwright not installed"
    )
    def test_create_playwright_fetcher_when_available(self):
        """Factory returns Playwright fetcher when render_js is True."""
        from yoink.playwright_fetcher import PlaywrightFetcher

        config = CrawlConfig(render_js=True)
        fetcher = create_fetcher(config)
        assert isinstance(fetcher, PlaywrightFetcher)

    @pytest.mark.skipif(
        not is_playwright_available(),
        reason="playwright not installed"
    )
    def test_playwright_fetcher_has_correct_settings(self):
        """Playwright fetcher has settings from config."""
        from yoink.playwright_fetcher import PlaywrightFetcher

        config = CrawlConfig(
            render_js=True,
            user_agent="test-agent",
            timeout=60,
            headless=False,
            browser_type="firefox",
            browser_pool_size=5,
        )
        fetcher = create_fetcher(config)

        assert isinstance(fetcher, PlaywrightFetcher)
        assert fetcher.user_agent == "test-agent"
        assert fetcher.timeout == 60000  # milliseconds
        assert fetcher.headless is False
        assert fetcher.browser_type == "firefox"
        assert fetcher.pool_size == 5

    def test_fallback_to_http_when_playwright_unavailable(self):
        """Factory falls back to HTTP when playwright not installed."""
        with patch(
            "yoink.playwright_fetcher.is_playwright_available", return_value=False
        ):
            config = CrawlConfig(render_js=True)

            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                fetcher = create_fetcher(config)

                assert isinstance(fetcher, HttpFetcher)
                assert len(w) == 1
                assert "playwright is not installed" in str(w[0].message)

    def test_rate_limiter_passed_to_http_fetcher(self):
        """Rate limiter is passed to HTTP fetcher."""
        from yoink.rate_limiter import RateLimiter

        config = CrawlConfig(render_js=False)
        rate_limiter = RateLimiter()
        fetcher = create_fetcher(config, rate_limiter=rate_limiter)

        assert fetcher.rate_limiter is rate_limiter

    @pytest.mark.skipif(
        not is_playwright_available(),
        reason="playwright not installed"
    )
    def test_rate_limiter_passed_to_playwright_fetcher(self):
        """Rate limiter is passed to Playwright fetcher."""
        from yoink.rate_limiter import RateLimiter
        from yoink.playwright_fetcher import PlaywrightFetcher

        config = CrawlConfig(render_js=True)
        rate_limiter = RateLimiter()
        fetcher = create_fetcher(config, rate_limiter=rate_limiter)

        assert isinstance(fetcher, PlaywrightFetcher)
        assert fetcher.rate_limiter is rate_limiter

    def test_robots_checker_passed_to_http_fetcher(self):
        """Robots checker is passed to HTTP fetcher."""
        from yoink.robots import RobotsChecker

        config = CrawlConfig(render_js=False)
        robots_checker = RobotsChecker()
        fetcher = create_fetcher(config, robots_checker=robots_checker)

        assert fetcher.robots_checker is robots_checker
