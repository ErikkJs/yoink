"""
Basic crawling example.

This script demonstrates the simplest way to use yoink.
"""

import asyncio
from yoink import Crawler


async def main():
    """Simple crawl example."""
    print("🎯 Starting basic crawl...")

    # Create crawler with defaults
    crawler = Crawler()

    # Crawl a website
    pages = await crawler.crawl("https://example.com")

    # Print results
    print(f"\n✅ Crawled {len(pages)} pages\n")

    for page in pages:
        print(f"📄 {page.url}")
        print(f"   Title: {page.title or 'No title'}")
        print(f"   Text length: {len(page.text or '')} chars")
        print(f"   Links found: {len(page.links)}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
