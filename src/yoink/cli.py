"""CLI interface for yoink."""

import asyncio
from pathlib import Path
import click
import structlog

from yoink.crawler import Crawler
from yoink.models import CrawlConfig
from yoink.writers import Writer
from yoink.stats import CrawlStats
from yoink.filters import CombinedFilter
from yoink.checkpoint import CheckpointManager
from yoink import __version__

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.dev.ConsoleRenderer(),
    ]
)


@click.group()
@click.version_option(version=__version__)
def main():
    """
    YOINK - The public data crawler.

    Because it's public.
    """
    pass


@main.command()
@click.argument("url")
@click.option(
    "--depth",
    "-d",
    default=1,
    help="Maximum crawl depth (default: 1)",
    type=int,
)
@click.option(
    "--max-pages",
    "-n",
    default=100,
    help="Maximum number of pages to crawl (default: 100)",
    type=int,
)
@click.option(
    "--concurrency",
    "-c",
    default=10,
    help="Number of concurrent requests (default: 10)",
    type=int,
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "jsonl", "parquet", "text"], case_sensitive=False),
    default="jsonl",
    help="Output format (default: jsonl)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path (default: crawl_output.<format>)",
)
@click.option(
    "--follow-external",
    is_flag=True,
    help="Follow links to external domains",
)
@click.option(
    "--save-html",
    is_flag=True,
    help="Save raw HTML content",
)
@click.option(
    "--user-agent",
    default="yoink/0.3.0 (+https://github.com/ErikkJs/yoink)",
    help="Custom User-Agent string",
)
@click.option(
    "--include",
    multiple=True,
    help="URL patterns to include (glob or regex)",
)
@click.option(
    "--exclude",
    multiple=True,
    help="URL patterns to exclude (glob or regex)",
)
@click.option(
    "--skip-extensions",
    help="Comma-separated list of file extensions to skip (e.g., pdf,zip,exe)",
)
@click.option(
    "--checkpoint",
    type=str,
    help="Enable checkpointing and specify file path or URI (local file, s3://bucket/key)",
)
@click.option(
    "--checkpoint-interval",
    type=int,
    default=10,
    help="Number of pages between checkpoint flushes (default: 10)",
)
@click.option(
    "--resume",
    is_flag=True,
    help="Resume from checkpoint file",
)
def crawl(
    url: str,
    depth: int,
    max_pages: int,
    concurrency: int,
    format: str,
    output: str,
    follow_external: bool,
    save_html: bool,
    user_agent: str,
    include: tuple,
    exclude: tuple,
    skip_extensions: str,
    checkpoint: str,
    checkpoint_interval: int,
    resume: bool,
):
    """
    Yoink a website starting from URL.

    Examples:

        yoink crawl https://example.com

        yoink crawl https://docs.python.org --depth 2 --max-pages 50

        yoink crawl https://example.com --format parquet -o data.parquet

        yoink crawl https://example.com --include "*/blog/*" --exclude "*/private/*"

        yoink crawl https://example.com --skip-extensions pdf,zip,exe
    """
    # Validate checkpoint/resume options
    if resume and not checkpoint:
        click.echo("Error: --resume requires --checkpoint to be specified", err=True)
        return

    click.echo(f"Yoinking {url}...")
    click.echo(f"Max depth: {depth}, Max pages: {max_pages}, Concurrency: {concurrency}")

    if checkpoint:
        if resume:
            click.echo(f"Resuming from checkpoint: {checkpoint}")
        else:
            click.echo(f"Checkpointing to: {checkpoint} (interval: {checkpoint_interval} pages)")

    # Parse skip extensions
    skip_exts = None
    if skip_extensions:
        skip_exts = [ext.strip() for ext in skip_extensions.split(',')]

    # Create URL filter if any filter options are provided
    url_filter = None
    if include or exclude or skip_exts:
        url_filter = CombinedFilter.from_config(
            include_patterns=list(include) if include else None,
            exclude_patterns=list(exclude) if exclude else None,
            skip_extensions=skip_exts,
        )

        # Log filter info
        if include:
            click.echo(f"Include patterns: {', '.join(include)}")
        if exclude:
            click.echo(f"Exclude patterns: {', '.join(exclude)}")
        if skip_exts:
            click.echo(f"Skip extensions: {', '.join(skip_exts)}")

    # Create config
    config = CrawlConfig(
        max_depth=depth,
        max_pages=max_pages,
        max_concurrency=concurrency,
        follow_external=follow_external,
        save_html=save_html,
        user_agent=user_agent,
    )

    # Create checkpoint manager if specified
    checkpoint_manager = None
    if checkpoint:
        checkpoint_manager = CheckpointManager.from_uri(checkpoint, flush_interval=checkpoint_interval)

    # Create crawler
    crawler = Crawler(config=config, url_filter=url_filter, checkpoint_manager=checkpoint_manager)

    # Run crawl
    try:
        pages = asyncio.run(crawler.crawl_with_progress(url, resume=resume))
    except KeyboardInterrupt:
        click.echo("\nCrawl interrupted by user")
        pages = crawler.pages
        # Save checkpoint on interruption
        if checkpoint_manager:
            click.echo("Saving checkpoint before exit...")
            asyncio.run(crawler._save_checkpoint_state())
            asyncio.run(checkpoint_manager.close())
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        return

    if not pages:
        click.echo("No pages were crawled")
        return

    # Determine output path
    # If using checkpoint, don't create separate output file unless explicitly specified
    if checkpoint and not output:
        click.echo(f"Yoinked {len(pages)} pages (saved in checkpoint: {checkpoint})")

        # Print some stats
        total_links = sum(len(p.links) for p in pages)
        total_text_size = sum(len(p.text or "") for p in pages)
        click.echo(f"Total links found: {total_links}")
        click.echo(f"Total text extracted: {total_text_size:,} characters")
        return

    if output is None:
        output = f"crawl_output.{format}"
    output_path = Path(output)

    # Write output
    try:
        if format == "json":
            Writer.write_json(pages, output_path)
        elif format == "jsonl":
            Writer.write_jsonl(pages, output_path)
        elif format == "parquet":
            Writer.write_parquet(pages, output_path)
        elif format == "text":
            Writer.write_text(pages, output_path)

        click.echo(f"Yoinked {len(pages)} pages to {output_path}")

        # Print some stats
        total_links = sum(len(p.links) for p in pages)
        total_text_size = sum(len(p.text or "") for p in pages)
        click.echo(f"Total links found: {total_links}")
        click.echo(f"Total text extracted: {total_text_size:,} characters")

    except Exception as e:
        click.echo(f"Error writing output: {e}", err=True)


@main.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--export",
    "-e",
    type=click.Path(),
    help="Export stats to CSV file",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output stats as JSON",
)
def stats(file_path: str, export: str, output_json: bool):
    """
    Show statistics for crawled data.

    Examples:

        yoink stats crawl_output.jsonl

        yoink stats crawl_output.json --export stats.csv

        yoink stats crawl_output.jsonl --json
    """
    try:
        path = Path(file_path)
        crawl_stats = CrawlStats.from_file(path)

        if output_json:
            # Output as JSON
            import json

            stats_data = crawl_stats.compute()
            click.echo(json.dumps(stats_data, indent=2))
        else:
            # Output human-readable summary
            summary = crawl_stats.format_summary()
            click.echo(summary)

        # Export to CSV if requested
        if export:
            export_path = Path(export)
            crawl_stats.export_csv(export_path)
            click.echo(f"\nStats exported to {export_path}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@main.command()
def version():
    """Show version information."""
    click.echo(f"yoink version {__version__}")
    click.echo("The public data crawler.")


if __name__ == "__main__":
    main()
