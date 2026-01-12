"""Tests for robots.txt parser and checker."""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

import pytest

from yoink.robots import (
    RobotsRule,
    RobotsDirectives,
    CachedRobots,
    RobotsChecker,
)


class TestRobotsRule:
    """Test RobotsRule matching logic."""

    def test_prefix_match_basic(self):
        """Test prefix path matching (robots.txt default behavior)."""
        rule = RobotsRule(path="/admin", allowed=False)
        assert rule.matches("/admin")
        assert rule.matches("/admin/users")
        # Note: robots.txt uses prefix matching, so /admin matches /administrator
        assert rule.matches("/administrator")

    def test_prefix_match(self):
        """Test prefix path matching."""
        rule = RobotsRule(path="/api/", allowed=False)
        assert rule.matches("/api/")
        assert rule.matches("/api/v1/users")
        assert not rule.matches("/api")
        assert not rule.matches("/apiary")

    def test_wildcard_match(self):
        """Test * wildcard matching."""
        rule = RobotsRule(path="/*/private", allowed=False)
        assert rule.matches("/users/private")
        assert rule.matches("/a/private")
        assert rule.matches("/foo/bar/private")
        assert not rule.matches("/private")

    def test_wildcard_extension(self):
        """Test wildcard for file extensions."""
        rule = RobotsRule(path="/*.pdf", allowed=False)
        assert rule.matches("/document.pdf")
        assert rule.matches("/files/report.pdf")
        assert not rule.matches("/pdf")
        # Without $ anchor, this is prefix match so .pdf.txt also matches
        assert rule.matches("/document.pdf.txt")

    def test_wildcard_extension_exact(self):
        """Test wildcard with $ anchor for exact extension match."""
        rule = RobotsRule(path="/*.pdf$", allowed=False)
        assert rule.matches("/document.pdf")
        assert rule.matches("/files/report.pdf")
        assert not rule.matches("/pdf")
        assert not rule.matches("/document.pdf.txt")

    def test_end_anchor(self):
        """Test $ end anchor matching."""
        rule = RobotsRule(path="/page$", allowed=False)
        assert rule.matches("/page")
        assert not rule.matches("/page/")
        assert not rule.matches("/pages")

    def test_combined_wildcard_and_anchor(self):
        """Test combined * and $ patterns."""
        rule = RobotsRule(path="/*.pdf$", allowed=False)
        assert rule.matches("/doc.pdf")
        assert rule.matches("/path/file.pdf")
        assert not rule.matches("/doc.pdf/view")

    def test_empty_path(self):
        """Test empty path matches everything."""
        rule = RobotsRule(path="", allowed=True)
        assert rule.matches("/anything")
        assert rule.matches("/")

    def test_root_path(self):
        """Test root path matching."""
        rule = RobotsRule(path="/", allowed=False)
        assert rule.matches("/")
        assert rule.matches("/anything")


class TestRobotsDirectives:
    """Test RobotsDirectives logic."""

    def test_empty_rules_allows_all(self):
        """Test that no rules means everything allowed."""
        directives = RobotsDirectives(user_agent="*", rules=[])
        assert directives.is_allowed("/anything")
        assert directives.is_allowed("/admin")

    def test_single_disallow(self):
        """Test single disallow rule."""
        directives = RobotsDirectives(
            user_agent="*",
            rules=[RobotsRule(path="/private", allowed=False)],
        )
        assert not directives.is_allowed("/private")
        assert not directives.is_allowed("/private/data")
        assert directives.is_allowed("/public")

    def test_allow_overrides_disallow(self):
        """Test that more specific allow overrides disallow."""
        directives = RobotsDirectives(
            user_agent="*",
            rules=[
                RobotsRule(path="/admin", allowed=False),
                RobotsRule(path="/admin/public", allowed=True),
            ],
        )
        assert not directives.is_allowed("/admin")
        assert not directives.is_allowed("/admin/users")
        # More specific path takes precedence
        assert directives.is_allowed("/admin/public")
        assert directives.is_allowed("/admin/public/data")

    def test_longer_path_wins(self):
        """Test that longer (more specific) paths take precedence."""
        directives = RobotsDirectives(
            user_agent="*",
            rules=[
                RobotsRule(path="/a", allowed=False),
                RobotsRule(path="/a/b", allowed=True),
                RobotsRule(path="/a/b/c", allowed=False),
            ],
        )
        assert not directives.is_allowed("/a")
        assert directives.is_allowed("/a/b")
        assert not directives.is_allowed("/a/b/c")

    def test_crawl_delay(self):
        """Test crawl delay is stored."""
        directives = RobotsDirectives(
            user_agent="*",
            crawl_delay=2.5,
        )
        assert directives.crawl_delay == 2.5


class TestCachedRobots:
    """Test CachedRobots caching logic."""

    def test_not_expired(self):
        """Test cache is valid when not expired."""
        cached = CachedRobots(
            directives={},
            fetched_at=time.monotonic(),
            ttl=3600.0,
        )
        assert not cached.is_expired()

    def test_expired(self):
        """Test cache is expired after TTL."""
        cached = CachedRobots(
            directives={},
            fetched_at=time.monotonic() - 3601.0,
            ttl=3600.0,
        )
        assert cached.is_expired()

    def test_short_ttl(self):
        """Test short TTL expiration."""
        cached = CachedRobots(
            directives={},
            fetched_at=time.monotonic() - 2.0,
            ttl=1.0,
        )
        assert cached.is_expired()


class TestRobotsCheckerParsing:
    """Test RobotsChecker parsing logic."""

    def test_parse_basic_disallow(self):
        """Test parsing basic Disallow rule."""
        checker = RobotsChecker()
        content = """
User-agent: *
Disallow: /admin
"""
        directives = checker._parse_robots(content)
        assert "*" in directives
        assert len(directives["*"].rules) == 1
        assert not directives["*"].rules[0].allowed

    def test_parse_allow_and_disallow(self):
        """Test parsing Allow and Disallow rules."""
        checker = RobotsChecker()
        content = """
User-agent: *
Disallow: /private
Allow: /private/public
"""
        directives = checker._parse_robots(content)
        assert len(directives["*"].rules) == 2

    def test_parse_multiple_user_agents(self):
        """Test parsing rules for different user-agents."""
        checker = RobotsChecker()
        content = """
User-agent: Googlebot
Disallow: /google-only

User-agent: *
Disallow: /private
"""
        directives = checker._parse_robots(content)
        assert "Googlebot" in directives
        assert "*" in directives
        assert len(directives["Googlebot"].rules) == 1
        assert len(directives["*"].rules) == 1

    def test_parse_crawl_delay(self):
        """Test parsing Crawl-delay directive."""
        checker = RobotsChecker()
        content = """
User-agent: *
Crawl-delay: 2.5
Disallow: /admin
"""
        directives = checker._parse_robots(content)
        assert directives["*"].crawl_delay == 2.5

    def test_parse_sitemap(self):
        """Test parsing Sitemap directive."""
        checker = RobotsChecker()
        content = """
User-agent: *
Disallow:

Sitemap: https://example.com/sitemap.xml
"""
        directives = checker._parse_robots(content)
        # Sitemaps are collected for all agents
        assert "https://example.com/sitemap.xml" in directives["*"].sitemaps

    def test_parse_comments(self):
        """Test that comments are ignored."""
        checker = RobotsChecker()
        content = """
# This is a comment
User-agent: *
Disallow: /admin  # inline comment
"""
        directives = checker._parse_robots(content)
        assert "*" in directives
        assert len(directives["*"].rules) == 1
        assert directives["*"].rules[0].path == "/admin"

    def test_parse_empty_content(self):
        """Test parsing empty robots.txt."""
        checker = RobotsChecker()
        directives = checker._parse_robots("")
        assert directives == {}

    def test_parse_invalid_content(self):
        """Test parsing invalid robots.txt content."""
        checker = RobotsChecker()
        content = """
This is not valid robots.txt
Just random text
"""
        directives = checker._parse_robots(content)
        assert directives == {}


class TestRobotsCheckerMatching:
    """Test RobotsChecker user-agent matching."""

    def test_exact_user_agent_match(self):
        """Test exact user-agent matching."""
        checker = RobotsChecker(user_agent="yoink")
        directives = {
            "yoink": RobotsDirectives(
                user_agent="yoink",
                rules=[RobotsRule(path="/private", allowed=False)],
            ),
            "*": RobotsDirectives(
                user_agent="*",
                rules=[RobotsRule(path="/", allowed=False)],
            ),
        }
        matched = checker._get_matching_directives(directives)
        assert matched is not None
        assert matched.user_agent == "yoink"

    def test_partial_user_agent_match(self):
        """Test partial user-agent matching."""
        checker = RobotsChecker(user_agent="yoink/1.0 (+https://example.com)")
        directives = {
            "yoink": RobotsDirectives(
                user_agent="yoink",
                rules=[RobotsRule(path="/private", allowed=False)],
            ),
        }
        matched = checker._get_matching_directives(directives)
        assert matched is not None
        assert matched.user_agent == "yoink"

    def test_wildcard_fallback(self):
        """Test fallback to wildcard user-agent."""
        checker = RobotsChecker(user_agent="unknown-bot")
        directives = {
            "Googlebot": RobotsDirectives(
                user_agent="Googlebot",
                rules=[RobotsRule(path="/google", allowed=False)],
            ),
            "*": RobotsDirectives(
                user_agent="*",
                rules=[RobotsRule(path="/all", allowed=False)],
            ),
        }
        matched = checker._get_matching_directives(directives)
        assert matched is not None
        assert matched.user_agent == "*"

    def test_no_matching_directives(self):
        """Test when no matching directives found."""
        checker = RobotsChecker(user_agent="unknown-bot")
        directives = {
            "Googlebot": RobotsDirectives(
                user_agent="Googlebot",
                rules=[RobotsRule(path="/google", allowed=False)],
            ),
        }
        matched = checker._get_matching_directives(directives)
        assert matched is None


@pytest.mark.asyncio
class TestRobotsCheckerAsync:
    """Test RobotsChecker async methods."""

    async def test_is_allowed_when_disabled(self):
        """Test that everything is allowed when respect_robots=False."""
        checker = RobotsChecker(respect_robots=False)
        assert await checker.is_allowed("https://example.com/private")

    async def test_is_allowed_no_robots(self):
        """Test behavior when robots.txt is missing (404)."""
        checker = RobotsChecker()

        # Mock fetcher that returns 404
        mock_fetcher = AsyncMock()
        mock_fetcher.fetch = AsyncMock(return_value=("", 404))
        checker.set_fetcher(mock_fetcher)

        # Should allow when no robots.txt
        assert await checker.is_allowed("https://example.com/anything")

    async def test_is_allowed_blocked_path(self):
        """Test blocking disallowed path."""
        checker = RobotsChecker(user_agent="yoink")

        # Mock fetcher that returns robots.txt
        robots_content = """
User-agent: *
Disallow: /private
"""
        mock_fetcher = AsyncMock()
        mock_fetcher.fetch = AsyncMock(return_value=(robots_content, 200))
        checker.set_fetcher(mock_fetcher)

        assert not await checker.is_allowed("https://example.com/private")
        assert not await checker.is_allowed("https://example.com/private/data")
        assert await checker.is_allowed("https://example.com/public")

    async def test_caching(self):
        """Test that robots.txt is cached per domain."""
        checker = RobotsChecker()

        robots_content = """
User-agent: *
Disallow: /admin
"""
        mock_fetcher = AsyncMock()
        mock_fetcher.fetch = AsyncMock(return_value=(robots_content, 200))
        checker.set_fetcher(mock_fetcher)

        # First request
        await checker.is_allowed("https://example.com/page1")
        # Second request (should use cache)
        await checker.is_allowed("https://example.com/page2")

        # Should only fetch once
        assert mock_fetcher.fetch.call_count == 1

    async def test_get_crawl_delay(self):
        """Test retrieving Crawl-delay for domain."""
        checker = RobotsChecker(user_agent="yoink")

        robots_content = """
User-agent: *
Crawl-delay: 5
Disallow: /admin
"""
        mock_fetcher = AsyncMock()
        mock_fetcher.fetch = AsyncMock(return_value=(robots_content, 200))
        checker.set_fetcher(mock_fetcher)

        delay = await checker.get_crawl_delay("example.com")
        assert delay == 5.0

    async def test_get_crawl_delay_disabled(self):
        """Test crawl delay returns None when disabled."""
        checker = RobotsChecker(respect_robots=False)
        delay = await checker.get_crawl_delay("example.com")
        assert delay is None

    async def test_get_crawl_delay_no_directive(self):
        """Test crawl delay returns None when not specified."""
        checker = RobotsChecker()

        robots_content = """
User-agent: *
Disallow: /admin
"""
        mock_fetcher = AsyncMock()
        mock_fetcher.fetch = AsyncMock(return_value=(robots_content, 200))
        checker.set_fetcher(mock_fetcher)

        delay = await checker.get_crawl_delay("example.com")
        assert delay is None

    async def test_server_error_allows_access(self):
        """Test that server errors allow access."""
        checker = RobotsChecker()

        mock_fetcher = AsyncMock()
        mock_fetcher.fetch = AsyncMock(return_value=("", 500))
        checker.set_fetcher(mock_fetcher)

        assert await checker.is_allowed("https://example.com/anything")

    async def test_fetch_error_allows_access(self):
        """Test that fetch errors allow access."""
        checker = RobotsChecker()

        mock_fetcher = AsyncMock()
        mock_fetcher.fetch = AsyncMock(side_effect=Exception("Network error"))
        checker.set_fetcher(mock_fetcher)

        assert await checker.is_allowed("https://example.com/anything")

    async def test_no_fetcher_allows_access(self):
        """Test that no fetcher configured allows access."""
        checker = RobotsChecker()
        # Don't set fetcher
        assert await checker.is_allowed("https://example.com/anything")

    async def test_different_domains_separate_cache(self):
        """Test that different domains have separate caches."""
        checker = RobotsChecker()

        mock_fetcher = AsyncMock()
        mock_fetcher.fetch = AsyncMock(
            side_effect=[
                ("User-agent: *\nDisallow: /a", 200),
                ("User-agent: *\nDisallow: /b", 200),
            ]
        )
        checker.set_fetcher(mock_fetcher)

        await checker.is_allowed("https://a.com/test")
        await checker.is_allowed("https://b.com/test")

        assert mock_fetcher.fetch.call_count == 2


class TestRobotsCheckerCacheManagement:
    """Test cache management methods."""

    def test_clear_cache(self):
        """Test clearing the cache."""
        checker = RobotsChecker()
        checker._cache["example.com"] = CachedRobots(
            directives={},
            fetched_at=time.monotonic(),
        )

        checker.clear_cache()
        assert len(checker._cache) == 0

    def test_get_cache_stats(self):
        """Test getting cache statistics."""
        checker = RobotsChecker()

        # Add valid and expired entries
        checker._cache["valid.com"] = CachedRobots(
            directives={},
            fetched_at=time.monotonic(),
        )
        checker._cache["expired.com"] = CachedRobots(
            directives={},
            fetched_at=time.monotonic() - 7200,  # 2 hours ago
            ttl=3600,
        )

        stats = checker.get_cache_stats()
        assert stats["total"] == 2
        assert stats["valid"] == 1
        assert stats["expired"] == 1
