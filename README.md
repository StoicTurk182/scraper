# web-scraper-md

Scrape web pages, convert to formatted Markdown, log metadata to SQLite.

## Quick Start

```bash
# Clone / copy the project
cd web-scraper-md

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1    # Windows
# source venv/bin/activate     # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Scrape a page
python scraper.py https://example.com/article
```

## Usage

```bash
python scraper.py <url>                             # Scrape with output prompt
python scraper.py <url> -o ~/Documents/Scrapes      # Set output directory
python scraper.py <url> -o ~/Documents/Scrapes -q   # Quiet mode (no prompts)
python scraper.py <url> --images                    # Keep image links
python scraper.py <url> --robots                    # Check robots.txt first
python scraper.py --batch urls.txt -o ./output      # Batch scrape from file
python scraper.py --history                         # View scrape log
python scraper.py --stats                           # View statistics
python scraper.py --search microsoft                # Search history
```

## Project Structure

```
web-scraper-md/
├── scraper.py           # CLI entry point
├── requirements.txt     # Python dependencies
├── scrapes.db           # SQLite database (created at runtime)
├── config.json          # Saved output directory (created at runtime)
└── core/
    ├── __init__.py
    ├── fetcher.py       # HTTP request handling
    ├── converter.py     # HTML parsing and Markdown conversion
    ├── database.py      # SQLite logging
    └── file_handler.py  # Output path and file writing
```

## Requirements

- Python 3.9+
- requests
- beautifulsoup4
- markdownify
- lxml

## References

- requests: https://docs.python-requests.org/en/latest/
- BeautifulSoup: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- markdownify: https://pypi.org/project/markdownify/
- sqlite3: https://docs.python.org/3/library/sqlite3.html
- argparse: https://docs.python.org/3/library/argparse.html
