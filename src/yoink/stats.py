"""Statistics and analysis for crawled data."""

import json
from pathlib import Path
from typing import Any
from collections import Counter
from urllib.parse import urlparse
import structlog

from yoink.models import Page

logger = structlog.get_logger()


class CrawlStats:
    """Analyzes and computes statistics for crawled data."""

    def __init__(self, pages: list[Page]):
        """
        Initialize stats analyzer.

        Args:
            pages: List of crawled pages to analyze
        """
        self.pages = pages
        self._stats_cache: dict[str, Any] = {}

    @classmethod
    def from_file(cls, file_path: Path) -> "CrawlStats":
        """
        Load pages from file and create stats.

        Args:
            file_path: Path to JSONL or JSON file

        Returns:
            CrawlStats instance
        """
        pages = []
        suffix = file_path.suffix.lower()

        if suffix == ".jsonl":
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    data = json.loads(line.strip())
                    pages.append(Page(**data))

        elif suffix == ".json":
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                pages = [Page(**item) for item in data]

        else:
            raise ValueError(f"Unsupported file format: {suffix}")

        logger.info("loaded_pages", path=str(file_path), count=len(pages))
        return cls(pages)

    def compute(self) -> dict[str, Any]:
        """
        Compute all statistics.

        Returns:
            Dictionary with comprehensive stats
        """
        if self._stats_cache:
            return self._stats_cache

        total_pages = len(self.pages)
        if total_pages == 0:
            return {"total_pages": 0}

        # Basic counts
        total_links = sum(len(p.links) for p in self.pages)
        total_text_size = sum(len(p.text or "") for p in self.pages)
        total_html_size = sum(len(p.html or "") for p in self.pages)

        # Averages
        avg_links = total_links / total_pages
        avg_text_size = total_text_size / total_pages
        avg_html_size = total_html_size / total_pages if total_html_size > 0 else 0

        # Depth analysis
        depths = [p.depth for p in self.pages]
        max_depth = max(depths) if depths else 0
        pages_by_depth = Counter(depths)

        # Domain analysis
        domains = [urlparse(p.url).netloc for p in self.pages]
        unique_domains = len(set(domains))
        top_domains = Counter(domains).most_common(10)

        # Status codes
        status_codes = Counter(p.status_code for p in self.pages)

        # Pages with content
        pages_with_text = sum(1 for p in self.pages if p.text)
        pages_with_title = sum(1 for p in self.pages if p.title)
        pages_with_metadata = sum(1 for p in self.pages if p.metadata)

        # Content quality
        text_lengths = [len(p.text or "") for p in self.pages if p.text]
        min_text = min(text_lengths) if text_lengths else 0
        max_text = max(text_lengths) if text_lengths else 0
        median_text = sorted(text_lengths)[len(text_lengths) // 2] if text_lengths else 0

        self._stats_cache = {
            "total_pages": total_pages,
            "total_links": total_links,
            "total_text_size": total_text_size,
            "total_html_size": total_html_size,
            "avg_links_per_page": round(avg_links, 2),
            "avg_text_size": round(avg_text_size, 2),
            "avg_html_size": round(avg_html_size, 2),
            "max_depth": max_depth,
            "pages_by_depth": dict(pages_by_depth),
            "unique_domains": unique_domains,
            "top_domains": [{"domain": d, "count": c} for d, c in top_domains],
            "status_codes": dict(status_codes),
            "pages_with_text": pages_with_text,
            "pages_with_title": pages_with_title,
            "pages_with_metadata": pages_with_metadata,
            "text_length_min": min_text,
            "text_length_max": max_text,
            "text_length_median": median_text,
        }

        return self._stats_cache

    def format_summary(self) -> str:
        """
        Format stats as human-readable summary.

        Returns:
            Formatted string with statistics
        """
        stats = self.compute()

        if stats["total_pages"] == 0:
            return "No pages found."

        lines = [
            "=" * 60,
            "YOINK Crawl Statistics",
            "=" * 60,
            "",
            f"Total Pages: {stats['total_pages']:,}",
            f"Total Links: {stats['total_links']:,}",
            f"Avg Links/Page: {stats['avg_links_per_page']}",
            "",
            "Content Size:",
            f"  Total Text: {self._format_bytes(stats['total_text_size'])}",
            f"  Avg Text/Page: {self._format_bytes(stats['avg_text_size'])}",
        ]

        if stats["total_html_size"] > 0:
            lines.append(f"  Total HTML: {self._format_bytes(stats['total_html_size'])}")

        lines.extend(
            [
                "",
                "Domains:",
                f"  Unique Domains: {stats['unique_domains']}",
                "  Top Domains:",
            ]
        )

        for item in stats["top_domains"][:5]:
            lines.append(f"    - {item['domain']}: {item['count']} pages")

        lines.extend(
            [
                "",
                f"Depth Distribution:",
            ]
        )

        for depth in sorted(stats["pages_by_depth"].keys()):
            count = stats["pages_by_depth"][depth]
            bar = "#" * min(50, count)
            lines.append(f"  Depth {depth}: {count:>4} {bar}")

        lines.extend(
            [
                "",
                "Content Quality:",
                f"  Pages with Text: {stats['pages_with_text']} ({stats['pages_with_text'] / stats['total_pages'] * 100:.1f}%)",
                f"  Pages with Title: {stats['pages_with_title']} ({stats['pages_with_title'] / stats['total_pages'] * 100:.1f}%)",
                f"  Pages with Metadata: {stats['pages_with_metadata']} ({stats['pages_with_metadata'] / stats['total_pages'] * 100:.1f}%)",
                "",
                "Text Length:",
                f"  Min: {stats['text_length_min']:,} chars",
                f"  Median: {stats['text_length_median']:,} chars",
                f"  Max: {stats['text_length_max']:,} chars",
                "",
                "=" * 60,
            ]
        )

        return "\n".join(lines)

    def _format_bytes(self, size: float) -> str:
        """Format bytes as human-readable string."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"

    def export_csv(self, output_path: Path):
        """
        Export stats to CSV file.

        Args:
            output_path: Path to output CSV file
        """
        import csv

        stats = self.compute()

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Write summary stats
            writer.writerow(["Metric", "Value"])
            writer.writerow(["Total Pages", stats["total_pages"]])
            writer.writerow(["Total Links", stats["total_links"]])
            writer.writerow(["Avg Links per Page", stats["avg_links_per_page"]])
            writer.writerow(["Total Text Size (bytes)", stats["total_text_size"]])
            writer.writerow(["Unique Domains", stats["unique_domains"]])
            writer.writerow(["Max Depth", stats["max_depth"]])
            writer.writerow([])

            # Write top domains
            writer.writerow(["Top Domains", "Count"])
            for item in stats["top_domains"]:
                writer.writerow([item["domain"], item["count"]])

        logger.info("exported_stats_csv", path=str(output_path))
