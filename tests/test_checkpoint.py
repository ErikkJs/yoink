"""Tests for checkpoint functionality."""

import json
import pytest
from pathlib import Path
from datetime import datetime

from yoink.checkpoint import CheckpointManager
from yoink.storage import LocalFileStorage
from yoink.models import Page, CrawlConfig


@pytest.fixture
def temp_checkpoint_file(tmp_path):
    """Create a temporary checkpoint file path."""
    return tmp_path / "test_checkpoint.jsonl"


@pytest.fixture
def sample_page():
    """Create a sample page for testing."""
    return Page(
        url="https://example.com",
        title="Example Page",
        text="This is example text content",
        links=["https://example.com/page1", "https://example.com/page2"],
        metadata={"author": "Test Author"},
        status_code=200,
        depth=0,
    )


@pytest.fixture
def sample_config():
    """Create a sample config for testing."""
    return CrawlConfig(max_depth=2, max_pages=100)


@pytest.mark.asyncio
async def test_checkpoint_write_metadata(temp_checkpoint_file, sample_config):
    """Test writing metadata to checkpoint."""
    manager = CheckpointManager.from_uri(str(temp_checkpoint_file))

    await manager.write_metadata("https://example.com", sample_config)
    await manager.close()

    # Read and verify
    with open(temp_checkpoint_file, "r") as f:
        line = f.readline()
        data = json.loads(line)

        assert data["type"] == "metadata"
        assert data["start_url"] == "https://example.com"
        assert data["config"]["max_depth"] == 2
        assert data["config"]["max_pages"] == 100


@pytest.mark.asyncio
async def test_checkpoint_write_page(temp_checkpoint_file, sample_page):
    """Test writing page to checkpoint."""
    manager = CheckpointManager.from_uri(str(temp_checkpoint_file))

    await manager.write_page(sample_page)
    await manager.close()

    # Read and verify
    with open(temp_checkpoint_file, "r") as f:
        line = f.readline()
        data = json.loads(line)

        assert data["type"] == "page"
        assert data["url"] == "https://example.com"
        assert data["title"] == "Example Page"
        assert data["text"] == "This is example text content"
        assert len(data["links"]) == 2


@pytest.mark.asyncio
async def test_checkpoint_write_state(temp_checkpoint_file):
    """Test writing scheduler state to checkpoint."""
    manager = CheckpointManager.from_uri(str(temp_checkpoint_file))

    visited = {"https://example.com/1", "https://example.com/2"}
    queue = [("https://example.com/3", 1), ("https://example.com/4", 2)]
    filtered = {"https://example.com/filtered"}

    await manager.write_state(visited, queue, filtered)
    await manager.close()

    # Read and verify
    with open(temp_checkpoint_file, "r") as f:
        line = f.readline()
        data = json.loads(line)

        assert data["type"] == "state"
        assert set(data["visited"]) == visited
        # JSON serializes tuples as lists, so convert back
        assert [tuple(item) for item in data["queue"]] == queue
        assert set(data["filtered"]) == filtered


@pytest.mark.asyncio
async def test_checkpoint_load(temp_checkpoint_file, sample_page, sample_config):
    """Test loading checkpoint data."""
    manager = CheckpointManager.from_uri(str(temp_checkpoint_file))

    # Write test data
    await manager.write_metadata("https://example.com", sample_config)
    await manager.write_page(sample_page)
    await manager.write_state(
        visited={"https://example.com"},
        queue=[("https://example.com/next", 1)],
        filtered=set(),
    )
    await manager.close()

    # Load and verify
    manager2 = CheckpointManager.from_uri(str(temp_checkpoint_file))
    data = await manager2.load()
    await manager2.close()

    assert data["metadata"] is not None
    assert data["metadata"]["start_url"] == "https://example.com"

    assert len(data["pages"]) == 1
    assert data["pages"][0].url == "https://example.com"

    assert data["state"] is not None
    assert len(data["state"]["visited"]) == 1
    assert len(data["state"]["queue"]) == 1


@pytest.mark.asyncio
async def test_checkpoint_flush_interval(temp_checkpoint_file):
    """Test that checkpoint flushes at specified intervals."""
    manager = CheckpointManager.from_uri(str(temp_checkpoint_file), flush_interval=2)

    # Write pages
    for i in range(3):
        page = Page(
            url=f"https://example.com/{i}",
            title=f"Page {i}",
            depth=0,
        )
        await manager.write_page(page)

    # Don't close yet - just flush should happen automatically
    # After 2 pages, data should be flushed
    await manager.close()

    # Verify all pages were written
    with open(temp_checkpoint_file, "r") as f:
        lines = f.readlines()
        assert len(lines) == 3


@pytest.mark.asyncio
async def test_checkpoint_load_empty():
    """Test loading non-existent checkpoint."""
    manager = CheckpointManager.from_uri("nonexistent.jsonl")
    data = await manager.load()

    assert data["metadata"] is None
    assert len(data["pages"]) == 0
    assert data["state"] is None


@pytest.mark.asyncio
async def test_checkpoint_multiple_pages(temp_checkpoint_file):
    """Test writing and loading multiple pages."""
    manager = CheckpointManager.from_uri(str(temp_checkpoint_file))

    # Write multiple pages
    pages = []
    for i in range(5):
        page = Page(
            url=f"https://example.com/page{i}",
            title=f"Page {i}",
            text=f"Content {i}",
            depth=i,
        )
        pages.append(page)
        await manager.write_page(page)

    await manager.close()

    # Load and verify
    manager2 = CheckpointManager.from_uri(str(temp_checkpoint_file))
    data = await manager2.load()
    await manager2.close()

    assert len(data["pages"]) == 5
    for i, page in enumerate(data["pages"]):
        assert page.url == f"https://example.com/page{i}"
        assert page.title == f"Page {i}"
        assert page.depth == i
