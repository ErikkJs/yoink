"""Tests for statistics module."""

import json
from pathlib import Path
import pytest
from yoink.models import Page
from yoink.stats import CrawlStats


class TestCrawlStats:
    """Test crawl statistics functionality."""

    @pytest.fixture
    def sample_pages(self):
        """Sample pages for testing."""
        return [
            Page(
                url="https://example.com",
                title="Example",
                text="A" * 1000,
                links=["https://example.com/page1", "https://example.com/page2"],
                depth=0,
            ),
            Page(
                url="https://example.com/page1",
                title="Page 1",
                text="B" * 500,
                links=["https://example.com/page3"],
                depth=1,
            ),
            Page(
                url="https://example.com/page2",
                title="Page 2",
                text="C" * 1500,
                links=[],
                depth=1,
            ),
        ]

    def test_compute_basic_stats(self, sample_pages):
        """Test basic statistics computation."""
        stats = CrawlStats(sample_pages)
        result = stats.compute()

        assert result["total_pages"] == 3
        assert result["total_links"] == 3
        assert result["total_text_size"] == 3000
        assert result["max_depth"] == 1

    def test_compute_averages(self, sample_pages):
        """Test average calculations."""
        stats = CrawlStats(sample_pages)
        result = stats.compute()

        assert result["avg_links_per_page"] == 1.0  # 3 links / 3 pages
        assert result["avg_text_size"] == 1000.0  # 3000 chars / 3 pages

    def test_depth_distribution(self, sample_pages):
        """Test depth distribution."""
        stats = CrawlStats(sample_pages)
        result = stats.compute()

        assert result["pages_by_depth"][0] == 1
        assert result["pages_by_depth"][1] == 2

    def test_text_length_stats(self, sample_pages):
        """Test text length statistics."""
        stats = CrawlStats(sample_pages)
        result = stats.compute()

        assert result["text_length_min"] == 500
        assert result["text_length_max"] == 1500
        assert result["text_length_median"] == 1000

    def test_content_quality_stats(self, sample_pages):
        """Test content quality metrics."""
        stats = CrawlStats(sample_pages)
        result = stats.compute()

        assert result["pages_with_text"] == 3
        assert result["pages_with_title"] == 3

    def test_empty_pages(self):
        """Test stats with no pages."""
        stats = CrawlStats([])
        result = stats.compute()

        assert result["total_pages"] == 0

    def test_format_summary(self, sample_pages):
        """Test summary formatting."""
        stats = CrawlStats(sample_pages)
        summary = stats.format_summary()

        assert "Total Pages: 3" in summary
        assert "Total Links: 3" in summary
        assert "example.com" in summary

    def test_from_jsonl_file(self, sample_pages, tmp_path):
        """Test loading from JSONL file."""
        # Create test JSONL file
        jsonl_file = tmp_path / "test.jsonl"
        with open(jsonl_file, "w") as f:
            for page in sample_pages:
                f.write(json.dumps(page.model_dump(mode="json")) + "\n")

        # Load and verify
        stats = CrawlStats.from_file(jsonl_file)
        result = stats.compute()

        assert result["total_pages"] == 3
        assert result["total_links"] == 3

    def test_from_json_file(self, sample_pages, tmp_path):
        """Test loading from JSON file."""
        # Create test JSON file
        json_file = tmp_path / "test.json"
        with open(json_file, "w") as f:
            data = [page.model_dump(mode="json") for page in sample_pages]
            json.dump(data, f)

        # Load and verify
        stats = CrawlStats.from_file(json_file)
        result = stats.compute()

        assert result["total_pages"] == 3

    def test_export_csv(self, sample_pages, tmp_path):
        """Test CSV export."""
        stats = CrawlStats(sample_pages)
        csv_file = tmp_path / "stats.csv"

        stats.export_csv(csv_file)

        assert csv_file.exists()

        # Verify content
        import csv

        with open(csv_file, "r") as f:
            reader = csv.reader(f)
            rows = list(reader)

            # Check header
            assert rows[0] == ["Metric", "Value"]

            # Check some values
            metric_values = {row[0]: row[1] for row in rows[1:] if len(row) == 2}
            assert metric_values["Total Pages"] == "3"
            assert metric_values["Total Links"] == "3"

    def test_domain_analysis(self):
        """Test domain analysis."""
        pages = [
            Page(url="https://example.com/1", depth=0),
            Page(url="https://example.com/2", depth=0),
            Page(url="https://other.com/1", depth=0),
        ]

        stats = CrawlStats(pages)
        result = stats.compute()

        assert result["unique_domains"] == 2
        assert len(result["top_domains"]) == 2

    def test_status_code_tracking(self):
        """Test status code tracking."""
        pages = [
            Page(url="https://example.com/1", status_code=200, depth=0),
            Page(url="https://example.com/2", status_code=200, depth=0),
            Page(url="https://example.com/3", status_code=404, depth=0),
        ]

        stats = CrawlStats(pages)
        result = stats.compute()

        assert result["status_codes"][200] == 2
        assert result["status_codes"][404] == 1

    def test_stats_caching(self, sample_pages):
        """Test that stats are cached."""
        stats = CrawlStats(sample_pages)

        # First computation
        result1 = stats.compute()

        # Second computation should use cache
        result2 = stats.compute()

        assert result1 == result2
        assert result1 is result2  # Same object
