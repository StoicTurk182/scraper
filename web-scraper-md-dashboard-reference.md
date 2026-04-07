# Web Scraper Dashboard - Command Reference

Commands for generating, viewing, and working with the HTML dashboard.

## Generate the Dashboard

```powershell
python scraper.py --dashboard
```

Reads `scrapes.db` and writes `dashboard.html` to the project root. Requires at least one scrape in the database to show meaningful data.

## Open in Browser

```powershell
Start-Process .\dashboard.html
```

Opens the dashboard in the default browser. The HTML file is standalone and loads Chart.js from CDN for rendering.

## Populate the Database First

The dashboard visualises data from `scrapes.db`. Run scrapes to build up data before generating:

```powershell
python scraper.py https://docs.python.org/3/library/sqlite3.html
python scraper.py https://docs.python.org/3/library/argparse.html
python scraper.py https://wiki.archlinux.org/title/Systemd
python scraper.py https://docs.netgate.com/pfsense/en/latest/
```

## Refresh the Dashboard

The dashboard is a static HTML snapshot. To update it with new scrape data, regenerate it:

```powershell
python scraper.py --dashboard
Start-Process .\dashboard.html
```

## Full Workflow (Scrape, Check, Visualise)

```powershell
python scraper.py https://example.com/article
python scraper.py --history
python scraper.py --stats
python scraper.py --dashboard
Start-Process .\dashboard.html
```

## Dashboard Contents

The generated HTML displays four sections.

### Summary Cards

Total scrapes, successful, failed, unique domains, total output size, first scrape date.

### Charts

| Chart | Type | Shows |
|-------|------|-------|
| Scrapes Over Time | Stacked bar | Daily success/error counts |
| Top Domains | Horizontal bar | Most frequently scraped domains |
| Success vs Errors | Doughnut | Overall success/failure ratio |
| Activity by Hour | Bar | Scrape frequency by hour of day |

### Recent Scrapes Table

Last 50 scrapes with ID, date, time, status, domain, title, file size, and error message (if failed). Columns truncate long values with hover tooltips for full text.

## Query the Database Directly

The dashboard reads from `scrapes.db` which is a standard SQLite file. Query it directly for custom reports:

```powershell
python -c "from core.database import ScrapeDatabase; db = ScrapeDatabase(); [print(f'{r[\"id\"]:>4} {r[\"scrape_date\"]} {r[\"status\"]:>7} {r[\"domain\"]}') for r in db.get_history(20)]"
```

### Search by keyword

```powershell
python scraper.py --search microsoft
```

### View statistics

```powershell
python scraper.py --stats
```

### View recent history

```powershell
python scraper.py --history
```

## File Locations

| File | Location | Created |
|------|----------|---------|
| Database | `scrapes.db` in project root | First scrape |
| Dashboard | `dashboard.html` in project root | `--dashboard` command |
| Config | `config.json` in project root | First output directory selection |

All three are excluded from git via `.gitignore` as they contain local runtime data.

## References

- Chart.js documentation: https://www.chartjs.org/docs/latest/
- SQLite browser (optional GUI): https://sqlitebrowser.org/
