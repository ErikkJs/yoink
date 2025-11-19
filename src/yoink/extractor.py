"""Content extraction using trafilatura."""

from typing import Optional
import trafilatura
import structlog

logger = structlog.get_logger()


class Extractor:
    """Extracts clean text content from HTML."""

    def extract(self, html: str, url: str) -> Optional[str]:
        """
        Extract main text content from HTML.

        Args:
            html: Raw HTML content
            url: Source URL (used for logging)

        Returns:
            Extracted text or None if extraction fails
        """
        try:
            text = trafilatura.extract(
                html,
                include_comments=False,
                include_tables=True,
                no_fallback=False,
            )

            if text:
                logger.debug(
                    "text_extracted",
                    url=url,
                    length=len(text),
                )
            else:
                logger.warning("extraction_failed", url=url)

            return text

        except Exception as e:
            logger.error("extraction_error", url=url, error=str(e))
            return None
