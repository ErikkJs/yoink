"""
Extract data for AI training.

This example shows how to crawl a documentation site
and prepare clean training data for ML models.
"""

import asyncio
from pathlib import Path
from yoink import Crawler, CrawlConfig
from yoink.writers import Writer


async def main():
    """Crawl and prepare training data."""
    print("🤖 Building AI training dataset...")

    # Configure for AI training data
    config = CrawlConfig(
        max_depth=2,  # Crawl main pages + one level deep
        max_pages=500,  # Limit dataset size
        max_concurrency=20,  # Fast crawling
        extract_text=True,  # Get clean text
        save_html=False,  # Don't need raw HTML
        follow_external=False,  # Stay on same domain
    )

    crawler = Crawler(config=config)

    # Crawl documentation site
    pages = await crawler.crawl("https://docs.python.org/3/")

    print(f"\n✅ Collected {len(pages)} pages")

    # Filter for quality
    quality_pages = [
        page
        for page in pages
        if page.text and len(page.text) > 200  # Minimum content
    ]

    print(f"📊 {len(quality_pages)} pages after quality filtering")

    # Save as JSONL (best for streaming to ML pipeline)
    output_path = Path("training_data.jsonl")
    Writer.write_jsonl(quality_pages, output_path)

    print(f"💾 Saved to {output_path}")

    # Print stats
    total_text = sum(len(p.text or "") for p in quality_pages)
    avg_text = total_text // len(quality_pages) if quality_pages else 0

    print(f"\n📈 Dataset Statistics:")
    print(f"   Total pages: {len(quality_pages)}")
    print(f"   Total text: {total_text:,} characters")
    print(f"   Average page length: {avg_text:,} characters")

    # Sample output
    print(f"\n📝 Sample page:")
    if quality_pages:
        sample = quality_pages[0]
        print(f"   URL: {sample.url}")
        print(f"   Title: {sample.title}")
        print(f"   Text preview: {sample.text[:200]}...")


if __name__ == "__main__":
    asyncio.run(main())
