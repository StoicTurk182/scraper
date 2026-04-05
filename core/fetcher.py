"""
HTTP fetch logic with error handling and encoding detection.

Uses the requests library to fetch web page HTML content.
Handles redirects, encoding detection, and common HTTP errors.

Reference: https://docs.python-requests.org/en/latest/
"""

import requests
from urllib.parse import urlparse


class PageFetcher:
    """Fetches web page HTML content with proper headers and error handling."""

    # Mimic a standard browser to avoid basic bot-detection blocks.
    # Some sites return different content (or 403) for non-browser User-Agents.
    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
    }

    def __init__(self, timeout: int = 15):
        """
        Initialise the fetcher with a requests Session.

        Args:
            timeout: HTTP request timeout in seconds.
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)

    def fetch(self, url: str) -> dict:
        """
        Fetch a URL and return structured result data.

        Args:
            url: The full URL to fetch (must include scheme).

        Returns:
            Dict with keys: html, status_code, domain, final_url,
            content_type, content_length.

        Raises:
            requests.RequestException: On HTTP errors or connection failures.
        """
        response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
        response.raise_for_status()

        # Use apparent_encoding for better charset detection than
        # Content-Type header alone. This handles pages that declare
        # charset in meta tags or serve non-UTF8 without declaring it.
        response.encoding = response.apparent_encoding

        parsed = urlparse(response.url)

        return {
            "html": response.text,
            "status_code": response.status_code,
            "domain": parsed.netloc,
            "final_url": response.url,
            "content_type": response.headers.get("Content-Type", ""),
            "content_length": len(response.text),
        }

    def check_robots(self, url: str) -> bool:
        """
        Basic check if the URL path is allowed by robots.txt.

        This is a simplified check - it looks for Disallow rules
        that match the URL path. For production use, consider the
        robotparser module from urllib.

        Args:
            url: The URL to check.

        Returns:
            True if scraping appears to be allowed, False if explicitly blocked.
        """
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

        try:
            response = self.session.get(robots_url, timeout=5)
            if response.status_code != 200:
                # No robots.txt found - assume allowed
                return True

            path = parsed.path or "/"
            for line in response.text.split("\n"):
                line = line.strip().lower()
                if line.startswith("disallow:"):
                    disallowed = line.split(":", 1)[1].strip()
                    if disallowed and path.startswith(disallowed):
                        return False
            return True

        except requests.RequestException:
            # If we can't fetch robots.txt, assume allowed
            return True
