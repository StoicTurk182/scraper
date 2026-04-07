# Web Scraper to Markdown - Core Concepts

A deconstruction guide to every programming concept used in this project.

Organised by topic and subtopic with the specific file and line context where each concept appears. Intended as a reference for understanding the project through code reading.

## 1. Python Language Fundamentals

### 1.1 Imports

Imports make code from other modules available in the current file. Python searches for modules in the standard library, installed packages, and the current project.

```python
# Standard library import - module ships with Python
import os
import re
import sys
import json
import sqlite3
from datetime import datetime
from urllib.parse import urlparse

# Third-party import - installed via pip
import requests
from bs4 import BeautifulSoup, Comment
from markdownify import markdownify as md

# Relative import - from within this project
from core.fetcher import PageFetcher
from core.converter import HtmlToMarkdown
```

Used in: every file.

The `from X import Y` syntax imports only the specific name `Y` from module `X`, keeping the namespace clean. The `as` keyword creates an alias (`markdownify as md`) to shorten repeated usage.

Reference: https://docs.python.org/3/reference/import.html

### 1.2 Variables and Data Types

```python
# String
url = "https://example.com"

# Integer
timeout = 15
file_size = 1234

# Boolean
keep_images = False
quiet = True

# None (absence of a value)
error_msg = None
db_path = None

# List (ordered, mutable collection)
STRIP_TAGS = ["nav", "footer", "header", "aside"]

# Dictionary (key-value pairs)
packages = {"requests": "2.33.0", "lxml": "6.0.2"}

# Tuple (ordered, immutable collection)
# Used implicitly in SQL parameter passing: (url, title, domain)
```

Used in: all modules.

Python is dynamically typed. Variables do not need type declarations but the project uses type hints (section 1.9) for documentation.

Reference: https://docs.python.org/3/library/stdtypes.html

### 1.3 String Formatting

```python
# f-strings (formatted string literals) - Python 3.6+
print(f"Fetching: {url}")
print(f"Size: {file_size:,} bytes")    # :, adds thousand separators
print(f"{'ID':<5} {'Date':<12}")       # :<5 left-aligns, pads to 5 chars

# .format() method
timestamp = now.strftime("%Y-%m-%d")   # strftime formats datetime objects

# String concatenation
filepath = os.path.join(output_dir, filename)
```

Used in: `scraper.py` (print_success, show_history), `database.py` (SQL queries), `file_handler.py` (filename generation).

f-strings are the preferred approach in modern Python. The format spec after `:` controls alignment (`<` left, `>` right), padding width, and number formatting (`,` for thousands, `.2f` for decimal places).

Reference: https://docs.python.org/3/reference/lexemes.html#f-strings

### 1.4 Conditional Logic

```python
# if / elif / else
if choice == "2":
    new_path = input("Enter full path: ").strip()
else:
    output_dir = self.default_output_dir

# Ternary expression (inline if)
body = soup.find("body")
return body if body else soup

# Truthiness - empty strings, None, 0, empty lists are falsy
if not safe_title:
    safe_title = "scraped-page"

if converted["word_count"] < 10:
    print_error("Extracted content is very short")
```

Used in: all modules.

Python evaluates truthiness rather than requiring explicit boolean comparisons. `None`, `""`, `0`, `[]`, `{}` are all falsy. `not` inverts the boolean value.

Reference: https://docs.python.org/3/reference/compound_stmts.html#if

### 1.5 Loops

```python
# for loop over a list
for tag_name in self.STRIP_TAGS:
    for tag in soup.find_all(tag_name):
        tag.decompose()

# for loop with enumerate (provides index)
for i, url in enumerate(urls, 1):
    print(f"[{i}/{len(urls)}] {url}")

# while loop (not used in this project but related)
# while condition:
#     do_something()

# List comprehension (loop that builds a list)
lines = [line.rstrip() for line in text.split("\n")]
urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
```

Used in: `converter.py` (element stripping, line cleanup), `scraper.py` (batch scraping), `database.py` (result processing).

`enumerate(iterable, start)` wraps an iterable and yields `(index, value)` pairs. The `start` parameter sets the initial index (default 0).

List comprehensions are a compact syntax for building lists from loops with optional filtering. The `if` clause at the end filters items.

Reference: https://docs.python.org/3/tutorial/controlflow.html#for-statements

### 1.6 Functions

```python
# Function definition with parameters and return value
def generate_filename(self, title: str, url: str = "") -> str:
    safe_title = re.sub(r"[^\w\s-]", "", title)
    return f"{safe_title}_{timestamp}.md"

# Function with no return value (returns None implicitly)
def print_error(message: str):
    print(f"ERROR: {message}", file=sys.stderr)

# Default parameter values
def __init__(self, timeout: int = 15):

# Keyword arguments
db.log_scrape(
    url=url,
    title=converted["title"],
    status="success",
)
```

Used in: all modules.

Functions are defined with `def`. Parameters can have default values (used when the caller omits them). `self` is the first parameter in class methods and refers to the instance (section 2.1).

Keyword arguments (`name=value`) make function calls readable when passing many parameters.

Reference: https://docs.python.org/3/tutorial/controlflow.html#defining-functions

### 1.7 Exception Handling

```python
# try / except - catch and handle errors
try:
    result = fetcher.fetch(url)
    converted = converter.convert(result["html"])
    # ... write file, log to database
except Exception as e:
    print_error(str(e))
    db.log_scrape(
        url=url,
        status="error",
        error_msg=str(e),
    )
    return False

# Nested try/except for non-critical operations
try:
    with open(config_path, "r") as f:
        config = json.load(f)
except (json.JSONDecodeError, IOError):
    pass    # silently ignore corrupt/missing config
```

Used in: `scraper.py` (main scrape pipeline), `file_handler.py` (config loading), `fetcher.py` (robots.txt check).

`Exception as e` captures the exception object. `str(e)` converts it to a human-readable message. Multiple exception types can be caught with a tuple: `except (TypeError, ValueError)`.

`pass` is a no-op statement used when a code block is required syntactically but no action is needed.

Reference: https://docs.python.org/3/tutorial/errors.html

### 1.8 Context Managers (with statement)

```python
# File operations - file is automatically closed when the block exits
with open(filepath, "w", encoding="utf-8") as f:
    f.write(full_content)

# Database connections - automatically commits on success, rolls back on error
with sqlite3.connect(self.db_path) as conn:
    conn.execute("INSERT INTO scrapes ...", params)
    conn.commit()
```

Used in: `database.py` (every database operation), `file_handler.py` (file reading and writing).

The `with` statement guarantees cleanup (closing files, committing/rolling back transactions) even if an exception occurs inside the block. This replaces manual `try/finally` patterns.

Reference: https://docs.python.org/3/reference/compound_stmts.html#the-with-statement

### 1.9 Type Hints

```python
def fetch(self, url: str) -> dict:
def log_scrape(self, url: str, title: str, domain: str,
               output_path: str, file_size: int,
               status: str = "success", error_msg: str = None):
def get_history(self, limit: int = 20) -> list:
```

Used in: all modules (function signatures).

Type hints annotate what types a function expects and returns. They are not enforced at runtime but serve as documentation and enable IDE autocompletion and static analysis tools like mypy.

`-> dict` means the function returns a dictionary. `error_msg: str = None` means the parameter accepts a string but defaults to None.

Reference: https://docs.python.org/3/library/typing.html

## 2. Object-Oriented Programming

### 2.1 Classes and Instances

```python
class PageFetcher:
    """Fetches web page HTML content with proper headers and error handling."""

    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 ..."
    }

    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)

    def fetch(self, url: str) -> dict:
        response = self.session.get(url, timeout=self.timeout)
        return {"html": response.text, ...}
```

Used in: `fetcher.py` (PageFetcher), `converter.py` (HtmlToMarkdown), `database.py` (ScrapeDatabase), `file_handler.py` (FileHandler).

A class is a blueprint for creating objects. `__init__` is the constructor, called when a new instance is created. `self` refers to the specific instance being operated on.

Class-level variables like `DEFAULT_HEADERS` are shared across all instances. Instance variables like `self.timeout` are unique to each instance.

```python
# Creating an instance (calls __init__)
fetcher = PageFetcher(timeout=20)

# Calling a method on the instance
result = fetcher.fetch("https://example.com")
```

Reference: https://docs.python.org/3/tutorial/classes.html

### 2.2 Encapsulation

```python
class ScrapeDatabase:
    def __init__(self, db_path=None):
        self.db_path = os.path.abspath(db_path)
        self._init_db()    # private method - underscore prefix convention

    def _init_db(self):
        """Create the scrapes table if it does not exist."""
        # Implementation details hidden from callers

    def log_scrape(self, ...):
        """Public interface - callers use this."""
```

Used in: `database.py` (_init_db), `file_handler.py` (_load_default_dir, _save_default_dir), `converter.py` (_extract_title, _strip_elements, _find_main_content, _clean_markdown).

Methods prefixed with `_` are conventionally private. They handle internal logic that callers should not need to use directly. Python does not enforce this (unlike Java's `private` keyword) but it signals intent.

Each class in this project has a clear single responsibility: fetching, converting, storing, or file handling.

Reference: https://docs.python.org/3/tutorial/classes.html#private-variables

### 2.3 Docstrings

```python
class HtmlToMarkdown:
    """Converts raw HTML to clean, formatted Markdown."""

    def convert(self, html: str, keep_images: bool = False) -> dict:
        """
        Parse HTML and convert to clean Markdown.

        Args:
            html:        Raw HTML string.
            keep_images: If True, preserve image markdown links.

        Returns:
            Dict with keys: markdown, title, meta_description, word_count, link_count.
        """
```

Used in: all modules.

Triple-quoted strings immediately after a class or function definition become that object's docstring. They are accessible at runtime via `help()` and used by documentation generators.

The Args/Returns format follows Google-style docstring conventions.

Reference: https://peps.python.org/pep-0257/

## 3. HTTP and Web Requests

### 3.1 The requests Library

```python
import requests

# Create a persistent session (reuses TCP connections)
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 ..."})

# Make a GET request
response = session.get(url, timeout=15, allow_redirects=True)

# Check for HTTP errors (raises exception for 4xx/5xx)
response.raise_for_status()

# Access response data
html = response.text              # decoded string content
status = response.status_code     # 200, 404, 500, etc.
content_type = response.headers.get("Content-Type", "")
```

Used in: `fetcher.py`.

A Session object persists headers and cookies across multiple requests to the same server. This is more efficient than individual `requests.get()` calls because it reuses the underlying TCP connection.

`timeout=15` prevents the script from hanging indefinitely on unresponsive servers. `allow_redirects=True` follows HTTP 301/302 redirects automatically.

Reference: https://docs.python-requests.org/en/latest/

### 3.2 Character Encoding Detection

```python
response.encoding = response.apparent_encoding
```

Used in: `fetcher.py`.

Web servers declare character encoding in the `Content-Type` header, but this is often missing or wrong. `apparent_encoding` uses the chardet library to detect the actual encoding from the byte content, producing correct text for non-UTF8 pages.

Reference: https://docs.python-requests.org/en/latest/user/advanced/#encodings

### 3.3 URL Parsing

```python
from urllib.parse import urlparse

parsed = urlparse("https://blog.ajolnet.com/post/example/")
# parsed.scheme   = "https"
# parsed.netloc   = "blog.ajolnet.com"
# parsed.path     = "/post/example/"
```

Used in: `fetcher.py` (domain extraction), `scraper.py` (URL validation).

`urlparse` breaks a URL into its component parts. This is used to extract the domain name for database logging and to validate that the URL has a scheme (`http://` or `https://`).

Reference: https://docs.python.org/3/library/urllib.parse.html

## 4. HTML Parsing

### 4.1 BeautifulSoup

```python
from bs4 import BeautifulSoup, Comment

# Parse HTML into a navigable DOM tree
soup = BeautifulSoup(html, "lxml")

# Find elements by tag name
title_tag = soup.find("title")
h1 = soup.find("h1")

# Find all matching elements
for tag in soup.find_all("nav"):
    tag.decompose()    # remove from DOM entirely

# Find by CSS class (partial match using lambda)
for tag in soup.find_all(class_=lambda c: c and "sidebar" in " ".join(c).lower()):
    tag.decompose()

# CSS selector syntax
found = soup.select_one("main")
found = soup.select_one('[role="main"]')
found = soup.select_one("#content")
found = soup.select_one(".article-body")

# Extract text content
text = tag.get_text(strip=True)

# Get attribute value
content = meta.get("content")
```

Used in: `converter.py` (all parsing and cleaning operations).

BeautifulSoup builds a tree representation of the HTML document. Elements can be found by tag name, CSS class, ID, attribute, or CSS selector. `decompose()` permanently removes an element and its children from the tree.

The `"lxml"` parser is faster and more tolerant of malformed HTML than Python's built-in `html.parser`.

`find()` returns the first match or None. `find_all()` returns a list of all matches.

Reference: https://www.crummy.com/software/BeautifulSoup/bs4/doc/

### 4.2 Content Detection Strategy

```python
def _find_main_content(self, soup):
    selectors = [
        "main",                  # HTML5 semantic element
        "article",               # HTML5 article element
        '[role="main"]',         # ARIA role attribute
        "#content",              # ID selector
        ".post-content",         # Class selector
        ".markdown-body",        # GitHub-specific
        ".mw-parser-output",     # Wikipedia/MediaWiki
    ]
    for selector in selectors:
        found = soup.select_one(selector)
        if found and len(found.get_text(strip=True)) > 100:
            return found
    return soup.find("body") or soup
```

Used in: `converter.py` (_find_main_content).

This is a heuristic approach. The method tries progressively less specific selectors until it finds a container with substantial text content (> 100 characters). This works because most websites and CMSs use predictable element names and classes for their main content area.

The fallback to `<body>` ensures something is always returned even if no known content container exists.

## 5. HTML to Markdown Conversion

### 5.1 markdownify

```python
from markdownify import markdownify as md

markdown_text = md(
    str(content),              # HTML string to convert
    heading_style="ATX",       # Use # style headings (not underline style)
    bullets="-",               # Use - for unordered lists (not * or +)
    strip=["img"],             # Remove these tags entirely
)
```

Used in: `converter.py` (convert method).

markdownify walks the HTML DOM tree and produces equivalent Markdown syntax. It handles headings (`<h1>` to `# Heading`), links (`<a>` to `[text](url)`), emphasis (`<strong>` to `**bold**`), code blocks (`<pre><code>` to fenced blocks), tables, and lists.

ATX headings use `#` prefixes. The alternative (Setext) uses underlines, which is less common in modern Markdown.

The `strip` parameter removes specified HTML tags and their content from the output entirely. It cannot be used simultaneously with `convert` (which whitelists tags to include).

Reference: https://pypi.org/project/markdownify/

## 6. Regular Expressions

### 6.1 The re Module

```python
import re

# Remove characters not matching the pattern
safe_title = re.sub(r"[^\w\s-]", "", title)
# \w = word characters (letters, digits, underscore)
# \s = whitespace
# -  = literal hyphen
# ^  = NOT (inside character class)
# Result: keeps only alphanumeric, spaces, hyphens

# Replace whitespace runs with single hyphen
safe_title = re.sub(r"[\s]+", "-", safe_title)

# Remove blank-only lines
text = re.sub(r"^[ \t]+$", "", text, flags=re.MULTILINE)

# Collapse excessive blank lines
text = re.sub(r"\n{3,}", "\n\n", text)
```

Used in: `file_handler.py` (filename sanitisation), `converter.py` (markdown cleanup).

`re.sub(pattern, replacement, string)` replaces all matches of the regex pattern with the replacement string.

The `r""` prefix creates a raw string where backslashes are literal (not escape sequences). This is important because regex uses backslashes extensively (`\w`, `\s`, `\n`).

`re.MULTILINE` makes `^` and `$` match the start/end of each line rather than the entire string.

Reference: https://docs.python.org/3/library/re.html

## 7. File System Operations

### 7.1 The os and os.path Modules

```python
import os

# Path construction (handles OS-specific separators)
filepath = os.path.join(output_dir, filename)
# Windows: "C:\Users\Andrew\Documents\file.md"
# Linux:   "/home/andrew/documents/file.md"

# Resolve relative paths to absolute
db_path = os.path.abspath(db_path)

# Get the directory containing a file
parent = os.path.dirname(os.path.abspath(__file__))
# __file__ is the current script's path

# Expand ~ to user home directory
home = os.path.expanduser("~")

# Create directory tree (no error if it already exists)
os.makedirs(output_dir, exist_ok=True)

# Check if path exists
if os.path.exists(config_path):

# Check if path is a directory
if os.path.isdir(saved):

# Get file size in bytes
size = os.path.getsize(filepath)
```

Used in: `file_handler.py` (path management), `database.py` (db path resolution), `scraper.py` (directory creation).

`os.path.join()` is critical for cross-platform compatibility. It uses `\` on Windows and `/` on Linux/macOS automatically.

`__file__` is a special variable containing the path to the current Python file. Combined with `dirname` and `abspath`, it produces reliable paths relative to the script location rather than the working directory.

Reference: https://docs.python.org/3/library/os.path.html

### 7.2 File Reading and Writing

```python
# Write a text file
with open(filepath, "w", encoding="utf-8") as f:
    f.write(full_content)

# Read a text file
with open(file_path, "r") as f:
    urls = [line.strip() for line in f if line.strip()]

# Read and parse JSON
with open(config_path, "r") as f:
    config = json.load(f)

# Write JSON
with open(config_path, "w") as f:
    json.dump(config, f, indent=2)
```

Used in: `file_handler.py` (markdown output, config persistence), `scraper.py` (batch URL reading).

`"w"` mode creates/overwrites a file. `"r"` mode reads. `encoding="utf-8"` ensures non-ASCII characters are handled correctly.

`json.load(f)` reads a file object and parses JSON into a Python dict/list. `json.dump(obj, f)` serialises a Python object to JSON and writes it to a file. `indent=2` produces human-readable formatting.

Reference: https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files

## 8. Database Operations (SQLite)

### 8.1 The sqlite3 Module

```python
import sqlite3

# Connect (creates the file if it doesn't exist)
with sqlite3.connect(self.db_path) as conn:

    # Create a table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scrapes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            url         TEXT NOT NULL,
            title       TEXT,
            status      TEXT DEFAULT 'success'
        )
    """)

    # Insert a row (parameterised query - ? placeholders)
    conn.execute(
        "INSERT INTO scrapes (url, title) VALUES (?, ?)",
        (url, title)
    )
    conn.commit()

    # Query rows
    conn.row_factory = sqlite3.Row    # return dicts instead of tuples
    cursor = conn.execute(
        "SELECT * FROM scrapes ORDER BY id DESC LIMIT ?", (limit,)
    )
    results = [dict(row) for row in cursor.fetchall()]
```

Used in: `database.py` (all methods).

SQLite is an embedded database engine. The entire database lives in a single `.db` file with no server process required. The `sqlite3` module is part of Python's standard library.

Parameterised queries (`?` placeholders) prevent SQL injection by separating the query structure from the data values. Never use f-strings or string concatenation to build SQL queries with user input.

`row_factory = sqlite3.Row` makes query results accessible by column name (`row["title"]`) instead of just index (`row[0]`).

`CREATE TABLE IF NOT EXISTS` is idempotent. It creates the table on first run and does nothing on subsequent runs.

Reference: https://docs.python.org/3/library/sqlite3.html

### 8.2 SQL Concepts Used

```sql
-- DDL (Data Definition Language) - defines structure
CREATE TABLE IF NOT EXISTS scrapes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,  -- auto-incrementing unique ID
    url         TEXT NOT NULL,                       -- required field
    title       TEXT,                                -- optional field (nullable)
    status      TEXT DEFAULT 'success'               -- default value if omitted
);

-- DML (Data Manipulation Language) - manipulates data
INSERT INTO scrapes (url, title) VALUES (?, ?);

-- Queries with filtering, ordering, limiting
SELECT * FROM scrapes WHERE status = 'error' ORDER BY id DESC LIMIT 20;

-- Aggregation
SELECT domain, COUNT(*) as count FROM scrapes GROUP BY domain;

-- Multiple aggregations in one query
SELECT
    COUNT(*) AS total,
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) AS successful,
    COUNT(DISTINCT domain) AS unique_domains,
    COALESCE(SUM(file_size), 0) AS total_bytes
FROM scrapes;
```

Used in: `database.py` (_init_db, log_scrape, get_history, get_stats, search).

`COALESCE(value, fallback)` returns the first non-NULL argument. Used here to handle the case where `SUM(file_size)` returns NULL when there are no rows.

`CASE WHEN ... THEN ... ELSE ... END` is SQL's conditional expression, equivalent to an if/else inside a query.

`LIKE` with `%` wildcards performs pattern matching: `%keyword%` matches any string containing "keyword".

Reference: https://sqlite.org/lang.html

## 9. CLI Design (argparse)

### 9.1 The argparse Module

```python
import argparse

parser = argparse.ArgumentParser(
    description="Scrape web pages and convert to formatted Markdown files.",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="examples:\n  python scraper.py https://example.com",
)

# Positional argument (no -- prefix, order matters)
parser.add_argument("url", nargs="?", help="URL to scrape")

# Optional arguments (-- prefix, order doesn't matter)
parser.add_argument("--output", "-o", help="Output directory path")
parser.add_argument("--quiet", "-q", action="store_true", help="Suppress prompts")
parser.add_argument("--history", action="store_true", help="Show history")
parser.add_argument("--search", "-s", help="Search keyword")

args = parser.parse_args()

# Access parsed values
if args.history:
    show_history()
if args.url:
    scrape(args.url, output_dir=args.output)
```

Used in: `scraper.py` (main function).

`nargs="?"` makes a positional argument optional (normally they are required). `action="store_true"` creates a boolean flag that is False by default and True when the flag is present.

Short flags (`-o`, `-q`, `-s`) provide convenience. Long flags (`--output`, `--quiet`, `--search`) provide clarity.

`RawDescriptionHelpFormatter` preserves whitespace in the epilog text, allowing formatted examples in the help output.

Reference: https://docs.python.org/3/library/argparse.html

## 10. JSON Configuration

### 10.1 Persistent Settings

```python
import json

CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "config.json"
)

# Load
with open(config_path, "r") as f:
    config = json.load(f)
saved_dir = config.get("output_dir", "")

# Save
config["output_dir"] = directory
with open(config_path, "w") as f:
    json.dump(config, f, indent=2)
```

Used in: `file_handler.py` (_load_default_dir, _save_default_dir).

This pattern stores user preferences in a JSON file so they persist between runs. The `dict.get(key, default)` method returns the default value if the key doesn't exist, avoiding KeyError exceptions.

The config file is placed in the project root (one level up from `core/`) using the `..` relative path combined with `os.path.abspath()`.

Reference: https://docs.python.org/3/library/json.html

## 11. Lambdas and Callable Arguments

### 11.1 Lambda Functions

```python
# Lambda as a filter function for BeautifulSoup
soup.find_all(class_=lambda c: c and "sidebar" in " ".join(c).lower())

# Lambda as a filter for HTML comments
soup.find_all(string=lambda text: isinstance(text, Comment))
```

Used in: `converter.py` (_strip_elements, _strip_comments).

A lambda is an anonymous function defined inline. `lambda c: c and "sidebar" in " ".join(c).lower()` takes one argument `c` (the element's class list) and returns True if the class list is not None and contains "sidebar".

BeautifulSoup's `find_all()` accepts callables (functions or lambdas) as filter criteria. The callable receives each candidate value and should return True to include it.

Reference: https://docs.python.org/3/reference/expressions.html#lambda

## 12. Project Structure

### 12.1 Python Packages

```
web-scraper-md/
├── scraper.py          # Entry point
└── core/               # Package directory
    ├── __init__.py     # Makes 'core' a package (can be empty)
    ├── database.py     # Module
    ├── fetcher.py      # Module
    ├── converter.py    # Module
    └── file_handler.py # Module
```

The `__init__.py` file tells Python that the `core/` directory is a package (importable collection of modules). Without it, `from core.database import ScrapeDatabase` would fail.

Each module (`.py` file) contains one class with a single responsibility. This separation makes the code testable, maintainable, and replaceable. The converter can be swapped out without touching the database or fetcher.

Reference: https://docs.python.org/3/tutorial/modules.html#packages

### 12.2 Entry Point Pattern

```python
if __name__ == "__main__":
    main()
```

Used in: `scraper.py`.

`__name__` is a special variable set by Python. When a file is run directly (`python scraper.py`), `__name__` equals `"__main__"`. When a file is imported by another module, `__name__` equals the module name (e.g., `"scraper"`).

This pattern allows a file to be both a standalone script and an importable module. The `main()` function only runs when the file is executed directly.

Reference: https://docs.python.org/3/library/__main__.html

## Concept Map

How the concepts connect across modules:

```
scraper.py (CLI + Pipeline)
  ├── argparse          -> parse command-line arguments
  ├── imports           -> load all core modules
  ├── exception handling -> catch errors, log to database
  ├── f-strings         -> format terminal output
  └── calls:
      ├── PageFetcher.fetch()
      │     ├── requests.Session   -> HTTP GET
      │     ├── urlparse           -> extract domain
      │     └── encoding detection -> charset handling
      │
      ├── HtmlToMarkdown.convert()
      │     ├── BeautifulSoup      -> parse HTML DOM
      │     ├── lambdas            -> filter elements
      │     ├── CSS selectors      -> find main content
      │     ├── markdownify        -> HTML to Markdown
      │     └── regex              -> clean output
      │
      ├── FileHandler.write_markdown()
      │     ├── os.path            -> path construction
      │     ├── regex              -> filename sanitisation
      │     ├── file I/O           -> write .md file
      │     └── json               -> persist config
      │
      └── ScrapeDatabase.log_scrape()
            ├── sqlite3            -> embedded database
            ├── context managers   -> connection handling
            └── SQL                -> parameterised queries
```

## References

- Python Tutorial: https://docs.python.org/3/tutorial/index.html
- Python Standard Library: https://docs.python.org/3/library/index.html
- requests: https://docs.python-requests.org/en/latest/
- BeautifulSoup: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- markdownify: https://pypi.org/project/markdownify/
- SQLite SQL Reference: https://sqlite.org/lang.html
- Real Python (tutorials): https://realpython.com/
- PEP 8 Style Guide: https://peps.python.org/pep-0008/
- PEP 257 Docstring Conventions: https://peps.python.org/pep-0257/
