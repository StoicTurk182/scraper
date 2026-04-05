"""
Dashboard generator for the scrape database.

Reads scrapes.db and produces a standalone HTML file with
interactive charts and statistics. Uses Chart.js loaded from CDN
for client-side rendering - no additional Python dependencies required.

Usage:
    Called via: python scraper.py --dashboard
    Or directly: python -m core.dashboard

Reference: https://www.chartjs.org/docs/latest/
"""

import os
import sqlite3
import json
from datetime import datetime


class DashboardGenerator:
    """Generates an HTML dashboard from the scrape database."""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "..", "scrapes.db"
            )
        self.db_path = os.path.abspath(db_path)

    def _query(self, sql: str, params: tuple = ()) -> list:
        """Execute a query and return results as list of dicts."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]

    def _get_summary(self) -> dict:
        """Get overall summary statistics."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("""
                SELECT
                    COUNT(*)                                            AS total,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) AS success,
                    SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END)   AS errors,
                    COUNT(DISTINCT domain)                              AS domains,
                    COALESCE(SUM(file_size), 0)                         AS total_bytes,
                    MIN(scrape_date)                                    AS first_date,
                    MAX(scrape_date)                                    AS last_date
                FROM scrapes
            """).fetchone()
            return {
                "total": row[0],
                "success": row[1],
                "errors": row[2],
                "domains": row[3],
                "total_bytes": row[4],
                "first_date": row[5] or "N/A",
                "last_date": row[6] or "N/A",
            }

    def _get_daily_counts(self) -> list:
        """Get scrape counts grouped by date."""
        return self._query("""
            SELECT scrape_date AS date,
                   SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) AS success,
                   SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END)   AS errors
            FROM scrapes
            GROUP BY scrape_date
            ORDER BY scrape_date ASC
        """)

    def _get_domain_counts(self) -> list:
        """Get scrape counts grouped by domain."""
        return self._query("""
            SELECT domain, COUNT(*) AS count,
                   COALESCE(SUM(file_size), 0) AS total_bytes
            FROM scrapes
            WHERE domain IS NOT NULL
            GROUP BY domain
            ORDER BY count DESC
            LIMIT 15
        """)

    def _get_recent_scrapes(self, limit: int = 50) -> list:
        """Get recent scrape records."""
        return self._query("""
            SELECT id, url, title, domain, scrape_date, scrape_time,
                   file_size, status, error_msg
            FROM scrapes
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))

    def _get_hourly_distribution(self) -> list:
        """Get scrape counts by hour of day."""
        return self._query("""
            SELECT CAST(SUBSTR(scrape_time, 1, 2) AS INTEGER) AS hour,
                   COUNT(*) AS count
            FROM scrapes
            GROUP BY hour
            ORDER BY hour ASC
        """)

    def generate(self, output_path: str = None) -> str:
        """
        Generate the HTML dashboard and write to file.

        Args:
            output_path: Where to save the HTML file.
                         Defaults to dashboard.html in the project root.

        Returns:
            Full path to the generated HTML file.
        """
        if output_path is None:
            output_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "..", "dashboard.html"
            )
        output_path = os.path.abspath(output_path)

        # Gather all data
        summary = self._get_summary()
        daily = self._get_daily_counts()
        domains = self._get_domain_counts()
        recent = self._get_recent_scrapes()
        hourly = self._get_hourly_distribution()

        # Format bytes for display
        total_mb = summary["total_bytes"] / (1024 * 1024)

        # Prepare chart data as JSON
        daily_labels = json.dumps([r["date"] for r in daily])
        daily_success = json.dumps([r["success"] for r in daily])
        daily_errors = json.dumps([r["errors"] for r in daily])

        domain_labels = json.dumps([r["domain"][:25] for r in domains])
        domain_counts = json.dumps([r["count"] for r in domains])

        hourly_labels = json.dumps([f"{r['hour']:02d}:00" for r in hourly])
        hourly_counts = json.dumps([r["count"] for r in hourly])

        # Build the recent scrapes table rows
        table_rows = ""
        for r in recent:
            title = (r["title"] or "N/A")[:60]
            domain = (r["domain"] or "N/A")[:30]
            size_kb = (r["file_size"] or 0) / 1024
            status_class = "success" if r["status"] == "success" else "error"
            error_cell = ""
            if r["error_msg"]:
                error_cell = f'<span class="error-msg" title="{r["error_msg"]}">{r["error_msg"][:40]}</span>'

            table_rows += f"""
                <tr>
                    <td>{r["id"]}</td>
                    <td>{r["scrape_date"]}</td>
                    <td>{r["scrape_time"]}</td>
                    <td><span class="status {status_class}">{r["status"]}</span></td>
                    <td title="{r["url"]}">{domain}</td>
                    <td title="{r["title"] or ""}">{title}</td>
                    <td>{size_kb:.1f} KB</td>
                    <td>{error_cell}</td>
                </tr>"""

        # Assemble HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Scraper Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #0d1117;
            color: #c9d1d9;
            padding: 24px;
        }}
        h1 {{
            font-size: 1.6rem;
            font-weight: 600;
            margin-bottom: 8px;
            color: #e6edf3;
        }}
        .subtitle {{
            color: #7d8590;
            font-size: 0.9rem;
            margin-bottom: 24px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .stat-card {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 16px;
        }}
        .stat-value {{
            font-size: 1.8rem;
            font-weight: 700;
            color: #e6edf3;
        }}
        .stat-label {{
            font-size: 0.8rem;
            color: #7d8590;
            margin-top: 4px;
        }}
        .charts-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-bottom: 24px;
        }}
        .chart-card {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 16px;
        }}
        .chart-card h2 {{
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 12px;
            color: #e6edf3;
        }}
        .chart-card canvas {{
            max-height: 280px;
        }}
        .table-card {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 16px;
            overflow-x: auto;
        }}
        .table-card h2 {{
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 12px;
            color: #e6edf3;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
        }}
        th {{
            text-align: left;
            padding: 8px 12px;
            border-bottom: 2px solid #30363d;
            color: #7d8590;
            font-weight: 600;
            white-space: nowrap;
        }}
        td {{
            padding: 6px 12px;
            border-bottom: 1px solid #21262d;
            max-width: 200px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        tr:hover {{
            background: #1c2128;
        }}
        .status {{
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        .status.success {{
            background: #0d1f0d;
            color: #3fb950;
            border: 1px solid #238636;
        }}
        .status.error {{
            background: #2d0d0d;
            color: #f85149;
            border: 1px solid #da3633;
        }}
        .error-msg {{
            color: #f85149;
            font-size: 0.8rem;
        }}
        .generated {{
            text-align: center;
            color: #484f58;
            font-size: 0.75rem;
            margin-top: 24px;
            padding-top: 16px;
            border-top: 1px solid #21262d;
        }}
        @media (max-width: 768px) {{
            .charts-grid {{ grid-template-columns: 1fr; }}
            body {{ padding: 12px; }}
        }}
    </style>
</head>
<body>
    <h1>Web Scraper Dashboard</h1>
    <p class="subtitle">Database: {self.db_path}</p>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">{summary["total"]}</div>
            <div class="stat-label">Total Scrapes</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{summary["success"]}</div>
            <div class="stat-label">Successful</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{summary["errors"]}</div>
            <div class="stat-label">Failed</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{summary["domains"]}</div>
            <div class="stat-label">Unique Domains</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{total_mb:.2f}</div>
            <div class="stat-label">Total Output (MB)</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{summary["first_date"]}</div>
            <div class="stat-label">First Scrape</div>
        </div>
    </div>

    <div class="charts-grid">
        <div class="chart-card">
            <h2>Scrapes Over Time</h2>
            <canvas id="dailyChart"></canvas>
        </div>
        <div class="chart-card">
            <h2>Top Domains</h2>
            <canvas id="domainChart"></canvas>
        </div>
        <div class="chart-card">
            <h2>Success vs Errors</h2>
            <canvas id="statusChart"></canvas>
        </div>
        <div class="chart-card">
            <h2>Activity by Hour</h2>
            <canvas id="hourlyChart"></canvas>
        </div>
    </div>

    <div class="table-card">
        <h2>Recent Scrapes</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Status</th>
                    <th>Domain</th>
                    <th>Title</th>
                    <th>Size</th>
                    <th>Error</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </div>

    <p class="generated">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>

    <script>
        const chartDefaults = {{
            color: '#7d8590',
            borderColor: '#30363d',
        }};
        Chart.defaults.color = chartDefaults.color;
        Chart.defaults.borderColor = chartDefaults.borderColor;

        // Daily scrapes chart
        new Chart(document.getElementById('dailyChart'), {{
            type: 'bar',
            data: {{
                labels: {daily_labels},
                datasets: [
                    {{
                        label: 'Success',
                        data: {daily_success},
                        backgroundColor: 'rgba(63, 185, 80, 0.7)',
                        borderColor: '#3fb950',
                        borderWidth: 1,
                        borderRadius: 3,
                    }},
                    {{
                        label: 'Errors',
                        data: {daily_errors},
                        backgroundColor: 'rgba(248, 81, 73, 0.7)',
                        borderColor: '#f85149',
                        borderWidth: 1,
                        borderRadius: 3,
                    }}
                ]
            }},
            options: {{
                responsive: true,
                scales: {{
                    x: {{ stacked: true }},
                    y: {{ stacked: true, beginAtZero: true, ticks: {{ stepSize: 1 }} }}
                }},
                plugins: {{ legend: {{ position: 'bottom' }} }}
            }}
        }});

        // Domain chart
        new Chart(document.getElementById('domainChart'), {{
            type: 'bar',
            data: {{
                labels: {domain_labels},
                datasets: [{{
                    label: 'Scrapes',
                    data: {domain_counts},
                    backgroundColor: 'rgba(56, 139, 253, 0.7)',
                    borderColor: '#388bfd',
                    borderWidth: 1,
                    borderRadius: 3,
                }}]
            }},
            options: {{
                indexAxis: 'y',
                responsive: true,
                scales: {{
                    x: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }}
                }},
                plugins: {{ legend: {{ display: false }} }}
            }}
        }});

        // Status pie chart
        new Chart(document.getElementById('statusChart'), {{
            type: 'doughnut',
            data: {{
                labels: ['Success', 'Errors'],
                datasets: [{{
                    data: [{summary["success"]}, {summary["errors"]}],
                    backgroundColor: [
                        'rgba(63, 185, 80, 0.8)',
                        'rgba(248, 81, 73, 0.8)'
                    ],
                    borderColor: ['#3fb950', '#f85149'],
                    borderWidth: 2,
                }}]
            }},
            options: {{
                responsive: true,
                cutout: '60%',
                plugins: {{ legend: {{ position: 'bottom' }} }}
            }}
        }});

        // Hourly distribution
        new Chart(document.getElementById('hourlyChart'), {{
            type: 'bar',
            data: {{
                labels: {hourly_labels},
                datasets: [{{
                    label: 'Scrapes',
                    data: {hourly_counts},
                    backgroundColor: 'rgba(163, 113, 247, 0.7)',
                    borderColor: '#a371f7',
                    borderWidth: 1,
                    borderRadius: 3,
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }}
                }},
                plugins: {{ legend: {{ display: false }} }}
            }}
        }});
    </script>
</body>
</html>"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        return output_path


if __name__ == "__main__":
    gen = DashboardGenerator()
    path = gen.generate()
    print(f"Dashboard generated: {path}")
