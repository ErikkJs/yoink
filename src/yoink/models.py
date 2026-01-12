"""Data models for yoink."""

from datetime import datetime
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class Page(BaseModel):
    """Represents a crawled web page."""

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()},
    )

    url: str
    title: Optional[str] = None
    text: Optional[str] = None
    html: Optional[str] = None
    links: list[str] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)
    crawled_at: datetime = Field(default_factory=datetime.utcnow)
    status_code: int = 200
    depth: int = 0


class WaitStrategy(str, Enum):
    """Wait strategies for Playwright page loading."""

    LOAD = "load"
    DOMCONTENTLOADED = "domcontentloaded"
    NETWORKIDLE = "networkidle"
    COMMIT = "commit"


class CrawlConfig(BaseModel):
    """Configuration for crawler behavior."""

    # Core crawl settings
    max_depth: int = Field(default=1, ge=0, description="Maximum crawl depth")
    max_pages: int = Field(default=100, ge=1, description="Maximum pages to crawl")
    max_concurrency: int = Field(default=10, ge=1, le=100, description="Max concurrent requests")
    user_agent: str = Field(
        default="yoink/0.3.0 (+https://github.com/ErikkJs/yoink)",
        description="User agent string",
    )
    timeout: int = Field(default=30, ge=1, description="Request timeout in seconds")
    follow_external: bool = Field(default=False, description="Follow links to external domains")
    extract_text: bool = Field(default=True, description="Extract clean text from pages")
    save_html: bool = Field(default=False, description="Save raw HTML")

    # robots.txt settings
    respect_robots: bool = Field(default=True, description="Respect robots.txt")

    # Rate limiting settings
    requests_per_second: float = Field(
        default=2.0,
        ge=0.1,
        le=100.0,
        description="Maximum requests per second per domain",
    )
    request_delay: float = Field(
        default=0.0,
        ge=0.0,
        description="Minimum delay between requests in seconds",
    )

    # JavaScript rendering settings (Playwright)
    render_js: bool = Field(
        default=False,
        description="Enable JavaScript rendering via browser",
    )
    headless: bool = Field(
        default=True,
        description="Run browser in headless mode",
    )
    wait_strategy: WaitStrategy = Field(
        default=WaitStrategy.NETWORKIDLE,
        description="Page load wait strategy",
    )
    wait_selector: Optional[str] = Field(
        default=None,
        description="CSS selector to wait for after page load",
    )
    browser_type: Literal["chromium", "firefox", "webkit"] = Field(
        default="chromium",
        description="Browser engine to use",
    )
    browser_pool_size: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of browser contexts to pool",
    )
    screenshot_dir: Optional[str] = Field(
        default=None,
        description="Directory to save debug screenshots",
    )
