"""
Output path selection and Markdown file writing.

Handles prompting the user for an output directory,
generating safe filenames from page titles, and writing
the final Markdown file with a metadata header.

Reference: https://docs.python.org/3/library/os.path.html
"""

import os
import re
import json
from datetime import datetime


# Config file stores the user's last-used output directory
# so they don't have to re-enter it every time.
CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "config.json"
)


class FileHandler:
    """Manages output directory selection and Markdown file writing."""

    def __init__(self, default_output_dir: str = None):
        """
        Initialise the file handler.

        Args:
            default_output_dir: Override default output directory.
                                If None, uses ~/Documents/WebScrapes
                                or the last-used directory from config.
        """
        if default_output_dir:
            self.default_output_dir = os.path.abspath(default_output_dir)
        else:
            self.default_output_dir = self._load_default_dir()

    def _load_default_dir(self) -> str:
        """Load the last-used output directory from config, or use fallback."""
        config_path = os.path.abspath(CONFIG_FILE)
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
                    saved = config.get("output_dir", "")
                    if saved and os.path.isdir(saved):
                        return saved
            except (json.JSONDecodeError, IOError):
                pass

        # Fallback: ~/Documents/WebScrapes
        return os.path.join(os.path.expanduser("~"), "Documents", "WebScrapes")

    def _save_default_dir(self, directory: str):
        """Persist the chosen output directory to config for next run."""
        config_path = os.path.abspath(CONFIG_FILE)
        config = {}
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        config["output_dir"] = directory
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

    def prompt_output_location(self) -> str:
        """
        Present the user with the current default output directory and
        offer the choice to use it or specify a different path.

        Returns:
            The selected output directory path (created if it doesn't exist).
        """
        print(f"\n  Output directory: {self.default_output_dir}")
        print("  [1] Use this location")
        print("  [2] Choose a different location")
        print()

        choice = input("  Select [1/2]: ").strip()

        if choice == "2":
            new_path = input("  Enter full path: ").strip()
            if new_path:
                output_dir = os.path.abspath(new_path)
            else:
                print("  No path entered, using default.")
                output_dir = self.default_output_dir
        else:
            output_dir = self.default_output_dir

        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Save this choice for next time
        self._save_default_dir(output_dir)

        return output_dir

    def generate_filename(self, title: str, url: str = "") -> str:
        """
        Generate a filesystem-safe filename from the page title.

        Format: {sanitised-title}_{YYYYMMDD-HHMMSS}.md

        Args:
            title: Page title to derive filename from.
            url:   Original URL (unused currently, reserved for future use).

        Returns:
            A safe filename string ending in .md.
        """
        # Remove characters that are unsafe in filenames
        safe_title = re.sub(r"[^\w\s-]", "", title)

        # Replace whitespace runs with single hyphen
        safe_title = re.sub(r"[\s]+", "-", safe_title).strip("-").lower()

        # Truncate to avoid filesystem path length issues
        safe_title = safe_title[:80]

        # If title was entirely special characters, use fallback
        if not safe_title:
            safe_title = "scraped-page"

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        return f"{safe_title}_{timestamp}.md"

    def write_markdown(self, output_dir: str, filename: str,
                       markdown: str, url: str, title: str,
                       meta_description: str = "") -> str:
        """
        Write Markdown content to a file with a source metadata header.

        The header block at the top of the file records where and when
        the content was scraped, providing traceability.

        Args:
            output_dir:       Directory to write the file into.
            filename:         The filename (from generate_filename).
            markdown:         The converted Markdown content.
            url:              Original source URL.
            title:            Page title.
            meta_description: Optional meta description from the page.

        Returns:
            Full path to the written file.
        """
        filepath = os.path.join(output_dir, filename)

        # Build the metadata header
        header_lines = [
            f"# {title}",
            "",
            f"Source: {url}  ",
            f"Scraped: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
        ]

        if meta_description:
            header_lines.append(f"Description: {meta_description}  ")

        header_lines.extend(["", "---", ""])

        header = "\n".join(header_lines)
        full_content = header + "\n" + markdown

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(full_content)

        return filepath
