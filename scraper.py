#!/usr/bin/env python3
"""
Web Scraper to Markdown

Scrapes web pages, converts HTML content to formatted Markdown files,
and logs all scrape metadata to an embedded SQLite database.

Usage:
    python scraper.py <url>                           # Scrape with output prompt
    python scraper.py <url> -o /path/to/dir           # Scrape to specific directory
    python scraper.py <url> -o /path/to/dir --quiet   # No prompts, no verbose output
    python scraper.py --history                        # Show scrape history
    python scraper.py --stats                          # Show scrape statistics
    python scraper.py --search microsoft               # Search scrape history

Reference:
    argparse: https://docs.python.org/3/library/argparse.html
"""

import argparse
import sys
import os
from urllib.parse import urlparse

from core.fetcher import PageFetcher
from core.converter import HtmlToMarkdown
from core.database import ScrapeDatabase
from core.file_handler import FileHandler


# ============================================================================
# DISPLAY HELPERS
# ============================================================================

def print_banner():
    """Print application banner."""
    print()
    print("=" * 60)
    print("  Web Scraper to Markdown")
    print("  Scrape - Convert - Save - Log")
    print("=" * 60)


def print_success(filepath: str, file_size: int, word_count: int, title: str):
    """Print success summary after a scrape."""
    print()
    print(f"  Title:    {title}")
    print(f"  Words:    {word_count:,}")
    print(f"  Size:     {file_size:,} bytes")
    print(f"  Saved to: {filepath}")
    print()


def print_error(message: str):
    """Print an error message."""
    print(f"\n  ERROR: {message}\n", file=sys.stderr)


# ============================================================================
# CORE OPERATIONS
# ============================================================================

def scrape(url: str, output_dir: str = None, quiet: bool = False,
           keep_images: bool = False, check_robots: bool = False):
    """
    Execute the full scrape pipeline for a single URL.

    Steps:
        1. Optionally check robots.txt
        2. Fetch the page HTML
        3. Convert HTML to Markdown
        4. Prompt user for output location (unless quiet mode)
        5. Write the .md file
        6. Log the scrape to the database

    Args:
        url:          Full URL to scrape.
        output_dir:   Pre-set output directory (skips prompt if quiet=True).
        quiet:        If True, skip all interactive prompts.
        keep_images:  If True, preserve image links in output.
        check_robots: If True, check robots.txt before scraping.

    Returns:
        True on success, False on failure.
    """
    db = ScrapeDatabase()
    fetcher = PageFetcher()
    converter = HtmlToMarkdown()
    handler = FileHandler(default_output_dir=output_dir)

    # Step 1: Optional robots.txt check
    if check_robots:
        if not quiet:
            print(f"\n  Checking robots.txt for {url}...")
        if not fetcher.check_robots(url):
            print_error(f"robots.txt disallows scraping this path: {url}")
            db.log_scrape(
                url=url, title=None, domain=urlparse(url).netloc,
                output_path="", file_size=0,
                status="error", error_msg="Blocked by robots.txt"
            )
            return False

    # Step 2: Determine output location
    if quiet and output_dir:
        target_dir = output_dir
        os.makedirs(target_dir, exist_ok=True)
    else:
        target_dir = handler.prompt_output_location()

    if not quiet:
        print(f"\n  Fetching: {url}")

    try:
        # Step 3: Fetch page
        result = fetcher.fetch(url)
        if not quiet:
            print(f"  Status:   {result['status_code']}")
            print(f"  Domain:   {result['domain']}")
            print(f"  Size:     {result['content_length']:,} chars")

        # Step 4: Convert to Markdown
        converted = converter.convert(result["html"], keep_images=keep_images)

        if converted["word_count"] < 10:
            print_error(
                "Extracted content is very short (< 10 words). "
                "The page may require JavaScript rendering or use "
                "a structure this tool cannot parse."
            )

        # Step 5: Write file
        filename = handler.generate_filename(converted["title"], url)
        filepath = handler.write_markdown(
            output_dir=target_dir,
            filename=filename,
            markdown=converted["markdown"],
            url=url,
            title=converted["title"],
            meta_description=converted.get("meta_description", ""),
        )
        file_size = os.path.getsize(filepath)

        # Step 6: Log to database
        db.log_scrape(
            url=url,
            title=converted["title"],
            domain=result["domain"],
            output_path=filepath,
            file_size=file_size,
        )

        if not quiet:
            print_success(filepath, file_size, converted["word_count"],
                          converted["title"])

        return True

    except Exception as e:
        print_error(str(e))
        db.log_scrape(
            url=url,
            title=None,
            domain=urlparse(url).netloc,
            output_path="",
            file_size=0,
            status="error",
            error_msg=str(e),
        )
        return False


def batch_scrape(file_path: str, output_dir: str = None, keep_images: bool = False):
    """
    Scrape multiple URLs from a text file (one URL per line).

    Args:
        file_path:   Path to a .txt file containing URLs.
        output_dir:  Output directory for all scraped files.
        keep_images: If True, preserve image links in output.
    """
    if not os.path.exists(file_path):
        print_error(f"File not found: {file_path}")
        return

    with open(file_path, "r") as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    if not urls:
        print_error("No URLs found in file.")
        return

    print(f"\n  Batch scraping {len(urls)} URLs...")

    # Determine output directory once
    handler = FileHandler(default_output_dir=output_dir)
    if output_dir:
        target_dir = output_dir
        os.makedirs(target_dir, exist_ok=True)
    else:
        target_dir = handler.prompt_output_location()

    success_count = 0
    fail_count = 0

    for i, url in enumerate(urls, 1):
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        print(f"\n  [{i}/{len(urls)}] {url}")
        result = scrape(url, output_dir=target_dir, quiet=True, keep_images=keep_images)

        if result:
            success_count += 1
            print(f"    OK")
        else:
            fail_count += 1
            print(f"    FAILED")

    print(f"\n  Batch complete: {success_count} succeeded, {fail_count} failed\n")


# ============================================================================
# HISTORY AND REPORTING
# ============================================================================

def show_history(limit: int = 20):
    """Display recent scrape history from the database."""
    db = ScrapeDatabase()
    records = db.get_history(limit)

    if not records:
        print("\n  No scrape history found.\n")
        return

    print(f"\n  {'ID':<5} {'Date':<12} {'Time':<10} {'Status':<8} "
          f"{'Domain':<30} {'Title'}")
    print("  " + "-" * 95)

    for r in records:
        title = (r["title"] or "N/A")[:40]
        domain = (r["domain"] or "N/A")[:28]
        print(f"  {r['id']:<5} {r['scrape_date']:<12} {r['scrape_time']:<10} "
              f"{r['status']:<8} {domain:<30} {title}")

    print()


def show_stats():
    """Display summary statistics from the database."""
    db = ScrapeDatabase()
    stats = db.get_stats()

    if stats["total_scrapes"] == 0:
        print("\n  No scrape history found.\n")
        return

    total_mb = stats["total_bytes"] / (1024 * 1024)

    print()
    print(f"  Total scrapes:    {stats['total_scrapes']}")
    print(f"  Successful:       {stats['successful']}")
    print(f"  Failed:           {stats['failed']}")
    print(f"  Unique domains:   {stats['unique_domains']}")
    print(f"  Total output:     {total_mb:.2f} MB")
    print(f"  First scrape:     {stats['first_scrape']}")
    print(f"  Last scrape:      {stats['last_scrape']}")
    print()


def search_history(keyword: str, limit: int = 20):
    """Search scrape history by keyword."""
    db = ScrapeDatabase()
    records = db.search(keyword, limit)

    if not records:
        print(f"\n  No results found for: {keyword}\n")
        return

    print(f"\n  Results for '{keyword}':")
    print(f"\n  {'ID':<5} {'Date':<12} {'Status':<8} "
          f"{'Domain':<30} {'Title'}")
    print("  " + "-" * 85)

    for r in records:
        title = (r["title"] or "N/A")[:40]
        domain = (r["domain"] or "N/A")[:28]
        print(f"  {r['id']:<5} {r['scrape_date']:<12} "
              f"{r['status']:<8} {domain:<30} {title}")

    print()


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Scrape web pages and convert to formatted Markdown files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python scraper.py https://example.com/article
  python scraper.py https://example.com -o ~/Documents/Scrapes
  python scraper.py --batch urls.txt -o ~/Documents/Scrapes
  python scraper.py --history
  python scraper.py --stats
  python scraper.py --search microsoft
        """,
    )

    # Positional
    parser.add_argument(
        "url", nargs="?",
        help="URL to scrape",
    )

    # Output options
    parser.add_argument(
        "--output", "-o",
        help="Output directory path",
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true",
        help="Suppress interactive prompts and verbose output",
    )
    parser.add_argument(
        "--images", action="store_true",
        help="Keep image links in the output Markdown",
    )
    parser.add_argument(
        "--robots", action="store_true",
        help="Check robots.txt before scraping",
    )

    # Batch mode
    parser.add_argument(
        "--batch", "-b",
        help="Path to a text file with one URL per line",
    )

    # History and reporting
    parser.add_argument(
        "--history", action="store_true",
        help="Show recent scrape history",
    )
    parser.add_argument(
        "--stats", action="store_true",
        help="Show scrape statistics",
    )
    parser.add_argument(
        "--search", "-s",
        help="Search scrape history by keyword",
    )

    args = parser.parse_args()

    # Route to the correct operation
    if args.history:
        show_history()
        return

    if args.stats:
        show_stats()
        return

    if args.search:
        search_history(args.search)
        return

    if args.batch:
        print_banner()
        batch_scrape(args.batch, output_dir=args.output, keep_images=args.images)
        return

    if not args.url:
        parser.print_help()
        sys.exit(1)

    # Ensure URL has a scheme
    url = args.url
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    print_banner()
    success = scrape(
        url,
        output_dir=args.output,
        quiet=args.quiet,
        keep_images=args.images,
        check_robots=args.robots,
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
