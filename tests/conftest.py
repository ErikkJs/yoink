"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def sample_html():
    """Sample HTML for testing."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
        <meta name="description" content="A test page">
        <meta property="og:title" content="Test OG Title">
    </head>
    <body>
        <h1>Welcome</h1>
        <p>This is a test page with some content.</p>
        <a href="/page1">Page 1</a>
        <a href="/page2">Page 2</a>
        <a href="https://external.com">External</a>
    </body>
    </html>
    """


@pytest.fixture
def sample_url():
    """Sample base URL for testing."""
    return "https://example.com"
