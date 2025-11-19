"""Data models for yoink."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl, Field


class Page(BaseModel):
    """Represents a crawled web page."""

    url: str
    title: Optional[str] = None
    text: Optional[str] = None
    html: Optional[str] = None
    links: list[str] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)
    crawled_at: datetime = Field(default_factory=datetime.utcnow)
    status_code: int = 200
    depth: int = 0

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class CrawlConfig(BaseModel):
    """Configuration for crawler behavior."""

    max_depth: int = Field(default=1, ge=0, description="Maximum crawl depth")
    max_pages: int = Field(default=100, ge=1, description="Maximum pages to crawl")
    max_concurrency: int = Field(default=10, ge=1, le=100, description="Max concurrent requests")
    respect_robots: bool = Field(default=True, description="Respect robots.txt")
    user_agent: str = Field(
        default="yoink/0.3.0 (+https://github.com/ErikkJs/yoink)",
        description="User agent string",
    )
    timeout: int = Field(default=30, ge=1, description="Request timeout in seconds")
    follow_external: bool = Field(default=False, description="Follow links to external domains")
    extract_text: bool = Field(default=True, description="Extract clean text from pages")
    save_html: bool = Field(default=False, description="Save raw HTML")
