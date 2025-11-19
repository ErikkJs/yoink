"""Tests for data models."""

import pytest
from yoink.models import Page, CrawlConfig


class TestPage:
    """Test Page model."""

    def test_create_page(self):
        """Test creating a Page instance."""
        page = Page(
            url="https://example.com",
            title="Test",
            text="Some text",
            links=["https://example.com/1"],
        )

        assert page.url == "https://example.com"
        assert page.title == "Test"
        assert page.text == "Some text"
        assert len(page.links) == 1
        assert page.status_code == 200
        assert page.depth == 0

    def test_page_defaults(self):
        """Test Page default values."""
        page = Page(url="https://example.com")

        assert page.title is None
        assert page.text is None
        assert page.html is None
        assert page.links == []
        assert page.metadata == {}
        assert page.status_code == 200
        assert page.depth == 0

    def test_page_serialization(self):
        """Test Page JSON serialization."""
        page = Page(url="https://example.com", title="Test")
        data = page.model_dump(mode="json")

        assert data["url"] == "https://example.com"
        assert data["title"] == "Test"
        assert isinstance(data["crawled_at"], str)


class TestCrawlConfig:
    """Test CrawlConfig model."""

    def test_create_config(self):
        """Test creating CrawlConfig instance."""
        config = CrawlConfig(
            max_depth=2, max_pages=100, max_concurrency=10
        )

        assert config.max_depth == 2
        assert config.max_pages == 100
        assert config.max_concurrency == 10
        assert config.respect_robots is True
        assert config.extract_text is True

    def test_config_defaults(self):
        """Test CrawlConfig default values."""
        config = CrawlConfig()

        assert config.max_depth == 1
        assert config.max_pages == 100
        assert config.max_concurrency == 10
        assert config.timeout == 30
        assert config.respect_robots is True
        assert config.follow_external is False

    def test_config_validation(self):
        """Test CrawlConfig validation."""
        # Valid config
        config = CrawlConfig(max_depth=0)
        assert config.max_depth == 0

        # Invalid config (negative depth) should raise
        with pytest.raises(Exception):
            CrawlConfig(max_depth=-1)
