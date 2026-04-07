# Web Scraper to Markdown - Command Reference

Terminal commands used during project setup, dependency management, and operation.

Covers Python virtual environments, pip, PowerShell file operations, and application CLI usage.

## Python Virtual Environment

A virtual environment isolates project dependencies from the system Python installation. Each project gets its own `venv` folder containing a dedicated Python interpreter and package directory.

### Create a Virtual Environment

```powershell
python -m venv venv
```

This creates a `venv\` folder in the current directory containing a copy of the Python interpreter and an empty `site-packages` directory. The `-m venv` flag tells Python to run the built-in `venv` module, and the second `venv` is the folder name (convention, not required).

### Activate the Virtual Environment

```powershell
.\venv\Scripts\Activate.ps1
```

Activation modifies the current shell session so that `python` and `pip` point to the venv copies instead of the system-wide installation. The terminal prompt changes to show `(venv)` as confirmation.

If PowerShell blocks the script:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Deactivate the Virtual Environment

```powershell
deactivate
```

Returns the shell to using the system Python. The `(venv)` prefix disappears.

### Verify Active Environment

```powershell
python -c "import sys; print(sys.prefix)"
```

If the venv is active, this prints the path to the venv folder. If not, it prints the system Python path.

### Check Python Version

```powershell
python --version
```

## pip - Package Management

pip installs Python packages from the Python Package Index (PyPI). Inside an active venv, pip installs packages only into that venv's `site-packages`.

### Install from Requirements File

```powershell
pip install -r requirements.txt
```

The `-r` flag tells pip to read package specifications from a file. Each line in the file specifies a package and version constraint.

### Install with Pinned Versions

```powershell
pip install -r requirements-pinned.txt
```

Pinned files use `==` for exact versions (reproducible installs). Flexible files use `>=` for minimum versions (allows newer compatible releases).

### Install a Single Package

```powershell
pip install requests
```

### Install a Specific Version

```powershell
pip install requests==2.33.0
```

### List Installed Packages

```powershell
pip list
```

### Show Package Details

```powershell
pip show requests
```

Displays version, location, dependencies, and required-by information for a specific package.

### Freeze Current Environment

```powershell
pip freeze > requirements-pinned.txt
```

Outputs every installed package with exact version numbers. Useful for capturing the current state of a working environment.

### Upgrade pip

```powershell
python -m pip install --upgrade pip
```

### Verify Imports

Test that all project dependencies load correctly:

```powershell
python -c "import requests, bs4, markdownify, lxml; print('All dependencies OK')"
```

Test that all application modules load correctly:

```powershell
python -c "from core.database import ScrapeDatabase; from core.fetcher import PageFetcher; from core.converter import HtmlToMarkdown; from core.file_handler import FileHandler; print('All modules OK')"
```

## PowerShell File Operations

Commands used to set up and manage the project directory structure.

### Navigate to Project Directory

```powershell
cd "$env:USERPROFILE\Andrew J IT Labs\PYTHON\PROJECTS\web-scraper-md"
```

`$env:USERPROFILE` resolves to `C:\Users\<username>`. Quoting the path handles spaces in folder names.

### Create Directory

```powershell
mkdir web-scraper-md
```

PowerShell alias for `New-Item -ItemType Directory`.

### Create Subdirectory

```powershell
mkdir core
```

### Create an Empty File

```powershell
New-Item -Path "core\__init__.py" -ItemType File
```

### Create a File with Content (Here-String)

```powershell
@"
requests==2.33.0
beautifulsoup4==4.14.3
markdownify==1.2.2
lxml==6.0.2
"@ | Out-File -FilePath "requirements-pinned.txt" -Encoding UTF8
```

The `@" ... "@` syntax is a PowerShell here-string. It preserves line breaks and special characters. The opening `@"` must be the last thing on its line. The closing `"@` must be the first thing on its line.

### List Files in Current Directory

```powershell
Get-ChildItem
```

Short alias: `ls` or `dir`.

### List Files Excluding venv

```powershell
Get-ChildItem -Exclude venv | Select-Object Name
```

### List All Files Recursively

```powershell
Get-ChildItem -Recurse | Select-Object FullName
```

### Find a Specific File

```powershell
Get-ChildItem -Recurse -Filter "requirements-pinned.txt" | Select-Object FullName
```

### Show Current Directory

```powershell
Get-Location
```

Short alias: `pwd`.

### Extract a Zip Archive

```powershell
Expand-Archive "$env:USERPROFILE\Downloads\web-scraper-md.zip" -DestinationPath . -Force
```

`-DestinationPath .` extracts into the current directory. `-Force` overwrites existing files.

### Move Files Up One Level

```powershell
Move-Item .\web-scraper-md\* . -Force
```

The `*` wildcard selects all items inside the subfolder. `.` means current directory.

### Remove an Empty Folder

```powershell
Remove-Item .\web-scraper-md
```

### Read File Contents

```powershell
Get-Content "path\to\file.md"
```

Short alias: `cat`.

### Open a File in VS Code

```powershell
code core\converter.py
```

Opens the file in VS Code. If VS Code is not in PATH, use the full path or install the shell command from VS Code (Ctrl+Shift+P > "Install 'code' command in PATH").

## Application CLI

All commands assume the venv is active and the current directory is the project root.

### Scrape a Single URL (Interactive)

```powershell
python scraper.py https://example.com
```

Prompts for output directory before scraping.

### Scrape with Pre-Set Output Directory

```powershell
python scraper.py https://example.com -o "D:\Obsidian\Reference"
```

### Scrape in Quiet Mode (No Prompts)

```powershell
python scraper.py https://example.com -o "D:\Obsidian\Reference" --quiet
```

### Scrape with Image Links Preserved

```powershell
python scraper.py https://example.com --images
```

### Check robots.txt Before Scraping

```powershell
python scraper.py https://example.com --robots
```

### Scrape Without Scheme (Auto-Prepends https://)

```powershell
python scraper.py blog.ajolnet.com
```

The application adds `https://` if no scheme is provided.

### Batch Scrape from a URL List

```powershell
python scraper.py --batch urls.txt -o "D:\Obsidian\Reference"
```

The text file should contain one URL per line. Lines starting with `#` are ignored.

### View Scrape History

```powershell
python scraper.py --history
```

### View Scrape Statistics

```powershell
python scraper.py --stats
```

### Search Scrape History

```powershell
python scraper.py --search microsoft
```

### View Help

```powershell
python scraper.py --help
```

## SQLite Direct Queries

The scrape database can be queried directly if SQLite is available on the system. The database file is `scrapes.db` in the project root.

### Open the Database

```powershell
sqlite3 scrapes.db
```

### List All Scrapes

```sql
SELECT id, scrape_date, domain, title FROM scrapes ORDER BY id DESC;
```

### Count Scrapes by Domain

```sql
SELECT domain, COUNT(*) as count FROM scrapes GROUP BY domain ORDER BY count DESC;
```

### Find Failed Scrapes

```sql
SELECT url, error_msg FROM scrapes WHERE status = 'error';
```

### Exit SQLite

```sql
.quit
```

## References

- Python venv module: https://docs.python.org/3/library/venv.html
- pip documentation: https://pip.pypa.io/en/stable/
- PowerShell Get-ChildItem: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-childitem
- PowerShell Expand-Archive: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.archive/expand-archive
- PowerShell Here-Strings: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_quoting_rules
- SQLite CLI: https://sqlite.org/cli.html
