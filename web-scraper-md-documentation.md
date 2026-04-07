# Web Scraper to Markdown - Documentation

A Python CLI application that scrapes web pages, converts HTML content to formatted Markdown files, and logs all scrape metadata to an embedded SQLite database.

Repository structure, installation, usage, and module reference.

## Project Structure

```
web-scraper-md/
├── scraper.py           # CLI entry point and pipeline orchestration
├── requirements.txt     # Python dependencies
├── README.md
├── scrapes.db           # SQLite database (auto-created at runtime)
├── config.json          # Persisted output directory (auto-created at runtime)
└── core/
    ├── __init__.py
    ├── fetcher.py       # HTTP request handling with encoding detection
    ├── converter.py     # HTML parsing, cleaning, and Markdown conversion
    ├── database.py      # SQLite scrape logging and query operations
    └── file_handler.py  # Output path selection, filename generation, file writing
```

## Data Flow

```
URL (user input)
    |
    v
fetcher.py --- HTTP GET ---> raw HTML (with redirect/encoding handling)
    |
    v
converter.py --- BeautifulSoup ---> strip nav/ads/scripts ---> find main content
    |                                                               |
    |                                                               v
    |                                              markdownify ---> clean Markdown string
    |
    v
file_handler.py --- prompt for output path ---> write .md file with metadata header
    |
    v
database.py --- INSERT ---> scrapes.db (URL, title, domain, date, time, path, size, status)
```

## Installation

### Prerequisites

Python 3.9 or later:

```powershell
python --version
```

### Setup

```powershell
cd web-scraper-md

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

The `requirements.txt` uses minimum version constraints for flexibility:

```
requests>=2.31.0
beautifulsoup4>=4.12.0
markdownify>=0.13.1
lxml>=5.0.0
```

A `requirements-pinned.txt` is also included with exact tested versions for reproducible builds:

```
pip install -r requirements-pinned.txt
```

### Verified Dependencies

Tested and verified on Python 3.12.3 on 2026-04-05.

| Package | Type | Verified Version | Purpose |
|---------|------|-----------------|---------|
| requests | Direct | 2.33.0 | HTTP client |
| beautifulsoup4 | Direct | 4.14.3 | HTML parser |
| markdownify | Direct | 1.2.2 | HTML to Markdown converter |
| lxml | Direct | 6.0.2 | Fast XML/HTML parser backend |
| charset-normalizer | Transitive | 3.4.6 | Character encoding detection (requests) |
| idna | Transitive | 3.11 | Internationalized domain name handling (requests) |
| urllib3 | Transitive | 2.6.3 | HTTP connection pooling (requests) |
| certifi | Transitive | 2026.2.25 | TLS certificate bundle (requests) |
| soupsieve | Transitive | 2.8.3 | CSS selector engine (beautifulsoup4) |
| six | Transitive | 1.17.0 | Python 2/3 compatibility (markdownify) |
| typing-extensions | Transitive | 4.15.0 | Type hint backports (beautifulsoup4) |
| sqlite3 | Stdlib | built-in | Embedded database |
| argparse | Stdlib | built-in | CLI argument parsing |
| os / sys / re / json | Stdlib | built-in | File I/O, regex, config |
| datetime | Stdlib | built-in | Timestamps |
| urllib.parse | Stdlib | built-in | URL parsing |

## Usage

### Single URL Scrape

```bash
python scraper.py https://docs.microsoft.com/en-us/windows-server/get-started/whats-new
```

The application fetches the page, converts to Markdown, then prompts for the output location:

```
============================================================
  Web Scraper to Markdown
  Scrape - Convert - Save - Log
============================================================

  Output directory: C:\Users\Andrew\Documents\WebScrapes
  [1] Use this location
  [2] Choose a different location

  Select [1/2]:
```

The output directory choice is persisted to `config.json` so subsequent runs remember the last selection.

### Scrape with Pre-Set Output

```bash
python scraper.py https://example.com/article -o "D:\Obsidian\Reference"
```

### Quiet Mode (No Prompts)

```bash
python scraper.py https://example.com/article -o "D:\Obsidian\Reference" --quiet
```

### Keep Image Links

By default, image tags are stripped from the output. Use `--images` to preserve them as Markdown image links:

```bash
python scraper.py https://example.com/article --images
```

### Check robots.txt First

```bash
python scraper.py https://example.com/article --robots
```

### Batch Scrape

Create a text file with one URL per line (lines starting with `#` are ignored):

```
# urls.txt
https://docs.microsoft.com/en-us/article-1
https://docs.microsoft.com/en-us/article-2
https://learn.microsoft.com/en-us/article-3
```

Run:

```bash
python scraper.py --batch urls.txt -o "D:\Obsidian\Reference"
```

### View Scrape History

```bash
python scraper.py --history
```

Output:

```
  ID    Date         Time       Status   Domain                         Title
  -----------------------------------------------------------------------------------------------
  12    2026-04-05   14:32:01   success  docs.microsoft.com             What's New in Windows Server 2025
  11    2026-04-04   09:15:44   success  learn.microsoft.com            Configure Always On VPN
  10    2026-04-04   08:50:12   error    internal.example.com           N/A
```

### View Statistics

```bash
python scraper.py --stats
```

Output:

```
  Total scrapes:    42
  Successful:       39
  Failed:           3
  Unique domains:   12
  Total output:     1.84 MB
  First scrape:     2026-03-15 10:22:01
  Last scrape:      2026-04-05 14:32:01
```

### Search History

```bash
python scraper.py --search microsoft
```

## Output Format

Each scraped page produces a `.md` file with the following structure:

```markdown
# Page Title - Site Name

Source: https://example.com/original-url
Scraped: 2026-04-05 14:32:01
Description: Meta description if available

---

(converted Markdown content follows)
```

The metadata header provides traceability back to the source URL and scrape timestamp.

Filenames are generated as `{sanitised-title}_{YYYYMMDD-HHMMSS}.md`. Titles are lowercased, special characters removed, and spaces replaced with hyphens. Maximum 80 characters before truncation.

## Database Schema

The `scrapes.db` file is SQLite and can be queried directly with any SQLite client (DB Browser for SQLite, sqlite3 CLI, DBeaver, or Python).

```sql
CREATE TABLE IF NOT EXISTS scrapes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    url         TEXT NOT NULL,
    title       TEXT,
    domain      TEXT,
    scrape_date TEXT NOT NULL,   -- YYYY-MM-DD
    scrape_time TEXT NOT NULL,   -- HH:MM:SS
    output_path TEXT NOT NULL,
    file_size   INTEGER,        -- bytes
    status      TEXT DEFAULT 'success',
    error_msg   TEXT
);
```

### Direct Query Examples

```bash
sqlite3 scrapes.db "SELECT url, title, scrape_date FROM scrapes WHERE domain LIKE '%microsoft%' ORDER BY id DESC LIMIT 10;"
```

```bash
sqlite3 scrapes.db "SELECT domain, COUNT(*) as count FROM scrapes GROUP BY domain ORDER BY count DESC;"
```

## Module Reference

### core/fetcher.py - PageFetcher

Handles HTTP requests using the `requests` library with a persistent session.

| Method | Arguments | Returns | Purpose |
|--------|-----------|---------|---------|
| `__init__` | `timeout: int = 15` | - | Create session with browser-like headers |
| `fetch` | `url: str` | `dict` with html, status_code, domain, final_url, content_type, content_length | Fetch page with redirect following and encoding detection |
| `check_robots` | `url: str` | `bool` | Basic robots.txt Disallow check |

The User-Agent header mimics Chrome to avoid bot-detection blocks on sites that serve different content to non-browser clients.

Encoding detection uses `response.apparent_encoding` (chardet-based) rather than relying solely on the Content-Type header, which handles pages that declare charset in HTML meta tags or serve non-UTF8 without headers.

### core/converter.py - HtmlToMarkdown

Parses HTML with BeautifulSoup, strips non-content elements, locates the main content container, and converts to Markdown via markdownify.

| Method | Arguments | Returns | Purpose |
|--------|-----------|---------|---------|
| `convert` | `html: str, keep_images: bool = False` | `dict` with markdown, title, meta_description, word_count, link_count | Full conversion pipeline |

Content cleaning removes:

- HTML tags: `nav`, `footer`, `header`, `aside`, `script`, `style`, `noscript`, `iframe`, `form`, `button`, `svg`, `canvas`, `video`, `audio`, `object`, `embed`
- Elements with CSS classes containing: `sidebar`, `menu`, `nav`, `footer`, `header`, `ad`, `advertisement`, `social`, `share`, `comment`, `cookie`, `popup`, `modal`, `banner`, `newsletter`, `signup`, `related`, `recommended`, `widget`, `toolbar`
- ARIA/role selectors: `[role="navigation"]`, `[role="banner"]`, `[role="complementary"]`, `[aria-hidden="true"]`
- HTML comments
- Empty `div` and `span` elements

Main content detection tries these selectors in order: `main`, `article`, `[role="main"]`, `#content`, `#main-content`, `#main`, `.content`, `.main`, `.post-content`, `.entry-content`, `.article-body`, `.article-content`, `.page-content`, `.doc-content`, `.markdown-body` (GitHub), `.mw-parser-output` (MediaWiki), `#bodyContent` (MediaWiki), `.prose` (Tailwind). Falls back to `<body>` if none match.

### core/database.py - ScrapeDatabase

Wraps SQLite3 operations for the scrape log.

| Method | Arguments | Returns | Purpose |
|--------|-----------|---------|---------|
| `__init__` | `db_path: str = None` | - | Create/connect to database, auto-create table |
| `log_scrape` | url, title, domain, output_path, file_size, status, error_msg | - | Insert a scrape record |
| `get_history` | `limit: int = 20` | `list[dict]` | Most recent scrape records |
| `get_stats` | - | `dict` | Aggregate statistics |
| `search` | `keyword: str, limit: int = 20` | `list[dict]` | Search by URL, title, or domain |

All queries use parameterised statements (`?` placeholders) to prevent SQL injection. The database connection uses context managers (`with sqlite3.connect()`) for automatic commit on success and rollback on exception.

### core/file_handler.py - FileHandler

Manages output directory selection and Markdown file writing.

| Method | Arguments | Returns | Purpose |
|--------|-----------|---------|---------|
| `__init__` | `default_output_dir: str = None` | - | Load saved directory from config or use default |
| `prompt_output_location` | - | `str` (directory path) | Interactive directory selection |
| `generate_filename` | `title: str, url: str` | `str` (filename) | Safe filename from page title |
| `write_markdown` | output_dir, filename, markdown, url, title, meta_description | `str` (full filepath) | Write file with metadata header |

The chosen output directory is persisted to `config.json` so the user does not need to re-enter it on each run.

## Python Concepts Covered

| Concept | Where Used |
|---------|------------|
| HTTP requests and sessions | `fetcher.py` - GET requests, headers, encoding, error handling |
| HTML DOM parsing | `converter.py` - BeautifulSoup selectors, tree traversal, element removal |
| String manipulation and regex | `converter.py`, `file_handler.py` - text cleaning, filename sanitisation |
| File I/O | `file_handler.py` - writing files, creating directories, path handling |
| JSON config files | `file_handler.py` - reading/writing persistent application settings |
| SQL and databases | `database.py` - DDL, parameterised queries, aggregation, context managers |
| OOP and classes | All modules - encapsulation, constructors, methods, single responsibility |
| CLI argument parsing | `scraper.py` - argparse with positional args, flags, and subcommands |
| Exception handling | `scraper.py` - try/except with error logging to database |
| Standard library usage | `os`, `re`, `datetime`, `sqlite3`, `urllib.parse`, `json`, `sys` |
| Package structure | `core/` package with `__init__.py` and module separation |
| Context managers | `database.py` - `with sqlite3.connect()` for automatic commit/rollback |
| Type hints | All modules - function signatures with type annotations |

## Tested Conversion Example

Input HTML:

```html
<html>
<head><title>Test Article - My Site</title></head>
<body>
<nav><a href="/">Home</a></nav>
<main>
<h1>Understanding Python Virtual Environments</h1>
<p>Virtual environments isolate project dependencies.</p>
<h2>Creating a Virtual Environment</h2>
<pre><code>python -m venv .venv</code></pre>
<ul>
<li>Dependency isolation per project</li>
<li>Reproducible builds with requirements.txt</li>
</ul>
<table>
<tr><th>Command</th><th>Purpose</th></tr>
<tr><td>pip install</td><td>Add a package</td></tr>
<tr><td>pip freeze</td><td>List installed packages</td></tr>
</table>
</main>
<footer>Copyright 2026</footer>
</body>
</html>
```

Output Markdown:

```markdown
# Test Article - My Site

Source: https://example.com/test
Scraped: 2026-04-05 09:43:48
Description: A test article.

---

# Understanding Python Virtual Environments

Virtual environments isolate project dependencies.

## Creating a Virtual Environment

    python -m venv .venv

- Dependency isolation per project
- Reproducible builds with requirements.txt

| Command | Purpose |
| --- | --- |
| pip install | Add a package |
| pip freeze | List installed packages |
```

Navigation and footer elements were stripped. Headings, code blocks, lists, and tables all converted correctly.

## Limitations

| Limitation | Cause | Mitigation |
|------------|-------|------------|
| JavaScript-rendered content not captured | `requests` fetches raw HTML only | Use `playwright` for SPA sites |
| Some sites block scraping | Anti-bot measures, rate limiting | Respect `robots.txt`, add delays |
| Table formatting may be imperfect | Complex HTML tables with merged cells | Manual cleanup or custom handler |
| Images not included by default | Stripped to keep output clean | Use `--images` flag |
| Login-protected content inaccessible | No authentication handling | Add session cookie support |

## References

- requests library: https://docs.python-requests.org/en/latest/
- BeautifulSoup documentation: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- markdownify package: https://pypi.org/project/markdownify/
- SQLite3 Python module: https://docs.python.org/3/library/sqlite3.html
- argparse module: https://docs.python.org/3/library/argparse.html
- lxml parser: https://lxml.de/
- Python virtual environments: https://docs.python.org/3/library/venv.html
- robots.txt specification: https://www.rfc-editor.org/rfc/rfc9309
