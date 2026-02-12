# -*- coding: utf-8 -*-
"""
SQLite database writer.

Creates the schema and provides batch-insert helpers for the shapelet
ingestion pipeline.
"""

from __future__ import annotations

import datetime
import json
import sqlite3
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Schema DDL
# ---------------------------------------------------------------------------

_SCHEMA_SQL = """
-- Lookup: pollutant parameter codes
CREATE TABLE IF NOT EXISTS pollutants (
    parameter_code  TEXT PRIMARY KEY,
    name            TEXT,
    unit            TEXT
);

-- Lookup: monitoring sites
CREATE TABLE IF NOT EXISTS sites (
    site_key    TEXT PRIMARY KEY,   -- "{state}_{county}_{site_num}"
    state       TEXT NOT NULL,
    county      TEXT NOT NULL,
    site_num    INTEGER NOT NULL,
    latitude    REAL,
    longitude   REAL
);

-- Core data: one row per shapelet
CREATE TABLE IF NOT EXISTS shapelets (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    dataset_key     TEXT    NOT NULL,
    shapelet_id     INTEGER NOT NULL,
    site_key        TEXT    NOT NULL REFERENCES sites(site_key),
    parameter_code  TEXT    REFERENCES pollutants(parameter_code),
    year            INTEGER NOT NULL,
    start_date      TEXT    NOT NULL,   -- ISO-8601
    end_date        TEXT    NOT NULL,
    length_days     INTEGER NOT NULL,
    pattern_type    TEXT,
    data_type       TEXT,
    quality         REAL,
    shapelet_values TEXT    NOT NULL,   -- JSON array of floats
    source_file     TEXT,
    UNIQUE(dataset_key, shapelet_id, source_file)
);

-- Ingestion audit log
CREATE TABLE IF NOT EXISTS ingestion_runs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at  TEXT    NOT NULL,
    finished_at TEXT,
    status      TEXT    DEFAULT 'running',
    total_files INTEGER DEFAULT 0,
    total_rows  INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_shapelets_site
    ON shapelets(site_key);
CREATE INDEX IF NOT EXISTS idx_shapelets_year
    ON shapelets(year);
CREATE INDEX IF NOT EXISTS idx_shapelets_dates
    ON shapelets(start_date, end_date);
"""


# ---------------------------------------------------------------------------
# Database connection / init
# ---------------------------------------------------------------------------

def init_db(db_path: str | Path) -> sqlite3.Connection:
    """
    Open (or create) the SQLite database and ensure the schema exists.

    Parameters
    ----------
    db_path : str or Path
        Path to the .db file.  Created if it doesn't exist yet.

    Returns
    -------
    sqlite3.Connection
    """
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.executescript(_SCHEMA_SQL)
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# Writes
# ---------------------------------------------------------------------------

def upsert_site(conn: sqlite3.Connection, record: dict[str, Any]) -> str:
    """Insert or update a site row.  Returns the site_key."""
    site_key = f"{record['state']}_{record['county']}_{record['site_num']}"
    conn.execute(
        """
        INSERT INTO sites (site_key, state, county, site_num, latitude, longitude)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(site_key) DO UPDATE SET
            latitude  = excluded.latitude,
            longitude = excluded.longitude
        """,
        (
            site_key,
            record["state"],
            record["county"],
            record["site_num"],
            record["latitude"],
            record["longitude"],
        ),
    )
    return site_key


def upsert_pollutant(conn: sqlite3.Connection, parameter_code: str) -> None:
    """Ensure a row exists in the pollutants table for this code."""
    if parameter_code is None:
        return
    conn.execute(
        """
        INSERT OR IGNORE INTO pollutants (parameter_code)
        VALUES (?)
        """,
        (parameter_code,),
    )


def insert_shapelets(
    conn: sqlite3.Connection,
    records: list[dict[str, Any]],
    *,
    batch_size: int = 500,
) -> int:
    """
    Insert a batch of flat record dicts into the shapelets table.

    Automatically upserts corresponding site rows.

    Parameters
    ----------
    conn : sqlite3.Connection
    records : list[dict]
        Flat records as produced by :func:`helpers.records.iter_records`.
    batch_size : int
        Rows per ``executemany`` call (controls memory).

    Returns
    -------
    int
        Number of rows inserted.
    """
    rows_inserted = 0
    sites_seen: set[str] = set()
    pollutants_seen: set[str] = set()

    for start in range(0, len(records), batch_size):
        chunk = records[start : start + batch_size]

        # Upsert sites first (deduplicated within this chunk)
        for rec in chunk:
            sk = f"{rec['state']}_{rec['county']}_{rec['site_num']}"
            if sk not in sites_seen:
                upsert_site(conn, rec)
                sites_seen.add(sk)

        # Parse parameter_code from pattern_type (e.g. "daily_42401")
        db_rows = []
        for rec in chunk:
            site_key = f"{rec['state']}_{rec['county']}_{rec['site_num']}"
            param_code = _extract_param_code(rec.get("pattern_type", ""))

            # Ensure pollutant exists in lookup table
            if param_code and param_code not in pollutants_seen:
                upsert_pollutant(conn, param_code)
                pollutants_seen.add(param_code)
            db_rows.append((
                rec["dataset_key"],
                rec["shapelet_id"],
                site_key,
                param_code,
                rec["year"],
                rec["start_date"].isoformat(),
                rec["end_date"].isoformat(),
                rec["length_days"],
                rec.get("pattern_type"),
                rec.get("data_type"),
                rec.get("quality"),
                json.dumps(rec["shapelet_values"]),
                rec.get("source_file"),
            ))

        conn.executemany(
            """
            INSERT OR IGNORE INTO shapelets (
                dataset_key, shapelet_id, site_key, parameter_code,
                year, start_date, end_date, length_days,
                pattern_type, data_type, quality, shapelet_values,
                source_file
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            db_rows,
        )
        rows_inserted += len(db_rows)

    conn.commit()
    return rows_inserted


# ---------------------------------------------------------------------------
# Ingestion-run helpers
# ---------------------------------------------------------------------------

def start_ingestion_run(conn: sqlite3.Connection) -> int:
    """Create a new run and return its id."""
    cur = conn.execute(
        "INSERT INTO ingestion_runs (started_at) VALUES (?)",
        (datetime.datetime.now(datetime.timezone.utc).isoformat(),),
    )
    conn.commit()
    return cur.lastrowid  # type: ignore[return-value]


def finish_ingestion_run(
    conn: sqlite3.Connection,
    run_id: int,
    *,
    status: str = "completed",
    total_files: int = 0,
    total_rows: int = 0,
    error_count: int = 0,
) -> None:
    """Mark a run as finished with summary stats."""
    conn.execute(
        """
        UPDATE ingestion_runs
        SET finished_at = ?, status = ?,
            total_files = ?, total_rows = ?, error_count = ?
        WHERE id = ?
        """,
        (
            datetime.datetime.now(datetime.timezone.utc).isoformat(),
            status,
            total_files,
            total_rows,
            error_count,
            run_id,
        ),
    )
    conn.commit()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_param_code(pattern_type: str) -> str | None:
    """
    Pull a numeric parameter code from pattern_type.

    Example: ``"daily_42401"`` → ``"42401"``
    """
    parts = pattern_type.split("_")
    for part in parts:
        if part.isdigit():
            return part
    return None
