"""HTML parsing and URL extraction."""

from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import structlog

logger = structlog.get_logger()


class Parser:
    """HTML parser for extracting links and metadata."""

    def parse(self, html: str, base_url: str) -> dict:
        """
        Parse HTML and extract links, title, and metadata.

        Args:
            html: Raw HTML content
            base_url: Base URL for resolving relative links

        Returns:
            Dict with title, links, and metadata
        """
        soup = BeautifulSoup(html, "lxml")

        # Extract title
        title = None
        if soup.title:
            title = soup.title.string.strip() if soup.title.string else None

        # Extract links
        links = self._extract_links(soup, base_url)

        # Extract metadata
        metadata = self._extract_metadata(soup)

        return {"title": title, "links": links, "metadata": metadata}

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> list[str]:
        """Extract and normalize all links from page."""
        links = []
        seen = set()

        for anchor in soup.find_all("a", href=True):
            href = anchor["href"]

            # Resolve relative URLs
            absolute_url = urljoin(base_url, href)

            # Remove fragments
            absolute_url = absolute_url.split("#")[0]

            # Skip non-http(s) URLs
            parsed = urlparse(absolute_url)
            if parsed.scheme not in ("http", "https"):
                continue

            # Deduplicate
            if absolute_url not in seen:
                seen.add(absolute_url)
                links.append(absolute_url)

        return links

    def _extract_metadata(self, soup: BeautifulSoup) -> dict[str, str]:
        """Extract metadata from page (OpenGraph, meta tags, etc)."""
        metadata = {}

        # OpenGraph tags
        for meta in soup.find_all("meta", property=True):
            prop = meta.get("property", "")
            if prop.startswith("og:"):
                content = meta.get("content")
                if content:
                    metadata[prop] = content

        # Standard meta tags
        for meta in soup.find_all("meta", attrs={"name": True}):
            name = meta.get("name", "")
            content = meta.get("content")
            if content and name in ("description", "author", "keywords", "date"):
                metadata[name] = content

        return metadata

    def is_same_domain(self, url1: str, url2: str) -> bool:
        """Check if two URLs belong to the same domain."""
        domain1 = urlparse(url1).netloc
        domain2 = urlparse(url2).netloc
        return domain1 == domain2
