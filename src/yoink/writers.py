"""Output writers for different formats."""

import json
from pathlib import Path
from typing import List
import structlog

from yoink.models import Page

logger = structlog.get_logger()


class Writer:
    """Handles writing crawled data to different formats."""

    @staticmethod
    def write_json(pages: List[Page], output_path: Path):
        """
        Write pages to JSON file.

        Args:
            pages: List of crawled pages
            output_path: Output file path
        """
        data = [page.model_dump(mode="json") for page in pages]

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info("wrote_json", path=str(output_path), pages=len(pages))

    @staticmethod
    def write_jsonl(pages: List[Page], output_path: Path):
        """
        Write pages to JSONL (newline-delimited JSON) file.

        Args:
            pages: List of crawled pages
            output_path: Output file path
        """
        with open(output_path, "w", encoding="utf-8") as f:
            for page in pages:
                json_line = json.dumps(page.model_dump(mode="json"), ensure_ascii=False)
                f.write(json_line + "\n")

        logger.info("wrote_jsonl", path=str(output_path), pages=len(pages))

    @staticmethod
    def write_parquet(pages: List[Page], output_path: Path):
        """
        Write pages to Parquet file.

        Requires pyarrow to be installed (pip install yoink[parquet]).

        Args:
            pages: List of crawled pages
            output_path: Output file path
        """
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq
        except ImportError:
            raise ImportError(
                "Parquet support requires pyarrow. Install with: pip install yoink[parquet]"
            )

        # Convert pages to dictionaries
        data = [page.model_dump(mode="json") for page in pages]

        # Flatten the data for better Parquet schema
        flattened = []
        for item in data:
            flat = {
                "url": item["url"],
                "title": item.get("title"),
                "text": item.get("text"),
                "crawled_at": item["crawled_at"],
                "status_code": item["status_code"],
                "depth": item["depth"],
                "num_links": len(item.get("links", [])),
                # Store metadata as JSON string
                "metadata": json.dumps(item.get("metadata", {})),
            }
            flattened.append(flat)

        # Create Arrow table and write to Parquet
        table = pa.Table.from_pylist(flattened)
        pq.write_table(table, output_path, compression="snappy")

        logger.info("wrote_parquet", path=str(output_path), pages=len(pages))

    @staticmethod
    def write_text(pages: List[Page], output_path: Path):
        """
        Write extracted text to plain text file.

        Args:
            pages: List of crawled pages
            output_path: Output file path
        """
        with open(output_path, "w", encoding="utf-8") as f:
            for page in pages:
                f.write(f"URL: {page.url}\n")
                f.write(f"Title: {page.title or 'N/A'}\n")
                f.write("-" * 80 + "\n")
                if page.text:
                    f.write(page.text)
                    f.write("\n\n")
                f.write("=" * 80 + "\n\n")

        logger.info("wrote_text", path=str(output_path), pages=len(pages))
