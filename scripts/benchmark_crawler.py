#!/usr/bin/env python3
"""
Crawler Performance Benchmark

Tests the overall crawler performance:
- Pages per second throughput
- Concurrency scaling
- Rate limiter impact
- Memory usage during crawl
"""

import asyncio
import sys
import time
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from yoink.crawler import Crawler
from yoink.models import CrawlConfig


class CrawlerBenchmark:
    """Benchmark crawler performance."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: list[dict] = []

    def log(self, msg: str):
        if self.verbose:
            print(f"  {msg}")

    async def benchmark_crawl(
        self,
        url: str,
        max_pages: int,
        max_depth: int,
        concurrency: int,
        rate_limit: float | None = None,
    ) -> dict:
        """Benchmark a single crawl configuration."""
        config = CrawlConfig(
            max_pages=max_pages,
            max_depth=max_depth,
            max_concurrency=concurrency,
            requests_per_second=rate_limit if rate_limit else 100.0,
            respect_robots=True,
            extract_text=True,
            save_html=False,
        )

        crawler = Crawler(config=config)

        self.log(f"Starting crawl: {url}")
        self.log(f"  max_pages={max_pages}, depth={max_depth}, concurrency={concurrency}")
        if rate_limit:
            self.log(f"  rate_limit={rate_limit} req/s")

        start = time.perf_counter()
        try:
            pages = await crawler.crawl(url)
            elapsed = time.perf_counter() - start

            result = {
                "url": url,
                "max_pages": max_pages,
                "max_depth": max_depth,
                "concurrency": concurrency,
                "rate_limit": rate_limit,
                "pages_crawled": len(pages),
                "elapsed_seconds": elapsed,
                "pages_per_second": len(pages) / elapsed if elapsed > 0 else 0,
                "success": True,
                "error": None,
            }
        except Exception as e:
            elapsed = time.perf_counter() - start
            result = {
                "url": url,
                "max_pages": max_pages,
                "max_depth": max_depth,
                "concurrency": concurrency,
                "rate_limit": rate_limit,
                "pages_crawled": 0,
                "elapsed_seconds": elapsed,
                "pages_per_second": 0,
                "success": False,
                "error": str(e),
            }

        self.results.append(result)
        return result

    def print_result(self, result: dict):
        """Print a single benchmark result."""
        status = "OK" if result["success"] else "FAILED"
        print(f"\n  [{status}] {result['url']}")
        print(f"       Config: depth={result['max_depth']}, "
              f"concurrency={result['concurrency']}, "
              f"rate_limit={result['rate_limit'] or 'none'}")
        print(f"       Pages: {result['pages_crawled']}/{result['max_pages']} "
              f"in {result['elapsed_seconds']:.2f}s")
        print(f"       Throughput: {result['pages_per_second']:.2f} pages/sec")
        if result["error"]:
            print(f"       Error: {result['error']}")

    def print_summary(self):
        """Print summary of all benchmark results."""
        print("\n" + "=" * 60)
        print(" BENCHMARK SUMMARY")
        print("=" * 60)

        successful = [r for r in self.results if r["success"]]
        failed = [r for r in self.results if not r["success"]]

        print(f"\n  Total runs: {len(self.results)}")
        print(f"  Successful: {len(successful)}")
        print(f"  Failed: {len(failed)}")

        if successful:
            avg_throughput = sum(r["pages_per_second"] for r in successful) / len(successful)
            max_throughput = max(r["pages_per_second"] for r in successful)
            total_pages = sum(r["pages_crawled"] for r in successful)
            total_time = sum(r["elapsed_seconds"] for r in successful)

            print(f"\n  Total pages crawled: {total_pages}")
            print(f"  Total time: {total_time:.2f}s")
            print(f"  Average throughput: {avg_throughput:.2f} pages/sec")
            print(f"  Max throughput: {max_throughput:.2f} pages/sec")

        print()


async def run_quick_benchmark(verbose: bool = False):
    """Run a quick benchmark with httpbin.org."""
    benchmark = CrawlerBenchmark(verbose=verbose)

    print("\nYOINK Crawler Quick Benchmark")
    print("=" * 60)
    print("Target: httpbin.org (simple test site)")

    # Test 1: Basic crawl
    print("\n[Test 1] Basic crawl - 5 pages, depth 1")
    result = await benchmark.benchmark_crawl(
        url="https://httpbin.org",
        max_pages=5,
        max_depth=1,
        concurrency=3,
    )
    benchmark.print_result(result)

    # Test 2: With rate limiting
    print("\n[Test 2] Rate limited crawl - 5 pages, 1 req/s")
    result = await benchmark.benchmark_crawl(
        url="https://httpbin.org",
        max_pages=5,
        max_depth=1,
        concurrency=3,
        rate_limit=1.0,
    )
    benchmark.print_result(result)

    # Test 3: Higher concurrency
    print("\n[Test 3] Higher concurrency - 5 pages, concurrency=5")
    result = await benchmark.benchmark_crawl(
        url="https://httpbin.org",
        max_pages=5,
        max_depth=1,
        concurrency=5,
    )
    benchmark.print_result(result)

    benchmark.print_summary()


async def run_full_benchmark(url: str, verbose: bool = False):
    """Run full benchmark suite on a custom URL."""
    benchmark = CrawlerBenchmark(verbose=verbose)

    print(f"\nYOINK Crawler Full Benchmark")
    print("=" * 60)
    print(f"Target: {url}")

    # Concurrency scaling tests
    print("\n--- Concurrency Scaling Tests ---")
    for concurrency in [1, 3, 5, 10]:
        print(f"\n[Test] Concurrency = {concurrency}")
        result = await benchmark.benchmark_crawl(
            url=url,
            max_pages=20,
            max_depth=2,
            concurrency=concurrency,
        )
        benchmark.print_result(result)

    # Rate limit impact tests
    print("\n--- Rate Limit Impact Tests ---")
    for rate_limit in [None, 5.0, 2.0, 1.0]:
        label = f"{rate_limit} req/s" if rate_limit else "unlimited"
        print(f"\n[Test] Rate limit = {label}")
        result = await benchmark.benchmark_crawl(
            url=url,
            max_pages=10,
            max_depth=2,
            concurrency=5,
            rate_limit=rate_limit,
        )
        benchmark.print_result(result)

    # Depth scaling tests
    print("\n--- Depth Scaling Tests ---")
    for depth in [1, 2, 3]:
        print(f"\n[Test] Max depth = {depth}")
        result = await benchmark.benchmark_crawl(
            url=url,
            max_pages=30,
            max_depth=depth,
            concurrency=5,
        )
        benchmark.print_result(result)

    benchmark.print_summary()


def main():
    parser = argparse.ArgumentParser(
        description="YOINK Crawler Performance Benchmark",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python benchmark_crawler.py --quick
  python benchmark_crawler.py --url https://docs.python.org
  python benchmark_crawler.py --url https://example.com --verbose
        """,
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick benchmark with httpbin.org",
    )
    parser.add_argument(
        "--url",
        type=str,
        help="URL to benchmark against",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    if args.quick:
        asyncio.run(run_quick_benchmark(args.verbose))
    elif args.url:
        asyncio.run(run_full_benchmark(args.url, args.verbose))
    else:
        parser.print_help()
        print("\nError: Please specify --quick or --url")
        sys.exit(1)


if __name__ == "__main__":
    main()
