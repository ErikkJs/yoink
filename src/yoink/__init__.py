"""
YOINK - The public data crawler.

Because it's public.
"""

from yoink.checkpoint import CheckpointManager
from yoink.crawler import Crawler
from yoink.fetcher_factory import create_fetcher
from yoink.models import CrawlConfig, Page, WaitStrategy
from yoink.rate_limiter import RateLimiter
from yoink.robots import RobotsChecker
from yoink.storage import CheckpointStorage, LocalFileStorage, S3Storage, StorageFactory

__version__ = "0.1.0"
__all__ = [
    "Crawler",
    "Page",
    "CrawlConfig",
    "WaitStrategy",
    "CheckpointManager",
    "CheckpointStorage",
    "LocalFileStorage",
    "S3Storage",
    "StorageFactory",
    "RateLimiter",
    "RobotsChecker",
    "create_fetcher",
]
