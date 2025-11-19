"""Tests for URL filtering."""

import pytest
from yoink.filters import URLFilter, DomainFilter, CombinedFilter


class TestURLFilter:
    """Test URL pattern filtering."""

    def test_no_filters(self):
        """Test that all URLs pass with no filters."""
        filter = URLFilter()

        assert filter.should_crawl("https://example.com")
        assert filter.should_crawl("https://example.com/page")
        assert filter.should_crawl("https://other.com")

    def test_include_patterns_glob(self):
        """Test include patterns with glob."""
        filter = URLFilter(include_patterns=["https://example.com/blog/*"])

        assert filter.should_crawl("https://example.com/blog/post1")
        assert filter.should_crawl("https://example.com/blog/post2")
        assert not filter.should_crawl("https://example.com/about")
        assert not filter.should_crawl("https://other.com/blog/post1")

    def test_multiple_include_patterns(self):
        """Test multiple include patterns (OR logic)."""
        filter = URLFilter(
            include_patterns=[
                "https://example.com/blog/*",
                "https://example.com/docs/*",
            ]
        )

        assert filter.should_crawl("https://example.com/blog/post1")
        assert filter.should_crawl("https://example.com/docs/guide")
        assert not filter.should_crawl("https://example.com/about")

    def test_exclude_patterns_glob(self):
        """Test exclude patterns with glob."""
        filter = URLFilter(exclude_patterns=["*/download/*"])

        assert filter.should_crawl("https://example.com/blog/post")
        assert not filter.should_crawl("https://example.com/download/file.pdf")
        assert not filter.should_crawl("https://other.com/download/app.exe")

    def test_multiple_exclude_patterns(self):
        """Test multiple exclude patterns."""
        filter = URLFilter(
            exclude_patterns=[
                "*/download/*",
                "*/private/*",
            ]
        )

        assert filter.should_crawl("https://example.com/blog/post")
        assert not filter.should_crawl("https://example.com/download/file")
        assert not filter.should_crawl("https://example.com/private/data")

    def test_include_and_exclude(self):
        """Test combination of include and exclude patterns."""
        filter = URLFilter(
            include_patterns=["https://example.com/*"],
            exclude_patterns=["*/download/*"],
        )

        assert filter.should_crawl("https://example.com/blog/post")
        assert not filter.should_crawl("https://example.com/download/file")
        assert not filter.should_crawl("https://other.com/blog/post")  # Not in include

    def test_skip_extensions(self):
        """Test skipping file extensions."""
        filter = URLFilter(skip_extensions=["pdf", "zip", "exe"])

        assert filter.should_crawl("https://example.com/page.html")
        assert filter.should_crawl("https://example.com/page")
        assert not filter.should_crawl("https://example.com/file.pdf")
        assert not filter.should_crawl("https://example.com/archive.zip")
        assert not filter.should_crawl("https://example.com/app.exe")

    def test_skip_extensions_case_insensitive(self):
        """Test that extension matching is case-insensitive."""
        filter = URLFilter(skip_extensions=["PDF"])

        assert not filter.should_crawl("https://example.com/file.pdf")
        assert not filter.should_crawl("https://example.com/file.PDF")
        assert not filter.should_crawl("https://example.com/file.Pdf")

    def test_skip_extensions_with_dot(self):
        """Test that extensions work with or without leading dot."""
        filter = URLFilter(skip_extensions=[".pdf", "zip"])

        assert not filter.should_crawl("https://example.com/file.pdf")
        assert not filter.should_crawl("https://example.com/file.zip")

    def test_regex_pattern(self):
        """Test regex pattern matching."""
        filter = URLFilter(include_patterns=[r"^https://example\.com/blog/\d+$"])

        assert filter.should_crawl("https://example.com/blog/123")
        assert filter.should_crawl("https://example.com/blog/456")
        assert not filter.should_crawl("https://example.com/blog/abc")
        assert not filter.should_crawl("https://example.com/blog/")

    def test_substring_match(self):
        """Test simple substring matching."""
        filter = URLFilter(include_patterns=["python"])

        assert filter.should_crawl("https://example.com/python-tutorial")
        assert filter.should_crawl("https://docs.python.org")
        assert not filter.should_crawl("https://example.com/java-tutorial")

    def test_get_stats(self):
        """Test filter statistics."""
        filter = URLFilter(
            include_patterns=["pattern1", "pattern2"],
            exclude_patterns=["pattern3"],
            skip_extensions=["pdf", "zip"],
        )

        stats = filter.get_stats()
        assert stats["include_patterns"] == 2
        assert stats["exclude_patterns"] == 1
        assert stats["skip_extensions"] == 2


class TestDomainFilter:
    """Test domain filtering."""

    def test_no_filter(self):
        """Test that all domains pass with no filter."""
        filter = DomainFilter()

        assert filter.should_crawl("https://example.com")
        assert filter.should_crawl("https://other.com")

    def test_allowed_domains_exact(self):
        """Test exact domain matching."""
        filter = DomainFilter(allowed_domains=["example.com"])

        assert filter.should_crawl("https://example.com")
        assert filter.should_crawl("https://example.com/page")
        assert not filter.should_crawl("https://other.com")

    def test_allowed_domains_subdomain(self):
        """Test subdomain matching."""
        filter = DomainFilter(allowed_domains=["example.com"])

        assert filter.should_crawl("https://example.com")
        assert filter.should_crawl("https://blog.example.com")
        assert filter.should_crawl("https://docs.example.com")
        assert not filter.should_crawl("https://example.org")

    def test_multiple_allowed_domains(self):
        """Test multiple allowed domains."""
        filter = DomainFilter(allowed_domains=["example.com", "test.org"])

        assert filter.should_crawl("https://example.com")
        assert filter.should_crawl("https://test.org")
        assert filter.should_crawl("https://blog.example.com")
        assert not filter.should_crawl("https://other.com")


class TestCombinedFilter:
    """Test combined filtering."""

    def test_url_and_domain_filters(self):
        """Test combination of URL and domain filters."""
        url_filter = URLFilter(include_patterns=["*/blog/*"])
        domain_filter = DomainFilter(allowed_domains=["example.com"])
        combined = CombinedFilter(url_filter=url_filter, domain_filter=domain_filter)

        # Must match both filters
        assert combined.should_crawl("https://example.com/blog/post")

        # Fails domain filter
        assert not combined.should_crawl("https://other.com/blog/post")

        # Fails URL filter
        assert not combined.should_crawl("https://example.com/about")

    def test_from_config(self):
        """Test creating filter from configuration."""
        combined = CombinedFilter.from_config(
            include_patterns=["*/blog/*"],
            exclude_patterns=["*/private/*"],
            skip_extensions=["pdf"],
            allowed_domains=["example.com"],
        )

        assert combined.should_crawl("https://example.com/blog/post")
        assert not combined.should_crawl("https://example.com/blog/file.pdf")
        assert not combined.should_crawl("https://example.com/blog/private/post")
        assert not combined.should_crawl("https://other.com/blog/post")

    def test_from_config_empty(self):
        """Test creating filter with no configuration."""
        combined = CombinedFilter.from_config()

        # Should allow everything
        assert combined.should_crawl("https://example.com")
        assert combined.should_crawl("https://other.com/anything")

    def test_only_url_filter(self):
        """Test combined filter with only URL filter."""
        combined = CombinedFilter.from_config(
            include_patterns=["*/blog/*"]
        )

        assert combined.should_crawl("https://example.com/blog/post")
        assert combined.should_crawl("https://other.com/blog/post")
        assert not combined.should_crawl("https://example.com/about")

    def test_only_domain_filter(self):
        """Test combined filter with only domain filter."""
        combined = CombinedFilter.from_config(
            allowed_domains=["example.com"]
        )

        assert combined.should_crawl("https://example.com/anything")
        assert combined.should_crawl("https://blog.example.com/anything")
        assert not combined.should_crawl("https://other.com/anything")

    def test_complex_filtering(self):
        """Test complex real-world filtering scenario."""
        combined = CombinedFilter.from_config(
            include_patterns=[
                "https://docs.python.org/3/*",
                "https://docs.python.org/3.11/*",
            ],
            exclude_patterns=[
                "*/download/*",
                "*/archives/*",
            ],
            skip_extensions=["pdf", "zip", "tar.gz"],
            allowed_domains=["docs.python.org"],
        )

        # Should pass
        assert combined.should_crawl("https://docs.python.org/3/tutorial/")
        assert combined.should_crawl("https://docs.python.org/3.11/library/")

        # Should fail - wrong domain
        assert not combined.should_crawl("https://python.org/downloads/")

        # Should fail - doesn't match include pattern
        assert not combined.should_crawl("https://docs.python.org/2/tutorial/")

        # Should fail - matches exclude pattern
        assert not combined.should_crawl("https://docs.python.org/3/download/source/")

        # Should fail - has excluded extension
        assert not combined.should_crawl("https://docs.python.org/3/tutorial/guide.pdf")
