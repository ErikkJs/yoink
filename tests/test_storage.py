"""Tests for storage backends."""

import pytest
from pathlib import Path

from yoink.storage import LocalFileStorage, S3Storage, StorageFactory


@pytest.fixture
def temp_file(tmp_path):
    """Create a temporary file path."""
    return tmp_path / "test_storage.txt"


@pytest.mark.asyncio
async def test_local_storage_write_and_read(temp_file):
    """Test writing and reading from local storage."""
    storage = LocalFileStorage(str(temp_file))

    # Write data
    await storage.write("Line 1\n")
    await storage.write("Line 2\n")
    await storage.write("Line 3\n")
    await storage.flush()
    await storage.close()

    # Read data
    storage2 = LocalFileStorage(str(temp_file))
    lines = []
    async for line in storage2.read():
        lines.append(line.strip())
    await storage2.close()

    assert lines == ["Line 1", "Line 2", "Line 3"]


@pytest.mark.asyncio
async def test_local_storage_exists(temp_file):
    """Test checking if local file exists."""
    storage = LocalFileStorage(str(temp_file))

    # Should not exist initially
    assert not await storage.exists()

    # Write something
    await storage.write("test\n")
    await storage.close()

    # Should exist now
    storage2 = LocalFileStorage(str(temp_file))
    assert await storage2.exists()
    await storage2.close()


@pytest.mark.asyncio
async def test_local_storage_append(temp_file):
    """Test appending to existing file."""
    # First write
    storage1 = LocalFileStorage(str(temp_file))
    await storage1.write("Line 1\n")
    await storage1.close()

    # Append more
    storage2 = LocalFileStorage(str(temp_file))
    await storage2.write("Line 2\n")
    await storage2.close()

    # Read all
    storage3 = LocalFileStorage(str(temp_file))
    lines = []
    async for line in storage3.read():
        lines.append(line.strip())
    await storage3.close()

    assert lines == ["Line 1", "Line 2"]


@pytest.mark.asyncio
async def test_local_storage_flush():
    """Test flushing local storage."""
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        temp_path = f.name

    try:
        storage = LocalFileStorage(temp_path)
        await storage.write("test data\n")
        await storage.flush()

        # Data should be flushed to disk
        with open(temp_path, "r") as f:
            content = f.read()
            assert content == "test data\n"

        await storage.close()
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_s3_storage_uri_parsing():
    """Test S3 URI parsing."""
    storage = S3Storage("s3://my-bucket/path/to/file.jsonl")

    assert storage.bucket == "my-bucket"
    assert storage.key == "path/to/file.jsonl"


def test_s3_storage_invalid_uri():
    """Test S3 storage with invalid URI."""
    with pytest.raises(ValueError, match="Invalid S3 URI"):
        S3Storage("https://example.com/file.txt")

    with pytest.raises(ValueError, match="Invalid S3 URI format"):
        S3Storage("s3://bucket-only")


def test_storage_factory_local():
    """Test factory creates local storage for file paths."""
    storage = StorageFactory.from_uri("/path/to/file.jsonl")
    assert isinstance(storage, LocalFileStorage)

    storage = StorageFactory.from_uri("./relative/path.jsonl")
    assert isinstance(storage, LocalFileStorage)


def test_storage_factory_s3():
    """Test factory creates S3 storage for s3:// URIs."""
    storage = StorageFactory.from_uri("s3://bucket/key")
    assert isinstance(storage, S3Storage)
    assert storage.bucket == "bucket"
    assert storage.key == "key"


@pytest.mark.asyncio
async def test_local_storage_context_manager(temp_file):
    """Test using local storage as context manager."""
    storage = LocalFileStorage(str(temp_file))

    await storage.write("test\n")
    await storage.close()

    # Verify file was written
    assert temp_file.exists()
    with open(temp_file, "r") as f:
        assert f.read() == "test\n"
