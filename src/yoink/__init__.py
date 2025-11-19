"""
YOINK - The public data crawler.

Because it's public.
"""

from yoink.crawler import Crawler
from yoink.models import Page, CrawlConfig
from yoink.checkpoint import CheckpointManager
from yoink.storage import CheckpointStorage, LocalFileStorage, S3Storage, StorageFactory

__version__ = "0.1.0"
__all__ = [
    "Crawler",
    "Page",
    "CrawlConfig",
    "CheckpointManager",
    "CheckpointStorage",
    "LocalFileStorage",
    "S3Storage",
    "StorageFactory",
]
