"""
SQLite database operations for scrape logging.

The database file is created alongside the application executable.
No external database server required - sqlite3 is part of the Python
standard library and stores data in a single local file.

Reference: https://docs.python.org/3/library/sqlite3.html
"""

import sqlite3
import os
from datetime import datetime


class ScrapeDatabase:
    """Manages an embedded SQLite database that logs every scrape attempt."""

    def __init__(self, db_path: str = None):
        """
        Initialise the database connection.

        Args:
            db_path: Full path to the .db file. Defaults to scrapes.db
                     in the project root directory.
        """
        if db_path is None:
            # Place the database in the same directory as the main script
            db_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "..", "scrapes.db"
            )
        self.db_path = os.path.abspath(db_path)
        self._init_db()

    def _init_db(self):
        """Create the scrapes table if it does not exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scrapes (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    url         TEXT NOT NULL,
                    title       TEXT,
                    domain      TEXT,
                    scrape_date TEXT NOT NULL,
                    scrape_time TEXT NOT NULL,
                    output_path TEXT NOT NULL,
                    file_size   INTEGER,
                    status      TEXT DEFAULT 'success',
                    error_msg   TEXT
                )
            """)
            conn.commit()

    def log_scrape(self, url: str, title: str, domain: str,
                   output_path: str, file_size: int,
                   status: str = "success", error_msg: str = None):
        """
        Insert a scrape record into the database.

        Args:
            url:         The original URL that was scraped.
            title:       Page title extracted from the HTML.
            domain:      Domain name parsed from the URL.
            output_path: Full filesystem path to the saved .md file.
            file_size:   Size of the output file in bytes.
            status:      Either 'success' or 'error'.
            error_msg:   Error message string if status is 'error'.
        """
        now = datetime.now()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO scrapes (url, title, domain, scrape_date, scrape_time,
                                     output_path, file_size, status, error_msg)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                url,
                title,
                domain,
                now.strftime("%Y-%m-%d"),
                now.strftime("%H:%M:%S"),
                output_path,
                file_size,
                status,
                error_msg
            ))
            conn.commit()

    def get_history(self, limit: int = 20) -> list:
        """
        Return the most recent scrape records.

        Args:
            limit: Maximum number of records to return.

        Returns:
            List of dicts, each representing one scrape record.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM scrapes ORDER BY id DESC LIMIT ?", (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_stats(self) -> dict:
        """
        Return summary statistics from the scrape database.

        Returns:
            Dict with total_scrapes, successful, failed, unique_domains,
            total_bytes, first_scrape, last_scrape.
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("""
                SELECT
                    COUNT(*)                                    AS total_scrapes,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) AS successful,
                    SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END)   AS failed,
                    COUNT(DISTINCT domain)                      AS unique_domains,
                    COALESCE(SUM(file_size), 0)                 AS total_bytes,
                    MIN(scrape_date || ' ' || scrape_time)      AS first_scrape,
                    MAX(scrape_date || ' ' || scrape_time)      AS last_scrape
                FROM scrapes
            """).fetchone()
            return {
                "total_scrapes": row[0],
                "successful": row[1],
                "failed": row[2],
                "unique_domains": row[3],
                "total_bytes": row[4],
                "first_scrape": row[5],
                "last_scrape": row[6]
            }

    def search(self, keyword: str, limit: int = 20) -> list:
        """
        Search scrape history by URL, title, or domain.

        Args:
            keyword: Search term to match against url, title, or domain.
            limit:   Maximum results to return.

        Returns:
            List of matching scrape record dicts.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM scrapes
                WHERE url LIKE ? OR title LIKE ? OR domain LIKE ?
                ORDER BY id DESC LIMIT ?
            """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", limit))
            return [dict(row) for row in cursor.fetchall()]
