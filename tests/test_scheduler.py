"""Tests for URL scheduler."""

import pytest
from yoink.scheduler import Scheduler


@pytest.mark.asyncio
class TestScheduler:
    """Test URL scheduling and deduplication."""

    async def test_add_and_get(self):
        """Test adding and retrieving URLs."""
        scheduler = Scheduler()

        await scheduler.add("https://example.com", depth=0)
        url, depth = await scheduler.get()

        assert url == "https://example.com"
        assert depth == 0

    async def test_deduplication(self):
        """Test URL deduplication."""
        scheduler = Scheduler()

        await scheduler.add("https://example.com", depth=0)
        await scheduler.add("https://example.com", depth=0)  # Duplicate

        size = await scheduler.size()
        assert size == 1  # Only one URL in queue

    async def test_depth_limit(self):
        """Test max depth enforcement."""
        scheduler = Scheduler(max_depth=2)

        await scheduler.add("https://example.com", depth=0)
        await scheduler.add("https://example.com/page1", depth=2)
        await scheduler.add("https://example.com/page2", depth=3)  # Too deep

        size = await scheduler.size()
        visited = await scheduler.visited_count()

        assert size == 2  # Third URL rejected
        assert visited == 2

    async def test_external_domain_filtering(self):
        """Test external domain filtering."""
        scheduler = Scheduler(follow_external=False)

        await scheduler.add("https://example.com", depth=0)
        await scheduler.add("https://example.com/page", depth=1)
        await scheduler.add("https://external.com", depth=1)  # External

        size = await scheduler.size()
        assert size == 2  # External URL rejected

    async def test_follow_external(self):
        """Test following external links when enabled."""
        scheduler = Scheduler(follow_external=True)

        await scheduler.add("https://example.com", depth=0)
        await scheduler.add("https://external.com", depth=1)

        size = await scheduler.size()
        assert size == 2  # External URL accepted

    async def test_empty_queue(self):
        """Test getting from empty queue."""
        scheduler = Scheduler()
        result = await scheduler.get()

        assert result is None
        assert scheduler.is_empty()
