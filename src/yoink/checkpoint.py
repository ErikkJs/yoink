"""Checkpoint management for resumable crawls."""

import json
from datetime import datetime
from typing import Optional
from pathlib import Path
import structlog

from yoink.models import Page, CrawlConfig
from yoink.storage import CheckpointStorage, StorageFactory

logger = structlog.get_logger()


class CheckpointManager:
    """Manages checkpoint state for resumable crawls."""

    def __init__(
        self,
        storage: CheckpointStorage,
        flush_interval: int = 10,
    ):
        """
        Initialize checkpoint manager.

        Args:
            storage: Storage backend for checkpoint
            flush_interval: Number of pages between flushes (default: 10)
        """
        self.storage = storage
        self.flush_interval = flush_interval
        self._page_count = 0
        logger.info("checkpoint_manager_init", flush_interval=flush_interval)

    @classmethod
    def from_uri(cls, uri: str, flush_interval: int = 10) -> "CheckpointManager":
        """
        Create checkpoint manager from URI.

        Args:
            uri: Storage URI (file path, s3://, etc.)
            flush_interval: Number of pages between flushes

        Returns:
            CheckpointManager instance
        """
        storage = StorageFactory.from_uri(uri)
        return cls(storage, flush_interval)

    async def write_metadata(self, start_url: str, config: CrawlConfig) -> None:
        """
        Write crawl metadata to checkpoint.

        Args:
            start_url: Starting URL for crawl
            config: Crawl configuration
        """
        metadata = {
            "type": "metadata",
            "start_url": start_url,
            "config": config.model_dump(),
            "started_at": datetime.utcnow().isoformat(),
        }

        await self.storage.write(json.dumps(metadata) + "\n")
        await self.storage.flush()
        logger.info("checkpoint_metadata_written", start_url=start_url)

    async def write_page(self, page: Page) -> None:
        """
        Write page to checkpoint.

        Args:
            page: Page to write
        """
        page_data = {
            "type": "page",
            **page.model_dump(mode="json"),
        }

        await self.storage.write(json.dumps(page_data) + "\n")
        self._page_count += 1

        # Flush periodically
        if self._page_count % self.flush_interval == 0:
            await self.storage.flush()
            logger.info("checkpoint_flushed", pages=self._page_count)

    async def write_state(
        self,
        visited: set[str],
        queue: list[tuple[str, int]],
        filtered: set[str],
    ) -> None:
        """
        Write scheduler state to checkpoint.

        Args:
            visited: Set of visited URLs
            queue: Current URL queue with depths
            filtered: Set of filtered URLs
        """
        state = {
            "type": "state",
            "visited": list(visited),
            "queue": queue,
            "filtered": list(filtered),
            "saved_at": datetime.utcnow().isoformat(),
        }

        await self.storage.write(json.dumps(state) + "\n")
        await self.storage.flush()
        logger.info(
            "checkpoint_state_written",
            visited=len(visited),
            queue=len(queue),
            filtered=len(filtered),
        )

    async def load(self) -> dict:
        """
        Load checkpoint data.

        Returns:
            Dictionary with:
                - metadata: Crawl metadata
                - pages: List of crawled pages
                - state: Latest scheduler state
        """
        if not await self.storage.exists():
            logger.warning("checkpoint_not_found")
            return {
                "metadata": None,
                "pages": [],
                "state": None,
            }

        metadata = None
        pages = []
        state = None

        async for line in self.storage.read():
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
                data_type = data.get("type")

                if data_type == "metadata":
                    metadata = data
                elif data_type == "page":
                    # Remove 'type' field before creating Page
                    page_data = {k: v for k, v in data.items() if k != "type"}
                    pages.append(Page(**page_data))
                elif data_type == "state":
                    # Keep latest state (overwrite previous)
                    state = data

            except json.JSONDecodeError as e:
                logger.error("checkpoint_load_error", error=str(e), line=line[:100])
                continue
            except Exception as e:
                logger.error("checkpoint_parse_error", error=str(e))
                continue

        logger.info(
            "checkpoint_loaded",
            pages=len(pages),
            has_metadata=metadata is not None,
            has_state=state is not None,
        )

        return {
            "metadata": metadata,
            "pages": pages,
            "state": state,
        }

    async def close(self) -> None:
        """Close checkpoint and ensure all data is persisted."""
        await self.storage.flush()
        await self.storage.close()
        logger.info("checkpoint_closed", total_pages=self._page_count)
