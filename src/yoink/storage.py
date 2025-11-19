"""Storage backends for checkpoint persistence."""

import aiofiles
from abc import ABC, abstractmethod
from pathlib import Path
from typing import AsyncIterator, Optional
import structlog

logger = structlog.get_logger()


class CheckpointStorage(ABC):
    """Abstract storage backend for checkpoints."""

    @abstractmethod
    async def write(self, data: str) -> None:
        """
        Append data to checkpoint.

        Args:
            data: String data to append (should include newline if needed)
        """
        pass

    @abstractmethod
    async def read(self) -> AsyncIterator[str]:
        """
        Read checkpoint line by line.

        Yields:
            Lines from checkpoint file
        """
        pass

    @abstractmethod
    async def exists(self) -> bool:
        """
        Check if checkpoint exists.

        Returns:
            True if checkpoint exists, False otherwise
        """
        pass

    @abstractmethod
    async def flush(self) -> None:
        """Ensure all buffered data is persisted to storage."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close storage and release resources."""
        pass


class LocalFileStorage(CheckpointStorage):
    """Local filesystem storage backend."""

    def __init__(self, path: str):
        """
        Initialize local file storage.

        Args:
            path: Local file path
        """
        self.path = Path(path)
        self._file_handle: Optional[aiofiles.threadpool.text.AsyncTextIOWrapper] = None
        logger.info("local_storage_init", path=str(self.path))

    async def write(self, data: str) -> None:
        """Append data to local file."""
        if self._file_handle is None:
            # Open in append mode, create if doesn't exist
            self._file_handle = await aiofiles.open(self.path, mode="a", encoding="utf-8")

        await self._file_handle.write(data)
        logger.debug("local_storage_write", bytes=len(data))

    async def read(self) -> AsyncIterator[str]:
        """Read file line by line."""
        if not await self.exists():
            return

        async with aiofiles.open(self.path, mode="r", encoding="utf-8") as f:
            async for line in f:
                yield line

    async def exists(self) -> bool:
        """Check if file exists."""
        return self.path.exists()

    async def flush(self) -> None:
        """Flush file buffer to disk."""
        if self._file_handle is not None:
            await self._file_handle.flush()

    async def close(self) -> None:
        """Close file handle."""
        if self._file_handle is not None:
            await self._file_handle.close()
            self._file_handle = None


class S3Storage(CheckpointStorage):
    """AWS S3 storage backend."""

    def __init__(self, uri: str):
        """
        Initialize S3 storage.

        Args:
            uri: S3 URI in format s3://bucket/key/path
        """
        self.uri = uri
        self._parse_uri(uri)
        self._buffer: list[str] = []
        self._client: Optional[any] = None
        logger.info("s3_storage_init", bucket=self.bucket, key=self.key)

    def _parse_uri(self, uri: str) -> None:
        """Parse S3 URI into bucket and key."""
        if not uri.startswith("s3://"):
            raise ValueError(f"Invalid S3 URI: {uri}")

        # Remove s3:// prefix
        path = uri[5:]

        # Split into bucket and key
        parts = path.split("/", 1)
        if len(parts) < 2:
            raise ValueError(f"Invalid S3 URI format: {uri}. Expected s3://bucket/key")

        self.bucket = parts[0]
        self.key = parts[1]

    async def _get_client(self):
        """Lazy load aioboto3 client."""
        if self._client is None:
            try:
                import aioboto3
            except ImportError:
                raise ImportError(
                    "aioboto3 is required for S3 storage. Install with: pip install 'yoink[s3]' or pip install aioboto3"
                )

            try:
                session = aioboto3.Session()
                self._client = session.client("s3")
            except Exception as e:
                raise RuntimeError(
                    f"Failed to create S3 client: {e}\n\n"
                    "AWS credentials are required for S3 storage. Configure them using:\n"
                    "  1. AWS CLI: aws configure\n"
                    "  2. Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY\n"
                    "  3. IAM role (if running on AWS infrastructure)\n\n"
                    "For more info: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html"
                )

        return self._client

    async def write(self, data: str) -> None:
        """
        Buffer data for S3 upload.

        Data is buffered locally and uploaded on flush() to minimize S3 API calls.
        """
        self._buffer.append(data)
        logger.debug("s3_storage_buffer", bytes=len(data), buffer_size=len(self._buffer))

    async def read(self) -> AsyncIterator[str]:
        """Read checkpoint from S3 line by line."""
        if not await self.exists():
            return

        client = await self._get_client()

        async with client as s3:
            try:
                # Get object from S3
                response = await s3.get_object(Bucket=self.bucket, Key=self.key)

                # Read body line by line
                async with response["Body"] as stream:
                    # Read entire content and split by lines
                    content = await stream.read()
                    text = content.decode("utf-8")

                    for line in text.splitlines(keepends=True):
                        yield line

                logger.info("s3_storage_read", bucket=self.bucket, key=self.key)

            except Exception as e:
                logger.error("s3_storage_read_error", error=str(e))
                raise

    async def exists(self) -> bool:
        """Check if S3 object exists."""
        client = await self._get_client()

        async with client as s3:
            try:
                await s3.head_object(Bucket=self.bucket, Key=self.key)
                return True
            except s3.exceptions.NoSuchKey:
                return False
            except Exception:
                return False

    async def flush(self) -> None:
        """Upload buffered data to S3."""
        if not self._buffer:
            return

        client = await self._get_client()

        async with client as s3:
            try:
                # Combine buffered data
                data = "".join(self._buffer)

                # Check if object exists to append or create
                existing_data = ""
                if await self.exists():
                    # Download existing content
                    response = await s3.get_object(Bucket=self.bucket, Key=self.key)
                    async with response["Body"] as stream:
                        content = await stream.read()
                        existing_data = content.decode("utf-8")

                # Combine existing and new data
                combined_data = existing_data + data

                # Upload combined data
                await s3.put_object(
                    Bucket=self.bucket, Key=self.key, Body=combined_data.encode("utf-8")
                )

                logger.info(
                    "s3_storage_flush",
                    bucket=self.bucket,
                    key=self.key,
                    bytes=len(data),
                    lines=len(self._buffer),
                )

                # Clear buffer
                self._buffer.clear()

            except Exception as e:
                logger.error("s3_storage_flush_error", error=str(e))
                raise

    async def close(self) -> None:
        """Flush remaining data and close S3 client."""
        # Flush any remaining buffered data
        if self._buffer:
            await self.flush()

        # aioboto3 session cleanup is handled by context manager
        self._client = None


class StorageFactory:
    """Factory for creating storage backends from URIs."""

    @staticmethod
    def from_uri(uri: str) -> CheckpointStorage:
        """
        Create appropriate storage backend from URI.

        Args:
            uri: Storage URI (file path, s3://, etc.)

        Returns:
            CheckpointStorage instance

        Examples:
            - './checkpoint.jsonl' -> LocalFileStorage
            - 's3://bucket/checkpoint.jsonl' -> S3Storage
        """
        if uri.startswith("s3://"):
            return S3Storage(uri)
        else:
            # Treat as local file path
            return LocalFileStorage(uri)
