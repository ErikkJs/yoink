# YOINK

> The public data crawler. Because it's public.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Tests](https://img.shields.io/badge/tests-68%20passing-brightgreen.svg)

**YOINK** is a fast, async web crawler built for extracting clean, AI-ready data from public websites. Simple to use, respectful of servers, and outputs data in formats ready for machine learning pipelines.

## Features

- **Async crawling** - Fast concurrent requests with configurable limits
- **Text extraction** - Clean, AI-ready text via trafilatura
- **Multiple formats** - JSON, JSONL, Parquet, plain text
- **URL filtering** - Include/exclude patterns and extension filtering
- **Checkpoint/Resume** - Resumable crawls with local or S3 storage
- **Stats analysis** - Comprehensive crawl statistics and metrics
- **Cloud-ready** - S3 backend support for Lambda/cloud deployments

## Installation

```bash
# From source (not yet on PyPI)
git clone https://github.com/ErikkJs/yoink
cd yoink
poetry install

# Or with pip
git clone https://github.com/ErikkJs/yoink
cd yoink
pip install -e .

# Install with S3 support
pip install -e ".[s3]"
# or with poetry
poetry install -E s3
```

## Quick Start

### CLI Usage

```bash
# Basic crawl
yoink crawl https://example.com

# Crawl with depth and save as JSON
yoink crawl https://docs.python.org --depth 2 --format json -o python_docs.json

# Filter URLs with patterns
yoink crawl https://example.com --include "*/blog/*" --exclude "*/private/*"

# Skip file types
yoink crawl https://example.com --skip-extensions pdf,zip,exe

# Analyze your crawl
yoink stats crawl_output.jsonl

# Export stats to CSV
yoink stats crawl_output.jsonl --export stats.csv

# Combine features
yoink crawl https://docs.python.org \
  --depth 2 \
  --max-pages 100 \
  --include "*/tutorial/*" \
  --skip-extensions pdf,zip \
  -o python_tutorial.jsonl

yoink stats python_tutorial.jsonl

# Checkpoint to local file
yoink crawl https://example.com --checkpoint crawl.jsonl

# Resume from checkpoint
yoink crawl https://example.com --checkpoint crawl.jsonl --resume

# Checkpoint to S3 for cloud deployments
# Note: Requires AWS credentials configured (see below)
yoink crawl https://example.com --checkpoint s3://my-bucket/crawl.jsonl
```

**S3 Checkpointing Setup:**

To use S3 checkpoints outside of AWS Lambda, configure AWS credentials:

```bash
# Option 1: AWS CLI (recommended for local development)
aws configure

# Option 2: Environment variables
export AWS_ACCESS_KEY_ID=your_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1

# Option 3: IAM role (automatic on EC2/ECS/Lambda)
# No configuration needed when running on AWS infrastructure
```

**Required S3 Permissions:**

Your IAM user/role needs these permissions for the S3 bucket:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:HeadObject"
      ],
      "Resource": "arn:aws:s3:::your-bucket-name/*"
    }
  ]
}
```

### Library Usage

```python
import asyncio
from yoink import Crawler, CrawlConfig

# Simple crawl
async def main():
    crawler = Crawler()
    pages = await crawler.crawl("https://example.com")

    for page in pages:
        print(f"{page.url}: {page.title}")
        print(f"Text length: {len(page.text or '')}")

asyncio.run(main())
```

```python
# Advanced configuration
config = CrawlConfig(
    max_depth=3,
    max_pages=1000,
    max_concurrency=20,
    follow_external=False,
    extract_text=True,
    save_html=False,
)

crawler = Crawler(config=config)
pages = await crawler.crawl("https://example.com")

# Save to different formats
from yoink.writers import Writer
from pathlib import Path

Writer.write_jsonl(pages, Path("output.jsonl"))
Writer.write_parquet(pages, Path("output.parquet"))
```

```python
# Resumable crawls with checkpointing
from yoink import Crawler, CrawlConfig, CheckpointManager

async def resumable_crawl():
    config = CrawlConfig(max_depth=3, max_pages=1000)

    # Create checkpoint manager (local file)
    checkpoint = CheckpointManager.from_uri("./crawl_checkpoint.jsonl")

    # Or use S3 for cloud deployments
    # checkpoint = CheckpointManager.from_uri("s3://my-bucket/checkpoint.jsonl")

    crawler = Crawler(config=config, checkpoint_manager=checkpoint)

    # First run
    pages = await crawler.crawl("https://example.com")

    # If interrupted, resume with:
    # pages = await crawler.crawl("https://example.com", resume=True)

    return pages
```

## Use Cases

### 1. Building AI Training Datasets

```python
from yoink import Crawler, CrawlConfig
from yoink.writers import Writer

async def build_training_data():
    config = CrawlConfig(
        max_depth=2,
        max_pages=10000,
        extract_text=True,
        save_html=False,
    )

    crawler = Crawler(config)
    pages = await crawler.crawl("https://documentation-site.com")

    # Save as JSONL for streaming to ML pipeline
    Writer.write_jsonl(pages, Path("training_data.jsonl"))

    print(f"Collected {len(pages)} pages for training")
```

### 2. Content Analysis

```python
import pandas as pd
import pyarrow.parquet as pq

# Crawl and save as Parquet
pages = await crawler.crawl("https://blog.example.com")
Writer.write_parquet(pages, Path("blog_content.parquet"))

# Analyze with pandas
df = pd.read_parquet("blog_content.parquet")
print(df.describe())
print(df.groupby("depth")["num_links"].mean())
```

### 3. Documentation Mirroring

```bash
# Mirror documentation site
yoink crawl https://docs.framework.com \
  --depth 3 \
  --max-pages 1000 \
  --format jsonl \
  -o framework_docs.jsonl
```

### 4. Cloud/Lambda Deployments

```python
# AWS Lambda function with S3 checkpointing
from yoink import Crawler, CrawlConfig, CheckpointManager

async def lambda_handler(event, context):
    # Use S3 for persistent checkpoints
    checkpoint = CheckpointManager.from_uri(
        "s3://my-crawl-bucket/checkpoint.jsonl",
        flush_interval=10  # Flush every 10 pages
    )

    config = CrawlConfig(
        max_pages=1000,
        max_concurrency=20,
    )

    crawler = Crawler(config=config, checkpoint_manager=checkpoint)

    # Resume from previous run if exists
    pages = await crawler.crawl(
        event['url'],
        resume=True  # Automatically resumes if checkpoint exists
    )

    return {
        'statusCode': 200,
        'pages_crawled': len(pages)
    }

# If Lambda times out or crashes, next invocation resumes automatically!
```

## CLI Reference

### Crawl Command

```
yoink crawl [URL] [OPTIONS]

Options:
  -d, --depth INTEGER          Maximum crawl depth (default: 1)
  -n, --max-pages INTEGER      Maximum pages to crawl (default: 100)
  -c, --concurrency INTEGER    Concurrent requests (default: 10)
  -f, --format [json|jsonl|parquet|text]  Output format (default: jsonl)
  -o, --output PATH           Output file path
  --follow-external           Follow external domain links
  --save-html                 Save raw HTML content
  --user-agent TEXT           Custom User-Agent string

  URL Filtering:
  --include TEXT              URL patterns to include (glob or regex, multiple allowed)
  --exclude TEXT              URL patterns to exclude (glob or regex, multiple allowed)
  --skip-extensions TEXT      File extensions to skip (comma-separated: pdf,zip,exe)

  Checkpointing:
  --checkpoint TEXT           Enable checkpointing (local file or s3://bucket/key)
  --checkpoint-interval INT   Pages between flushes (default: 10)
  --resume                    Resume from checkpoint file
```

### Stats Command

```
yoink stats [FILE] [OPTIONS]

Arguments:
  FILE                        Path to crawled data file (JSON or JSONL)

Options:
  -e, --export PATH           Export stats to CSV file
  --json                      Output stats as JSON instead of human-readable

Examples:
  yoink stats crawl_output.jsonl
  yoink stats crawl_output.jsonl --export stats.csv
  yoink stats crawl_output.jsonl --json
```

## Output Formats

### JSON
Single JSON array with all pages. Good for small datasets.

```json
[
  {
    "url": "https://example.com",
    "title": "Example Domain",
    "text": "This domain is for use in illustrative...",
    "links": ["https://example.com/about"],
    "metadata": {},
    "crawled_at": "2025-01-15T10:30:00",
    "status_code": 200,
    "depth": 0
  }
]
```

### JSONL (Recommended for AI)
Newline-delimited JSON. Stream-friendly, works with large datasets.

```jsonl
{"url": "https://example.com", "title": "Example", "text": "..."}
{"url": "https://example.com/about", "title": "About", "text": "..."}
```

### Parquet
Columnar format optimized for analytics. Best for data science workflows.

```python
import pandas as pd
df = pd.read_parquet("output.parquet")
```

### Text
Simple text format with extracted content.

## Configuration

### Via Python

```python
from yoink.models import CrawlConfig

config = CrawlConfig(
    max_depth=2,              # How deep to crawl
    max_pages=500,            # Max pages to fetch
    max_concurrency=15,       # Parallel requests
    respect_robots=True,      # Honor robots.txt
    follow_external=False,    # Stay on same domain
    extract_text=True,        # Extract clean text
    save_html=False,          # Don't save raw HTML
    timeout=30,               # Request timeout (seconds)
)
```

## Features

### Core Features
- **Async Architecture** - Built on asyncio/aiohttp for high performance
- **Smart Crawling** - Depth-limited BFS with automatic deduplication
- **AI-Ready Text** - Clean text extraction via trafilatura
- **Multiple Formats** - JSON, JSONL, Parquet, plain text
- **Configurable** - Depth, concurrency, rate limiting, user agent

### Checkpointing & Resume
- **Incremental Saving** - Pages written to checkpoint as they're crawled
- **State Persistence** - Save visited URLs, queue, and filtered URLs
- **Cloud-Native** - S3 backend for AWS Lambda and cloud deployments
- **Auto-Recovery** - Resume interrupted crawls seamlessly
- **Configurable Flushing** - Control checkpoint write frequency

### URL Filtering
- **Include Patterns** - Whitelist URLs with glob or regex patterns
- **Exclude Patterns** - Blacklist URLs to skip
- **Extension Filtering** - Skip file types (pdf, zip, images, etc.)
- **Multiple Filters** - Combine filters for precise targeting

### Stats & Analysis
- **Comprehensive Metrics** - Pages, links, domains, depth distribution
- **Content Quality** - Text length, metadata presence, status codes
- **Multiple Outputs** - Human-readable, JSON, CSV export
- **Domain Analysis** - Top domains, subdomain tracking

## Architecture

YOINK is designed to be simple and maintainable:

- **Fetcher**: Async HTTP client with retry logic (aiohttp)
- **Parser**: HTML parsing and link extraction (BeautifulSoup + lxml)
- **Extractor**: AI-grade text extraction (trafilatura)
- **Scheduler**: URL queue with deduplication and filtering
- **Filters**: Pattern matching for URL targeting
- **Writers**: Output to various formats
- **Stats**: Comprehensive analysis engine
- **Checkpoint**: State persistence with pluggable storage backends
- **Storage**: Cloud-agnostic abstraction (Local, S3)

Total custom code: ~2,800 lines. The rest is battle-tested libraries.

## Examples

Check out the [`examples/`](examples/) directory for more:

- `basic_crawl.py` - Simple crawling example
- `ai_training_data.py` - Build training datasets
- `custom_extraction.py` - Custom content processing


## Why YOINK?

Because public data is public, and you should be able to easily access it for:
- Building AI/ML datasets
- Content analysis
- Documentation backups
- Research
- SEO analysis
- ...literally anything legal

## Responsible Use

YOINK is designed for ethical web crawling:

- ✅ Respects robots.txt by default
- ✅ Configurable rate limiting
- ✅ Identifies itself with User-Agent
- ✅ Only accesses public data

**Use responsibly:**
- Don't overwhelm servers (use reasonable concurrency)
- Respect rate limits and robots.txt
- Don't crawl sites that explicitly forbid it
- Only use data according to its license/terms

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**Test Coverage**: 68 passing tests

## Acknowledgments

Built with:
- [aiohttp](https://github.com/aio-libs/aiohttp) - Async HTTP
- [trafilatura](https://github.com/adbar/trafilatura) - Text extraction
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing
- [Click](https://click.palletsprojects.com/) - CLI framework

---

Star ⭐ this repo if YOINK helped you!
