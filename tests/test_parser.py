"""Tests for HTML parser."""

import pytest
from yoink.parser import Parser


class TestParser:
    """Test HTML parsing functionality."""

    def test_parse_title(self, sample_html, sample_url):
        """Test title extraction."""
        parser = Parser()
        result = parser.parse(sample_html, sample_url)

        assert result["title"] == "Test Page"

    def test_parse_links(self, sample_html, sample_url):
        """Test link extraction."""
        parser = Parser()
        result = parser.parse(sample_html, sample_url)

        links = result["links"]
        assert len(links) == 3
        assert "https://example.com/page1" in links
        assert "https://example.com/page2" in links
        assert "https://external.com" in links

    def test_parse_metadata(self, sample_html, sample_url):
        """Test metadata extraction."""
        parser = Parser()
        result = parser.parse(sample_html, sample_url)

        metadata = result["metadata"]
        assert "description" in metadata
        assert metadata["description"] == "A test page"
        assert "og:title" in metadata
        assert metadata["og:title"] == "Test OG Title"

    def test_is_same_domain(self, sample_url):
        """Test domain comparison."""
        parser = Parser()

        assert parser.is_same_domain(
            "https://example.com/page1", "https://example.com/page2"
        )
        assert not parser.is_same_domain(
            "https://example.com", "https://other.com"
        )

    def test_parse_empty_html(self, sample_url):
        """Test parsing empty HTML."""
        parser = Parser()
        result = parser.parse("", sample_url)

        assert result["title"] is None
        assert result["links"] == []
        assert result["metadata"] == {}
