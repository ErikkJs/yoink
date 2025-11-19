"""URL filtering utilities."""

import re
from typing import Optional
from fnmatch import fnmatch
from urllib.parse import urlparse
import structlog

logger = structlog.get_logger()


class URLFilter:
    """Filter URLs based on patterns."""

    def __init__(
        self,
        include_patterns: Optional[list[str]] = None,
        exclude_patterns: Optional[list[str]] = None,
        skip_extensions: Optional[list[str]] = None,
    ):
        """
        Initialize URL filter.

        Args:
            include_patterns: List of glob patterns to include (whitelist)
            exclude_patterns: List of glob patterns to exclude (blacklist)
            skip_extensions: List of file extensions to skip (e.g., ['pdf', 'zip'])
        """
        self.include_patterns = include_patterns or []
        self.exclude_patterns = exclude_patterns or []
        self.skip_extensions = [ext.lower().lstrip('.') for ext in (skip_extensions or [])]

    def should_crawl(self, url: str) -> bool:
        """
        Check if URL should be crawled based on filters.

        Args:
            url: URL to check

        Returns:
            True if URL should be crawled, False otherwise
        """
        # Check file extension first (fast check)
        if self.skip_extensions:
            parsed = urlparse(url)
            path = parsed.path.lower()
            for ext in self.skip_extensions:
                if path.endswith(f'.{ext}'):
                    logger.debug("url_filtered_extension", url=url, extension=ext)
                    return False

        # If include patterns exist, URL must match at least one
        if self.include_patterns:
            if not any(self._match_pattern(url, pattern) for pattern in self.include_patterns):
                logger.debug("url_filtered_include", url=url)
                return False

        # If exclude patterns exist, URL must not match any
        if self.exclude_patterns:
            if any(self._match_pattern(url, pattern) for pattern in self.exclude_patterns):
                logger.debug("url_filtered_exclude", url=url)
                return False

        return True

    def _match_pattern(self, url: str, pattern: str) -> bool:
        """
        Match URL against pattern (supports glob and regex).

        Args:
            url: URL to match
            pattern: Pattern to match against (glob or regex)

        Returns:
            True if pattern matches URL
        """
        # Try glob pattern first (simpler and more common)
        if '*' in pattern or '?' in pattern:
            return fnmatch(url, pattern)

        # Try regex if pattern looks like regex
        if pattern.startswith('^') or pattern.endswith('$') or '[' in pattern:
            try:
                return bool(re.match(pattern, url))
            except re.error:
                logger.warning("invalid_regex_pattern", pattern=pattern)
                return False

        # Fall back to substring match
        return pattern in url

    def get_stats(self) -> dict:
        """Get filter statistics."""
        return {
            "include_patterns": len(self.include_patterns),
            "exclude_patterns": len(self.exclude_patterns),
            "skip_extensions": len(self.skip_extensions),
        }


class DomainFilter:
    """Filter URLs based on domain."""

    def __init__(self, allowed_domains: Optional[list[str]] = None):
        """
        Initialize domain filter.

        Args:
            allowed_domains: List of allowed domains (e.g., ['example.com', 'test.com'])
        """
        self.allowed_domains = set(allowed_domains or [])

    def should_crawl(self, url: str) -> bool:
        """
        Check if URL's domain is allowed.

        Args:
            url: URL to check

        Returns:
            True if domain is allowed or no domain filter is set
        """
        if not self.allowed_domains:
            return True

        parsed = urlparse(url)
        domain = parsed.netloc

        # Check exact match
        if domain in self.allowed_domains:
            return True

        # Check subdomain match (e.g., sub.example.com matches example.com)
        for allowed in self.allowed_domains:
            if domain.endswith(f'.{allowed}'):
                return True

        logger.debug("url_filtered_domain", url=url, domain=domain)
        return False


class CombinedFilter:
    """Combines multiple filters."""

    def __init__(
        self,
        url_filter: Optional[URLFilter] = None,
        domain_filter: Optional[DomainFilter] = None,
    ):
        """
        Initialize combined filter.

        Args:
            url_filter: URL pattern filter
            domain_filter: Domain filter
        """
        self.url_filter = url_filter
        self.domain_filter = domain_filter

    def should_crawl(self, url: str) -> bool:
        """
        Check if URL should be crawled.

        Args:
            url: URL to check

        Returns:
            True if URL passes all filters
        """
        if self.domain_filter and not self.domain_filter.should_crawl(url):
            return False

        if self.url_filter and not self.url_filter.should_crawl(url):
            return False

        return True

    @classmethod
    def from_config(
        cls,
        include_patterns: Optional[list[str]] = None,
        exclude_patterns: Optional[list[str]] = None,
        skip_extensions: Optional[list[str]] = None,
        allowed_domains: Optional[list[str]] = None,
    ) -> "CombinedFilter":
        """
        Create combined filter from configuration.

        Args:
            include_patterns: URL patterns to include
            exclude_patterns: URL patterns to exclude
            skip_extensions: File extensions to skip
            allowed_domains: Allowed domains

        Returns:
            CombinedFilter instance
        """
        url_filter = None
        if include_patterns or exclude_patterns or skip_extensions:
            url_filter = URLFilter(
                include_patterns=include_patterns,
                exclude_patterns=exclude_patterns,
                skip_extensions=skip_extensions,
            )

        domain_filter = None
        if allowed_domains:
            domain_filter = DomainFilter(allowed_domains=allowed_domains)

        return cls(url_filter=url_filter, domain_filter=domain_filter)
