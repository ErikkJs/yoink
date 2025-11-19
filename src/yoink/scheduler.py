"""URL scheduling and deduplication."""

import asyncio
from collections import deque
from typing import Optional
from urllib.parse import urlparse
import structlog

from yoink.filters import CombinedFilter

logger = structlog.get_logger()


class Scheduler:
    """Manages URL queue with deduplication and depth tracking."""

    def __init__(
        self,
        max_depth: int = 1,
        follow_external: bool = False,
        url_filter: Optional[CombinedFilter] = None,
    ):
        self.max_depth = max_depth
        self.follow_external = follow_external
        self.url_filter = url_filter
        self.queue: deque[tuple[str, int]] = deque()  # (url, depth)
        self.visited: set[str] = set()
        self.filtered: set[str] = set()  # Track filtered URLs
        self.start_domain: Optional[str] = None
        self._lock = asyncio.Lock()

    async def add(self, url: str, depth: int = 0):
        """
        Add URL to queue if not already visited.

        Args:
            url: URL to add
            depth: Current depth level
        """
        async with self._lock:
            # Set start domain from first URL
            if self.start_domain is None:
                self.start_domain = urlparse(url).netloc

            # Skip if already visited
            if url in self.visited:
                return

            # Skip if exceeds max depth
            if depth > self.max_depth:
                return

            # Skip if external domain and not following external
            if not self.follow_external:
                if urlparse(url).netloc != self.start_domain:
                    return

            # Apply URL filters
            if self.url_filter and not self.url_filter.should_crawl(url):
                self.filtered.add(url)
                return

            self.visited.add(url)
            self.queue.append((url, depth))
            logger.debug("url_queued", url=url, depth=depth, queue_size=len(self.queue))

    async def get(self) -> Optional[tuple[str, int]]:
        """Get next URL from queue (FIFO)."""
        async with self._lock:
            if self.queue:
                return self.queue.popleft()
            return None

    async def size(self) -> int:
        """Get current queue size."""
        async with self._lock:
            return len(self.queue)

    async def visited_count(self) -> int:
        """Get count of visited URLs."""
        async with self._lock:
            return len(self.visited)

    async def filtered_count(self) -> int:
        """Get count of filtered URLs."""
        async with self._lock:
            return len(self.filtered)

    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self.queue) == 0
