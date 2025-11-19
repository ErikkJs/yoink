"""
Example: Using checkpoint/resume for large crawls.

This example demonstrates how to use the checkpoint/resume system
to handle interrupted crawls and resume from where you left off.
"""

import asyncio
from yoink import Crawler, CrawlConfig, CheckpointManager


async def example_local_checkpoint():
    """Example using local file checkpoint."""
    print("=== Local File Checkpoint Example ===\n")

    config = CrawlConfig(
        max_depth=2,
        max_pages=100,
        max_concurrency=10,
    )

    # Create checkpoint manager with local file
    checkpoint = CheckpointManager.from_uri(
        "./example_checkpoint.jsonl",
        flush_interval=5,  # Flush every 5 pages
    )

    crawler = Crawler(config=config, checkpoint_manager=checkpoint)

    print("Starting crawl with checkpoint enabled...")
    print("You can Ctrl+C to interrupt and resume later!\n")

    try:
        # First run - or resume if checkpoint exists
        pages = await crawler.crawl("https://example.com", resume=True)
        print(f"\nCrawled {len(pages)} pages")

    except KeyboardInterrupt:
        print("\n\nCrawl interrupted! Checkpoint saved.")
        print("Run this script again to resume from checkpoint.")


async def example_s3_checkpoint():
    """Example using S3 checkpoint (requires aioboto3)."""
    print("=== S3 Checkpoint Example ===\n")

    config = CrawlConfig(
        max_depth=2,
        max_pages=1000,
        max_concurrency=20,
    )

    # Create checkpoint manager with S3
    # Note: Requires AWS credentials configured (env vars, ~/.aws/credentials, etc.)
    checkpoint = CheckpointManager.from_uri(
        "s3://my-crawl-bucket/checkpoints/example.jsonl",
        flush_interval=10,  # Flush every 10 pages to minimize S3 API calls
    )

    crawler = Crawler(config=config, checkpoint_manager=checkpoint)

    print("Starting crawl with S3 checkpoint...")
    print("Perfect for AWS Lambda or cloud deployments!\n")

    # Automatically resumes if checkpoint exists in S3
    pages = await crawler.crawl("https://example.com", resume=True)
    print(f"\nCrawled {len(pages)} pages to S3")


async def example_lambda_handler():
    """
    Example AWS Lambda handler with checkpoint/resume.

    This can run across multiple Lambda invocations, automatically
    resuming from the previous checkpoint on each run.
    """
    print("=== Lambda Handler Example ===\n")

    # Lambda event would contain the URL to crawl
    event = {"url": "https://example.com"}

    # Use S3 for persistent storage across Lambda invocations
    checkpoint = CheckpointManager.from_uri(
        "s3://my-crawl-bucket/lambda-checkpoints/crawl.jsonl",
        flush_interval=10,
    )

    config = CrawlConfig(
        max_pages=5000,
        max_concurrency=30,
        max_depth=3,
    )

    crawler = Crawler(config=config, checkpoint_manager=checkpoint)

    # Always try to resume - if no checkpoint exists, starts fresh
    pages = await crawler.crawl(event["url"], resume=True)

    # Return response
    return {
        "statusCode": 200,
        "body": {
            "pages_crawled": len(pages),
            "message": "Crawl completed or checkpoint saved for next invocation",
        },
    }


async def main():
    """Run examples."""
    print("\n" + "=" * 60)
    print("YOINK Checkpoint/Resume Examples")
    print("=" * 60 + "\n")

    # Example 1: Local file checkpoint
    await example_local_checkpoint()

    # Example 2: S3 checkpoint (uncomment if you have AWS credentials)
    # await example_s3_checkpoint()

    # Example 3: Lambda handler (demonstration only)
    # result = await example_lambda_handler()
    # print(f"\nLambda result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
