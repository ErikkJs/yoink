"""robots.txt parser and checker."""

import asyncio
import re
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional
from urllib.parse import urlparse

import structlog

if TYPE_CHECKING:
    from yoink.fetcher import Fetcher

logger = structlog.get_logger()


@dataclass
class RobotsRule:
    """Represents a single Allow/Disallow rule."""

    path: str
    allowed: bool

    def matches(self, url_path: str) -> bool:
        """
        Check if this rule matches the given URL path.

        Supports:
        - Exact prefix matching
        - * wildcard (matches any sequence)
        - $ end anchor
        """
        pattern = self.path

        # Empty path means allow all
        if not pattern:
            return True

        # Convert robots.txt pattern to regex
        regex_pattern = ""
        i = 0
        while i < len(pattern):
            char = pattern[i]
            if char == "*":
                regex_pattern += ".*"
            elif char == "$" and i == len(pattern) - 1:
                regex_pattern += "$"
            else:
                regex_pattern += re.escape(char)
            i += 1

        # If pattern doesn't end with $, it's a prefix match
        if not pattern.endswith("$"):
            regex_pattern = f"^{regex_pattern}"
        else:
            regex_pattern = f"^{regex_pattern}"

        try:
            return bool(re.match(regex_pattern, url_path))
        except re.error:
            # Invalid regex, fall back to prefix match
            return url_path.startswith(pattern.rstrip("$"))


@dataclass
class RobotsDirectives:
    """Parsed robots.txt directives for a specific user-agent."""

    user_agent: str
    rules: list[RobotsRule] = field(default_factory=list)
    crawl_delay: Optional[float] = None
    sitemaps: list[str] = field(default_factory=list)

    def is_allowed(self, url_path: str) -> bool:
        """
        Check if URL path is allowed by these directives.

        Rules are checked in order; first match wins.
        More specific (longer) paths take precedence.
        """
        if not self.rules:
            return True

        # Sort rules by path length (longer = more specific = higher priority)
        sorted_rules = sorted(self.rules, key=lambda r: len(r.path), reverse=True)

        for rule in sorted_rules:
            if rule.matches(url_path):
                return rule.allowed

        # No matching rule = allowed
        return True


@dataclass
class CachedRobots:
    """Cached robots.txt data with TTL."""

    directives: dict[str, RobotsDirectives]
    fetched_at: float
    ttl: float = 3600.0  # 1 hour default

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return time.monotonic() - self.fetched_at > self.ttl


class RobotsChecker:
    """
    Async robots.txt manager with caching.

    Fetches, parses, and caches robots.txt files per domain.
    Checks URL permissions based on parsed rules.
    """

    def __init__(
        self,
        user_agent: str = "yoink",
        cache_ttl: float = 3600.0,
        respect_robots: bool = True,
    ):
        """
        Initialize robots checker.

        Args:
            user_agent: User agent string for matching robots.txt rules
            cache_ttl: How long to cache robots.txt (seconds, default 1 hour)
            respect_robots: Master toggle for robots.txt checking
        """
        self.user_agent = user_agent
        self.cache_ttl = cache_ttl
        self.respect_robots = respect_robots
        self._cache: dict[str, CachedRobots] = {}
        self._fetcher: Optional["Fetcher"] = None
        self._locks: dict[str, asyncio.Lock] = {}
        self._global_lock = asyncio.Lock()

    def set_fetcher(self, fetcher: "Fetcher") -> None:
        """Set the fetcher to use for HTTP requests."""
        self._fetcher = fetcher

    async def _get_domain_lock(self, domain: str) -> asyncio.Lock:
        """Get or create a lock for a specific domain."""
        async with self._global_lock:
            if domain not in self._locks:
                self._locks[domain] = asyncio.Lock()
            return self._locks[domain]

    async def is_allowed(self, url: str) -> bool:
        """
        Check if URL is allowed by robots.txt.

        Args:
            url: The URL to check

        Returns:
            True if allowed, False if disallowed
        """
        if not self.respect_robots:
            return True

        parsed = urlparse(url)
        domain = parsed.netloc
        path = parsed.path or "/"

        # Get or fetch robots.txt for this domain
        directives = await self._get_directives(domain)
        if directives is None:
            # No robots.txt or error fetching = allow
            return True

        allowed = directives.is_allowed(path)
        if not allowed:
            logger.debug("url_blocked_by_robots", url=url, domain=domain, path=path)
        return allowed

    async def get_crawl_delay(self, domain: str) -> Optional[float]:
        """
        Get Crawl-delay directive for a domain.

        Args:
            domain: The domain to check

        Returns:
            Crawl delay in seconds, or None if not specified
        """
        if not self.respect_robots:
            return None

        directives = await self._get_directives(domain)
        if directives is None:
            return None

        return directives.crawl_delay

    async def _get_directives(self, domain: str) -> Optional[RobotsDirectives]:
        """Get robots directives for domain, fetching if needed."""
        # Check cache first
        if domain in self._cache:
            cached = self._cache[domain]
            if not cached.is_expired():
                return self._get_matching_directives(cached.directives)

        # Fetch with domain-specific lock to prevent duplicate fetches
        lock = await self._get_domain_lock(domain)
        async with lock:
            # Double-check cache after acquiring lock
            if domain in self._cache:
                cached = self._cache[domain]
                if not cached.is_expired():
                    return self._get_matching_directives(cached.directives)

            # Fetch robots.txt
            content = await self._fetch_robots(domain)
            if content is None:
                # Cache the "no robots" result too
                self._cache[domain] = CachedRobots(
                    directives={},
                    fetched_at=time.monotonic(),
                    ttl=self.cache_ttl,
                )
                return None

            # Parse and cache
            directives = self._parse_robots(content)
            self._cache[domain] = CachedRobots(
                directives=directives,
                fetched_at=time.monotonic(),
                ttl=self.cache_ttl,
            )

            return self._get_matching_directives(directives)

    def _get_matching_directives(
        self, directives: dict[str, RobotsDirectives]
    ) -> Optional[RobotsDirectives]:
        """Get directives matching our user agent."""
        if not directives:
            return None

        # Try exact match first (case-insensitive)
        ua_lower = self.user_agent.lower()
        for ua, dirs in directives.items():
            if ua.lower() == ua_lower:
                return dirs

        # Try partial match (our UA contains their UA or vice versa)
        for ua, dirs in directives.items():
            ua_l = ua.lower()
            if ua_l in ua_lower or ua_lower in ua_l:
                return dirs

        # Fall back to wildcard
        if "*" in directives:
            return directives["*"]

        return None

    async def _fetch_robots(self, domain: str) -> Optional[str]:
        """Fetch robots.txt content for a domain."""
        if self._fetcher is None:
            logger.warning("no_fetcher_for_robots", domain=domain)
            return None

        robots_url = f"https://{domain}/robots.txt"

        try:
            content, status = await self._fetcher.fetch(robots_url)

            if status == 404:
                logger.debug("robots_not_found", domain=domain)
                return None

            if status >= 500:
                logger.warning("robots_server_error", domain=domain, status=status)
                return None

            if status >= 400:
                logger.debug("robots_client_error", domain=domain, status=status)
                return None

            logger.info("robots_fetched", domain=domain, size=len(content))
            return content

        except Exception as e:
            logger.warning("robots_fetch_failed", domain=domain, error=str(e))
            return None

    def _parse_robots(self, content: str) -> dict[str, RobotsDirectives]:
        """
        Parse robots.txt content into directives per user-agent.

        Args:
            content: Raw robots.txt content

        Returns:
            Dict mapping user-agent to directives
        """
        directives: dict[str, RobotsDirectives] = {}
        current_agents: list[str] = []
        current_rules: list[RobotsRule] = []
        crawl_delay: Optional[float] = None
        sitemaps: list[str] = []

        for line in content.split("\n"):
            # Remove comments and whitespace
            line = line.split("#")[0].strip()
            if not line:
                continue

            # Split on first colon
            if ":" not in line:
                continue

            field, _, value = line.partition(":")
            field = field.strip().lower()
            value = value.strip()

            if field == "user-agent":
                # Save previous group if exists
                if current_agents and (current_rules or crawl_delay is not None):
                    for agent in current_agents:
                        directives[agent] = RobotsDirectives(
                            user_agent=agent,
                            rules=current_rules.copy(),
                            crawl_delay=crawl_delay,
                            sitemaps=sitemaps.copy(),
                        )
                # Start new group
                current_agents = [value]
                current_rules = []
                crawl_delay = None

            elif field == "disallow":
                if current_agents:
                    current_rules.append(RobotsRule(path=value, allowed=False))

            elif field == "allow":
                if current_agents:
                    current_rules.append(RobotsRule(path=value, allowed=True))

            elif field == "crawl-delay":
                try:
                    crawl_delay = float(value)
                except ValueError:
                    pass

            elif field == "sitemap":
                sitemaps.append(value)

        # Save last group
        if current_agents and (current_rules or crawl_delay is not None):
            for agent in current_agents:
                directives[agent] = RobotsDirectives(
                    user_agent=agent,
                    rules=current_rules,
                    crawl_delay=crawl_delay,
                    sitemaps=sitemaps,
                )

        return directives

    def clear_cache(self) -> None:
        """Clear the robots.txt cache."""
        self._cache.clear()

    def get_cache_stats(self) -> dict[str, int]:
        """Get cache statistics."""
        expired = sum(1 for c in self._cache.values() if c.is_expired())
        return {
            "total": len(self._cache),
            "expired": expired,
            "valid": len(self._cache) - expired,
        }
