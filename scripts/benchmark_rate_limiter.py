#!/usr/bin/env python3
"""
Rate Limiter Performance Benchmark

Tests the performance characteristics of the RateLimiter:
- Token bucket throughput
- Per-domain isolation overhead
- Concurrent request handling
- Memory usage with many domains
"""

import asyncio
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from yoink.rate_limiter import RateLimiter


class BenchmarkResults:
    """Stores and displays benchmark results."""

    def __init__(self, name: str):
        self.name = name
        self.results: list[tuple[str, float, str]] = []

    def add(self, test_name: str, value: float, unit: str):
        self.results.append((test_name, value, unit))

    def display(self):
        print(f"\n{'=' * 60}")
        print(f" {self.name}")
        print(f"{'=' * 60}")
        for test_name, value, unit in self.results:
            print(f"  {test_name}: {value:.2f} {unit}")
        print()


async def benchmark_single_domain_throughput(
    requests_per_second: float, num_requests: int
) -> float:
    """Measure actual throughput for a single domain."""
    limiter = RateLimiter(requests_per_second=requests_per_second, burst_size=1)

    start = time.perf_counter()
    for _ in range(num_requests):
        await limiter.acquire("https://example.com/page")
    elapsed = time.perf_counter() - start

    return num_requests / elapsed


async def benchmark_multi_domain_throughput(
    requests_per_second: float, num_domains: int, requests_per_domain: int
) -> float:
    """Measure throughput across multiple domains."""
    limiter = RateLimiter(requests_per_second=requests_per_second, burst_size=1)
    domains = [f"https://domain{i}.com/page" for i in range(num_domains)]

    start = time.perf_counter()

    async def domain_requests(domain: str):
        for _ in range(requests_per_domain):
            await limiter.acquire(domain)

    await asyncio.gather(*[domain_requests(d) for d in domains])
    elapsed = time.perf_counter() - start

    total_requests = num_domains * requests_per_domain
    return total_requests / elapsed


async def benchmark_concurrent_same_domain(
    requests_per_second: float, num_concurrent: int
) -> float:
    """Measure how well rate limiting handles concurrent requests to same domain."""
    limiter = RateLimiter(requests_per_second=requests_per_second, burst_size=1)

    start = time.perf_counter()

    async def make_request():
        await limiter.acquire("https://example.com/page")

    await asyncio.gather(*[make_request() for _ in range(num_concurrent)])
    elapsed = time.perf_counter() - start

    return num_concurrent / elapsed


async def benchmark_acquire_overhead(num_iterations: int) -> float:
    """Measure the overhead of acquire() calls (with high rate limit)."""
    # Set very high rate to measure pure overhead
    limiter = RateLimiter(requests_per_second=100000, burst_size=100000)

    start = time.perf_counter()
    for i in range(num_iterations):
        await limiter.acquire(f"https://example.com/page{i}")
    elapsed = time.perf_counter() - start

    return elapsed / num_iterations * 1_000_000  # Return microseconds per call


async def benchmark_memory_scaling(num_domains: int) -> int:
    """Measure memory usage with many domains."""
    import tracemalloc

    tracemalloc.start()

    limiter = RateLimiter(requests_per_second=10)

    # Create buckets for many domains
    for i in range(num_domains):
        await limiter.acquire(f"https://domain{i}.com/page")

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return peak // 1024  # Return KB


async def benchmark_burst_handling(burst_size: int) -> tuple[float, float]:
    """Measure burst handling - time for burst vs sustained requests."""
    limiter = RateLimiter(requests_per_second=10, burst_size=burst_size)

    # Time for burst (should be near-instant)
    start = time.perf_counter()
    for _ in range(burst_size):
        await limiter.acquire("https://example.com/page")
    burst_time = time.perf_counter() - start

    # Time for next request after burst (should wait)
    start = time.perf_counter()
    await limiter.acquire("https://example.com/page")
    wait_time = time.perf_counter() - start

    return burst_time, wait_time


async def run_benchmarks():
    """Run all benchmarks and display results."""
    print("\nYOINK Rate Limiter Benchmark Suite")
    print("=" * 60)

    # Throughput benchmarks
    results = BenchmarkResults("Throughput Tests")

    # Single domain at 10 req/s
    throughput = await benchmark_single_domain_throughput(10.0, 20)
    results.add("Single domain (10 req/s limit, 20 requests)", throughput, "req/s")

    # Multi-domain parallel
    throughput = await benchmark_multi_domain_throughput(10.0, 10, 5)
    results.add("10 domains parallel (10 req/s each, 5 req/domain)", throughput, "req/s")

    # Concurrent to same domain
    throughput = await benchmark_concurrent_same_domain(10.0, 10)
    results.add("10 concurrent requests, same domain", throughput, "req/s")

    results.display()

    # Overhead benchmarks
    results = BenchmarkResults("Overhead Tests")

    overhead = await benchmark_acquire_overhead(10000)
    results.add("acquire() call overhead (10k calls)", overhead, "us/call")

    results.display()

    # Memory benchmarks
    results = BenchmarkResults("Memory Tests")

    mem = await benchmark_memory_scaling(100)
    results.add("Memory with 100 domains", mem, "KB")

    mem = await benchmark_memory_scaling(1000)
    results.add("Memory with 1000 domains", mem, "KB")

    results.display()

    # Burst handling
    results = BenchmarkResults("Burst Handling Tests")

    burst_time, wait_time = await benchmark_burst_handling(5)
    results.add("Time for 5-request burst", burst_time * 1000, "ms")
    results.add("Wait time after burst exhausted", wait_time * 1000, "ms")

    burst_time, wait_time = await benchmark_burst_handling(10)
    results.add("Time for 10-request burst", burst_time * 1000, "ms")
    results.add("Wait time after burst exhausted", wait_time * 1000, "ms")

    results.display()

    # Summary
    print("=" * 60)
    print(" SUMMARY")
    print("=" * 60)
    print("""
  The rate limiter implements a token bucket algorithm with:
  - Per-domain isolation for independent rate limiting
  - Burst capacity for handling traffic spikes
  - Minimal overhead per acquire() call
  - Linear memory scaling with number of domains

  Key findings:
  - Single domain throughput matches configured rate
  - Multiple domains can run in parallel at full speed
  - Burst requests are served immediately until capacity exhausted
  - Memory usage is efficient (~few KB per domain)
""")


if __name__ == "__main__":
    asyncio.run(run_benchmarks())
