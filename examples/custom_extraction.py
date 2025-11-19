"""
Custom content processing example.

Shows how to process crawled pages with custom logic,
such as filtering, transformation, or additional extraction.
"""

import asyncio
from yoink import Crawler, CrawlConfig
from yoink.models import Page


async def main():
    """Crawl with custom processing."""
    print("🎨 Custom extraction example...")

    config = CrawlConfig(
        max_depth=1,
        max_pages=50,
        extract_text=True,
    )

    crawler = Crawler(config=config)
    pages = await crawler.crawl("https://news.ycombinator.com")

    print(f"\n✅ Crawled {len(pages)} pages")

    # Custom processing: extract links by domain
    links_by_domain = {}

    for page in pages:
        for link in page.links:
            # Extract domain from link
            try:
                from urllib.parse import urlparse

                domain = urlparse(link).netloc
                if domain:
                    links_by_domain.setdefault(domain, 0)
                    links_by_domain[domain] += 1
            except:
                continue

    # Show top domains
    print("\n🔗 Top linked domains:")
    sorted_domains = sorted(links_by_domain.items(), key=lambda x: x[1], reverse=True)

    for domain, count in sorted_domains[:10]:
        print(f"   {domain}: {count} links")

    # Custom filtering: find pages with specific keywords
    keyword = "python"
    matching_pages = [
        page
        for page in pages
        if page.text and keyword.lower() in page.text.lower()
    ]

    print(f"\n🔍 Pages mentioning '{keyword}': {len(matching_pages)}")

    for page in matching_pages[:5]:
        print(f"   - {page.title or page.url}")

    # Custom extraction: get all metadata
    pages_with_metadata = [page for page in pages if page.metadata]

    print(f"\n📊 Pages with metadata: {len(pages_with_metadata)}")

    if pages_with_metadata:
        sample = pages_with_metadata[0]
        print(f"\n   Sample metadata from {sample.url}:")
        for key, value in sample.metadata.items():
            print(f"      {key}: {value[:100]}...")


if __name__ == "__main__":
    asyncio.run(main())
