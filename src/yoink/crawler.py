"""Core crawler engine."""

import asyncio
from typing import Optional

import structlog
from tqdm.asyncio import tqdm

from typing import Union

from yoink.checkpoint import CheckpointManager
from yoink.extractor import Extractor
from yoink.fetcher import Fetcher
from yoink.fetcher_factory import create_fetcher
from yoink.filters import CombinedFilter
from yoink.models import CrawlConfig, Page
from yoink.parser import Parser
from yoink.playwright_fetcher import PlaywrightFetcher
from yoink.rate_limiter import RateLimiter
from yoink.robots import RobotsChecker
from yoink.scheduler import Scheduler

# Type alias for both fetcher types
FetcherType = Union[Fetcher, PlaywrightFetcher]

logger = structlog.get_logger()


class Crawler:
    """Main async web crawler."""

    def __init__(
        self,
        config: Optional[CrawlConfig] = None,
        url_filter: Optional[CombinedFilter] = None,
        checkpoint_manager: Optional[CheckpointManager] = None,
    ):
        """
        Initialize crawler with configuration.

        Args:
            config: Crawler configuration, uses defaults if None
            url_filter: Optional URL filter for pattern matching
            checkpoint_manager: Optional checkpoint manager for resumable crawls
        """
        self.config = config or CrawlConfig()
        self.parser = Parser()
        self.extractor = Extractor()

        # Create rate limiter
        self.rate_limiter = RateLimiter(
            requests_per_second=self.config.requests_per_second,
            min_delay=self.config.request_delay,
        )

        # Create robots checker if enabled
        self.robots_checker: Optional[RobotsChecker] = None
        if self.config.respect_robots:
            self.robots_checker = RobotsChecker(
                user_agent=self.config.user_agent,
                respect_robots=True,
            )

        # Create scheduler with robots checker
        self.scheduler = Scheduler(
            max_depth=self.config.max_depth,
            follow_external=self.config.follow_external,
            url_filter=url_filter,
            robots_checker=self.robots_checker,
        )

        self.pages: list[Page] = []
        self.checkpoint_manager = checkpoint_manager

    async def crawl(self, start_url: str, resume: bool = False) -> list[Page]:
        """
        Crawl website starting from given URL.

        Args:
            start_url: URL to start crawling from
            resume: Whether to resume from checkpoint

        Returns:
            List of crawled pages
        """
        logger.info(
            "crawl_started",
            url=start_url,
            max_depth=self.config.max_depth,
            max_pages=self.config.max_pages,
            resume=resume,
        )

        # Create fetcher context with rate limiting
        fetcher = create_fetcher(
            self.config,
            rate_limiter=self.rate_limiter,
            robots_checker=self.robots_checker,
        )
        async with fetcher:
            # Set fetcher for robots checker BEFORE adding URLs
            # (robots.txt needs to be fetched to check if URL is allowed)
            if self.robots_checker:
                self.robots_checker.set_fetcher(fetcher)

            # Resume from checkpoint if requested
            if resume and self.checkpoint_manager:
                await self._resume_from_checkpoint(start_url)
            else:
                # Write initial metadata if checkpointing enabled
                if self.checkpoint_manager:
                    await self.checkpoint_manager.write_metadata(start_url, self.config)

                # Initialize queue with start URL
                await self.scheduler.add(start_url, depth=0)

            # Create worker tasks
            workers = [
                asyncio.create_task(self._worker(fetcher, worker_id))
                for worker_id in range(self.config.max_concurrency)
            ]

            # Wait for all workers to complete
            await asyncio.gather(*workers)

        # Save final state if checkpointing
        if self.checkpoint_manager:
            await self._save_checkpoint_state()
            await self.checkpoint_manager.close()

        logger.info(
            "crawl_completed",
            pages_crawled=len(self.pages),
            urls_visited=await self.scheduler.visited_count(),
        )

        return self.pages

    async def _worker(self, fetcher: FetcherType, worker_id: int):
        """
        Worker coroutine that processes URLs from queue.

        Args:
            fetcher: HTTP fetcher instance
            worker_id: Worker identifier for logging
        """
        while True:
            # Check if we've hit max pages limit
            if len(self.pages) >= self.config.max_pages:
                break

            # Get next URL from queue
            item = await self.scheduler.get()
            if item is None:
                # Queue is empty, check if other workers are still working
                await asyncio.sleep(0.1)
                if self.scheduler.is_empty() and len(self.pages) > 0:
                    break
                continue

            url, depth = item

            try:
                # Fetch page
                html, status_code = await fetcher.fetch(url)

                # Parse HTML
                parsed = self.parser.parse(html, url)

                # Extract text content if configured
                text = None
                if self.config.extract_text:
                    text = self.extractor.extract(html, url)

                # Create page object
                page = Page(
                    url=url,
                    title=parsed["title"],
                    text=text,
                    html=html if self.config.save_html else None,
                    links=parsed["links"],
                    metadata=parsed["metadata"],
                    status_code=status_code,
                    depth=depth,
                )

                self.pages.append(page)

                # Write to checkpoint if enabled
                if self.checkpoint_manager:
                    await self.checkpoint_manager.write_page(page)

                logger.info(
                    "page_crawled",
                    url=url,
                    depth=depth,
                    links=len(page.links),
                    worker=worker_id,
                    total_pages=len(self.pages),
                )

                # Add discovered links to queue
                for link in parsed["links"]:
                    await self.scheduler.add(link, depth=depth + 1)

            except Exception as e:
                logger.error(
                    "crawl_error",
                    url=url,
                    error=str(e),
                    worker=worker_id,
                )

    async def crawl_with_progress(self, start_url: str, resume: bool = False) -> list[Page]:
        """
        Crawl with progress bar (for CLI use).

        Args:
            start_url: URL to start crawling from
            resume: Whether to resume from checkpoint

        Returns:
            List of crawled pages
        """
        logger.info("crawl_started", url=start_url, resume=resume)

        fetcher = create_fetcher(
            self.config,
            rate_limiter=self.rate_limiter,
            robots_checker=self.robots_checker,
        )
        async with fetcher:
            # Set fetcher for robots checker BEFORE adding URLs
            if self.robots_checker:
                self.robots_checker.set_fetcher(fetcher)

            # Resume from checkpoint if requested
            if resume and self.checkpoint_manager:
                await self._resume_from_checkpoint(start_url)
            else:
                # Write initial metadata if checkpointing enabled
                if self.checkpoint_manager:
                    await self.checkpoint_manager.write_metadata(start_url, self.config)

                await self.scheduler.add(start_url, depth=0)

            with tqdm(
                total=self.config.max_pages,
                desc="Yoinking pages",
                unit="page",
            ) as pbar:
                workers = [
                    asyncio.create_task(self._worker_with_progress(fetcher, worker_id, pbar))
                    for worker_id in range(self.config.max_concurrency)
                ]

                await asyncio.gather(*workers)

        # Save final state if checkpointing
        if self.checkpoint_manager:
            await self._save_checkpoint_state()
            await self.checkpoint_manager.close()

        logger.info("crawl_completed", pages=len(self.pages))
        return self.pages

    async def _worker_with_progress(self, fetcher: FetcherType, worker_id: int, pbar):
        """Worker with progress bar updates."""
        while True:
            if len(self.pages) >= self.config.max_pages:
                break

            item = await self.scheduler.get()
            if item is None:
                await asyncio.sleep(0.1)
                if self.scheduler.is_empty() and len(self.pages) > 0:
                    break
                continue

            url, depth = item

            try:
                html, status_code = await fetcher.fetch(url)
                parsed = self.parser.parse(html, url)

                text = None
                if self.config.extract_text:
                    text = self.extractor.extract(html, url)

                page = Page(
                    url=url,
                    title=parsed["title"],
                    text=text,
                    html=html if self.config.save_html else None,
                    links=parsed["links"],
                    metadata=parsed["metadata"],
                    status_code=status_code,
                    depth=depth,
                )

                self.pages.append(page)

                # Write to checkpoint if enabled
                if self.checkpoint_manager:
                    await self.checkpoint_manager.write_page(page)

                pbar.update(1)
                pbar.set_postfix({"depth": depth, "queue": await self.scheduler.size()})

                for link in parsed["links"]:
                    await self.scheduler.add(link, depth=depth + 1)

            except Exception as e:
                logger.error("crawl_error", url=url, error=str(e))

    async def _resume_from_checkpoint(self, start_url: str) -> None:
        """
        Resume crawl from checkpoint.

        Args:
            start_url: Starting URL (used for validation)
        """
        logger.info("resuming_from_checkpoint")

        checkpoint_data = await self.checkpoint_manager.load()

        # Validate metadata if present
        metadata = checkpoint_data.get("metadata")
        if metadata and metadata.get("start_url") != start_url:
            logger.warning(
                "checkpoint_url_mismatch",
                checkpoint_url=metadata.get("start_url"),
                provided_url=start_url,
            )

        # Restore pages
        self.pages = checkpoint_data.get("pages", [])
        logger.info("checkpoint_pages_restored", count=len(self.pages))

        # Restore scheduler state if available
        state = checkpoint_data.get("state")
        if state:
            # Restore visited URLs
            for url in state.get("visited", []):
                self.scheduler.visited.add(url)

            # Restore filtered URLs
            for url in state.get("filtered", []):
                self.scheduler.filtered.add(url)

            # Restore queue
            for url, depth in state.get("queue", []):
                self.scheduler.queue.append((url, depth))

            # Restore start domain
            if self.scheduler.queue or self.scheduler.visited:
                from urllib.parse import urlparse

                first_url = (
                    list(self.scheduler.visited)[0]
                    if self.scheduler.visited
                    else self.scheduler.queue[0][0]
                )
                self.scheduler.start_domain = urlparse(first_url).netloc

            logger.info(
                "checkpoint_state_restored",
                visited=len(self.scheduler.visited),
                queue=len(self.scheduler.queue),
                filtered=len(self.scheduler.filtered),
            )
        else:
            # No state saved, start fresh from start_url
            logger.warning("no_checkpoint_state_found")
            await self.scheduler.add(start_url, depth=0)

    async def _save_checkpoint_state(self) -> None:
        """Save current scheduler state to checkpoint."""
        if not self.checkpoint_manager:
            return

        await self.checkpoint_manager.write_state(
            visited=self.scheduler.visited,
            queue=list(self.scheduler.queue),
            filtered=self.scheduler.filtered,
        )
