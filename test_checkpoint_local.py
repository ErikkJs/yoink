"""
Quick local test for checkpoint/resume functionality.

This script crawls a site with checkpoint enabled, then you can:
1. Interrupt it with Ctrl+C
2. Run again to see it resume from checkpoint
"""

import asyncio
from yoink import Crawler, CrawlConfig, CheckpointManager


async def test_checkpoint():
    print("\n" + "="*60)
    print("Testing Checkpoint/Resume Locally")
    print("="*60 + "\n")

    # Small config for quick testing
    config = CrawlConfig(
        max_depth=2,
        max_pages=20,  # Small number for testing
        max_concurrency=5,
        extract_text=True,
    )

    # Use local checkpoint file
    checkpoint_file = "./test_checkpoint.jsonl"
    checkpoint = CheckpointManager.from_uri(
        checkpoint_file,
        flush_interval=3  # Flush every 3 pages for testing
    )

    crawler = Crawler(config=config, checkpoint_manager=checkpoint)

    print(f"Checkpoint file: {checkpoint_file}")
    print(f"Config: max_pages={config.max_pages}, depth={config.max_depth}")
    print(f"Flush interval: 3 pages\n")

    # Check if checkpoint exists
    import os
    if os.path.exists(checkpoint_file):
        print("📂 Checkpoint file exists - will RESUME from previous crawl")
        print("   Delete test_checkpoint.jsonl to start fresh\n")
    else:
        print("🆕 No checkpoint found - starting NEW crawl\n")

    print("💡 TIP: Press Ctrl+C to interrupt, then run again to test resume!\n")
    print("-"*60 + "\n")

    try:
        # Try to resume (will start fresh if no checkpoint)
        pages = await crawler.crawl(
            "https://example.com",  # Simple site for testing
            resume=True
        )

        print("\n" + "="*60)
        print("✅ Crawl COMPLETED")
        print("="*60)
        print(f"Total pages crawled: {len(pages)}")
        print(f"\nCheckpoint saved to: {checkpoint_file}")
        print(f"File size: {os.path.getsize(checkpoint_file)} bytes")

        # Show some pages
        if pages:
            print(f"\nFirst few pages:")
            for i, page in enumerate(pages[:5]):
                print(f"  {i+1}. {page.url} (depth: {page.depth})")

    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print("⚠️  Crawl INTERRUPTED")
        print("="*60)
        print(f"Pages crawled so far: {len(crawler.pages)}")
        print(f"Checkpoint saved to: {checkpoint_file}")
        print("\n💾 Run this script again to RESUME from checkpoint!")
        print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(test_checkpoint())
