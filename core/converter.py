"""
HTML to Markdown conversion with content cleaning.

Uses BeautifulSoup for HTML parsing and element removal,
then markdownify for the actual HTML-to-Markdown conversion.

References:
    - BeautifulSoup: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
    - markdownify: https://pypi.org/project/markdownify/
"""

import re
from bs4 import BeautifulSoup, Comment
from markdownify import markdownify as md


class HtmlToMarkdown:
    """Converts raw HTML to clean, formatted Markdown."""

    # HTML elements that never contain useful article content.
    # These are removed from the DOM before conversion.
    STRIP_TAGS = [
        "nav", "footer", "header", "aside", "script", "style",
        "noscript", "iframe", "form", "button", "svg", "canvas",
        "video", "audio", "object", "embed",
    ]

    # CSS class name fragments that typically indicate non-content elements.
    # Matched case-insensitively against each element's class list.
    STRIP_CLASSES = [
        "sidebar", "menu", "nav", "footer", "header", "ad",
        "advertisement", "social", "share", "comment", "cookie",
        "popup", "modal", "banner", "newsletter", "signup",
        "related", "recommended", "widget", "toolbar",
    ]

    # CSS selectors for common non-content containers
    STRIP_SELECTORS = [
        '[role="navigation"]',
        '[role="banner"]',
        '[role="complementary"]',
        '[aria-hidden="true"]',
        ".breadcrumb",
        ".pagination",
        ".toc",  # table of contents (often clutters output)
    ]

    def convert(self, html: str, keep_images: bool = False) -> dict:
        """
        Parse HTML and convert to clean Markdown.

        Args:
            html:        Raw HTML string.
            keep_images: If True, preserve image markdown links.
                         Defaults to False (strips images).

        Returns:
            Dict with keys: markdown, title, word_count, link_count.
        """
        soup = BeautifulSoup(html, "lxml")

        # Extract metadata before stripping
        title = self._extract_title(soup)
        meta_description = self._extract_meta_description(soup)

        # Remove non-content elements
        self._strip_comments(soup)
        self._strip_elements(soup)

        # Target main content area if identifiable
        content = self._find_main_content(soup)

        # Configure markdownify options.
        # Note: markdownify does not allow both 'strip' and 'convert'
        # parameters simultaneously. We use 'strip' to remove unwanted
        # elements and let all other tags convert to Markdown by default.
        md_options = {
            "heading_style": "ATX",
            "bullets": "-",
        }

        if not keep_images:
            md_options["strip"] = ["img"]

        # Convert to markdown
        markdown_text = md(str(content), **md_options)

        # Post-processing cleanup
        markdown_text = self._clean_markdown(markdown_text)

        # Count useful metrics
        word_count = len(markdown_text.split())
        link_count = markdown_text.count("](")

        return {
            "markdown": markdown_text,
            "title": title,
            "meta_description": meta_description,
            "word_count": word_count,
            "link_count": link_count,
        }

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title from <title> tag or first <h1>."""
        title_tag = soup.find("title")
        if title_tag and title_tag.string:
            # Many titles include " - Site Name" suffix - keep it for now
            return title_tag.string.strip()
        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)
        return "Untitled"

    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description if present."""
        meta = soup.find("meta", attrs={"name": "description"})
        if meta and meta.get("content"):
            return meta["content"].strip()
        return ""

    def _strip_comments(self, soup: BeautifulSoup):
        """Remove HTML comments from the DOM."""
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

    def _strip_elements(self, soup: BeautifulSoup):
        """Remove non-content elements from the DOM."""
        # Remove by tag name
        for tag_name in self.STRIP_TAGS:
            for tag in soup.find_all(tag_name):
                tag.decompose()

        # Remove by CSS class (case-insensitive partial match)
        for class_fragment in self.STRIP_CLASSES:
            for tag in soup.find_all(
                class_=lambda c: c and class_fragment in " ".join(c).lower()
            ):
                tag.decompose()

        # Remove by CSS selector
        for selector in self.STRIP_SELECTORS:
            for tag in soup.select(selector):
                tag.decompose()

        # Remove empty divs and spans that add nothing
        for tag in soup.find_all(["div", "span"]):
            if not tag.get_text(strip=True) and not tag.find_all(["img", "table"]):
                tag.decompose()

    def _find_main_content(self, soup: BeautifulSoup) -> BeautifulSoup:
        """
        Attempt to locate the main content container.

        Tries semantic HTML5 elements first, then common class/ID
        patterns used by CMSs and documentation sites.
        Falls back to <body> if nothing specific is found.
        """
        # Priority-ordered list of selectors for main content
        selectors = [
            "main",
            "article",
            '[role="main"]',
            "#content",
            "#main-content",
            "#main",
            ".content",
            ".main",
            ".post-content",
            ".entry-content",
            ".article-body",
            ".article-content",
            ".page-content",
            ".doc-content",
            ".markdown-body",       # GitHub
            ".mw-parser-output",    # MediaWiki / Wikipedia
            "#bodyContent",         # MediaWiki
            ".prose",               # Tailwind prose class
        ]

        for selector in selectors:
            found = soup.select_one(selector)
            if found and len(found.get_text(strip=True)) > 100:
                return found

        # Fallback to body
        body = soup.find("body")
        return body if body else soup

    def _clean_markdown(self, text: str) -> str:
        """
        Post-process the markdown output to remove artifacts.

        Handles excessive blank lines, trailing whitespace,
        broken link formatting, and other conversion artefacts.
        """
        # Replace non-breaking spaces with regular spaces
        text = text.replace("\u00a0", " ")

        # Remove lines that are just whitespace
        text = re.sub(r"^[ \t]+$", "", text, flags=re.MULTILINE)

        # Collapse 3+ consecutive blank lines down to 2
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Remove trailing whitespace from each line
        lines = [line.rstrip() for line in text.split("\n")]

        # Remove leading blank lines
        while lines and lines[0] == "":
            lines.pop(0)

        # Remove trailing blank lines
        while lines and lines[-1] == "":
            lines.pop()

        return "\n".join(lines)
