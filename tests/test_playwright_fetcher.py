"""Tests for Playwright fetcher."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from yoink.models import WaitStrategy
from yoink.playwright_fetcher import is_playwright_available

# Skip all tests if playwright is not installed
pytestmark = pytest.mark.skipif(
    not is_playwright_available(),
    reason="playwright not installed"
)


class TestPlaywrightAvailability:
    """Test playwright availability detection."""

    def test_is_playwright_available_detection(self):
        """Test that availability check works."""
        # If we got here, playwright is available
        result = is_playwright_available()
        assert result is True


class TestPlaywrightFetcherInit:
    """Test PlaywrightFetcher initialization."""

    def test_default_values(self):
        """Test default initialization values."""
        from yoink.playwright_fetcher import PlaywrightFetcher

        fetcher = PlaywrightFetcher()
        assert fetcher.user_agent == "yoink/0.1.0"
        assert fetcher.timeout == 30000  # milliseconds
        assert fetcher.max_retries == 3
        assert fetcher.headless is True
        assert fetcher.wait_strategy == WaitStrategy.NETWORKIDLE
        assert fetcher.wait_selector is None
        assert fetcher.browser_type == "chromium"
        assert fetcher.pool_size == 3

    def test_custom_values(self):
        """Test custom initialization values."""
        from yoink.playwright_fetcher import PlaywrightFetcher

        fetcher = PlaywrightFetcher(
            user_agent="custom-agent",
            timeout=60,
            max_retries=5,
            headless=False,
            wait_strategy=WaitStrategy.LOAD,
            wait_selector=".content",
            browser_type="firefox",
            pool_size=5,
        )
        assert fetcher.user_agent == "custom-agent"
        assert fetcher.timeout == 60000
        assert fetcher.max_retries == 5
        assert fetcher.headless is False
        assert fetcher.wait_strategy == WaitStrategy.LOAD
        assert fetcher.wait_selector == ".content"
        assert fetcher.browser_type == "firefox"
        assert fetcher.pool_size == 5


@pytest.mark.asyncio
class TestPlaywrightFetcherMocked:
    """Test PlaywrightFetcher with mocked browser."""

    @pytest.fixture
    def mock_playwright_objects(self):
        """Create mocked playwright objects."""
        mock_page = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html><body>Rendered</body></html>")
        mock_page.goto = AsyncMock(return_value=MagicMock(status=200))
        mock_page.close = AsyncMock()
        mock_page.set_default_timeout = MagicMock()
        mock_page.wait_for_selector = AsyncMock()
        mock_page.screenshot = AsyncMock()

        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_context.close = AsyncMock()
        mock_context.clear_cookies = AsyncMock()

        mock_browser = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_browser.close = AsyncMock()

        mock_chromium = AsyncMock()
        mock_chromium.launch = AsyncMock(return_value=mock_browser)

        mock_pw_instance = MagicMock()
        mock_pw_instance.chromium = mock_chromium
        mock_pw_instance.stop = AsyncMock()

        mock_pw_cm = AsyncMock()
        mock_pw_cm.start = AsyncMock(return_value=mock_pw_instance)

        return {
            "pw_cm": mock_pw_cm,
            "pw": mock_pw_instance,
            "browser": mock_browser,
            "context": mock_context,
            "page": mock_page,
        }

    async def test_fetch_success(self, mock_playwright_objects):
        """Test successful fetch with mocked browser."""
        with patch("yoink.playwright_fetcher.is_playwright_available", return_value=True):
            with patch(
                "playwright.async_api.async_playwright",
                return_value=mock_playwright_objects["pw_cm"],
            ):
                from yoink.playwright_fetcher import PlaywrightFetcher

                fetcher = PlaywrightFetcher()
                async with fetcher:
                    html, status = await fetcher.fetch("https://example.com")

                    assert status == 200
                    assert "Rendered" in html
                    mock_playwright_objects["page"].goto.assert_called_once()

    async def test_fetch_with_wait_selector(self, mock_playwright_objects):
        """Test fetch with wait_selector option."""
        with patch("yoink.playwright_fetcher.is_playwright_available", return_value=True):
            with patch(
                "playwright.async_api.async_playwright",
                return_value=mock_playwright_objects["pw_cm"],
            ):
                from yoink.playwright_fetcher import PlaywrightFetcher

                fetcher = PlaywrightFetcher(wait_selector=".content-loaded")
                async with fetcher:
                    await fetcher.fetch("https://example.com")

                    mock_playwright_objects["page"].wait_for_selector.assert_called_once_with(
                        ".content-loaded",
                        timeout=10000,
                    )

    async def test_fetch_retry_on_error(self, mock_playwright_objects):
        """Test retry logic on navigation errors."""
        mock_playwright_objects["page"].goto = AsyncMock(
            side_effect=[Exception("Timeout"), MagicMock(status=200)]
        )

        with patch("yoink.playwright_fetcher.is_playwright_available", return_value=True):
            with patch(
                "playwright.async_api.async_playwright",
                return_value=mock_playwright_objects["pw_cm"],
            ):
                from yoink.playwright_fetcher import PlaywrightFetcher

                fetcher = PlaywrightFetcher(max_retries=3)
                async with fetcher:
                    html, status = await fetcher.fetch("https://example.com")

                    assert status == 200
                    assert mock_playwright_objects["page"].goto.call_count == 2

    async def test_fetch_without_context_manager_raises(self):
        """Test that fetch without context manager raises error."""
        from yoink.playwright_fetcher import PlaywrightFetcher

        fetcher = PlaywrightFetcher()

        with pytest.raises(RuntimeError, match="must be used as async context manager"):
            await fetcher.fetch("https://example.com")

    async def test_context_manager_cleanup(self, mock_playwright_objects):
        """Test that browser is properly cleaned up."""
        with patch("yoink.playwright_fetcher.is_playwright_available", return_value=True):
            with patch(
                "playwright.async_api.async_playwright",
                return_value=mock_playwright_objects["pw_cm"],
            ):
                from yoink.playwright_fetcher import PlaywrightFetcher

                fetcher = PlaywrightFetcher(pool_size=2)
                async with fetcher:
                    pass

                mock_playwright_objects["browser"].close.assert_called_once()
                mock_playwright_objects["pw"].stop.assert_called_once()

    async def test_playwright_not_available_raises(self):
        """Test that ImportError is raised when playwright not available."""
        with patch("yoink.playwright_fetcher.is_playwright_available", return_value=False):
            from yoink.playwright_fetcher import PlaywrightFetcher

            fetcher = PlaywrightFetcher()

            with pytest.raises(ImportError, match="playwright is required"):
                async with fetcher:
                    pass
