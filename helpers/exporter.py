# -*- coding: utf-8 -*-
"""
ArcGIS CSV export helpers.

Provides query builders and CSV formatting utilities for exporting
subsets of the shapelet database into ArcGIS-ready CSV files.
"""

from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd


# ---------------------------------------------------------------------------
# Discovery queries  –  what's available in the database?
# ---------------------------------------------------------------------------

def get_available_years(conn: sqlite3.Connection) -> list[int]:
    """Return sorted list of distinct years in the shapelets table."""
    rows = conn.execute("SELECT DISTINCT year FROM shapelets ORDER BY year").fetchall()
    return [r[0] for r in rows]


def get_available_pollutants(conn: sqlite3.Connection) -> list[dict]:
    """Return list of {parameter_code, name, unit} for all known pollutants."""
    rows = conn.execute(
        "SELECT parameter_code, name, unit FROM pollutants ORDER BY parameter_code"
    ).fetchall()
    return [
        {"parameter_code": r[0], "name": r[1] or r[0], "unit": r[2] or ""}
        for r in rows
    ]


def get_available_sites(conn: sqlite3.Connection) -> list[dict]:
    """Return list of {site_key, state, county, site_num, latitude, longitude}."""
    rows = conn.execute(
        "SELECT site_key, state, county, site_num, latitude, longitude "
        "FROM sites ORDER BY state, county, site_num"
    ).fetchall()
    return [
        {
            "site_key": r[0],
            "state": r[1],
            "county": r[2],
            "site_num": r[3],
            "latitude": r[4],
            "longitude": r[5],
        }
        for r in rows
    ]


def get_available_pattern_types(conn: sqlite3.Connection) -> list[str]:
    """Return sorted list of distinct pattern_type values."""
    rows = conn.execute(
        "SELECT DISTINCT pattern_type FROM shapelets ORDER BY pattern_type"
    ).fetchall()
    return [r[0] for r in rows if r[0]]


def get_row_count(conn: sqlite3.Connection) -> int:
    """Total shapelets in the database."""
    return conn.execute("SELECT COUNT(*) FROM shapelets").fetchone()[0]


def get_date_range(conn: sqlite3.Connection) -> tuple[str, str]:
    """Return (min_start_date, max_end_date) across all shapelets."""
    row = conn.execute(
        "SELECT MIN(start_date), MAX(end_date) FROM shapelets"
    ).fetchone()
    return row[0], row[1]


# ---------------------------------------------------------------------------
# Filtered query builder
# ---------------------------------------------------------------------------

def build_export_query(
    *,
    years: list[int] | None = None,
    sites: list[str] | None = None,
    pollutants: list[str] | None = None,
    pattern_types: list[str] | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> tuple[str, list[Any]]:
    """
    Build a parameterised SQL query that joins shapelets → sites.

    Returns (sql_string, params_list).
    """
    sql = """
        SELECT
            s.id,
            s.dataset_key,
            s.shapelet_id,
            s.site_key,
            si.state,
            si.county,
            si.site_num,
            si.latitude,
            si.longitude,
            s.parameter_code,
            s.year,
            s.start_date,
            s.end_date,
            s.length_days,
            s.pattern_type,
            s.data_type,
            s.quality,
            s.shapelet_values,
            s.source_file
        FROM shapelets s
        LEFT JOIN sites si ON s.site_key = si.site_key
        WHERE 1=1
    """
    params: list[Any] = []

    if years:
        placeholders = ",".join("?" for _ in years)
        sql += f"  AND s.year IN ({placeholders})\n"
        params.extend(years)

    if sites:
        placeholders = ",".join("?" for _ in sites)
        sql += f"  AND s.site_key IN ({placeholders})\n"
        params.extend(sites)

    if pollutants:
        placeholders = ",".join("?" for _ in pollutants)
        sql += f"  AND s.parameter_code IN ({placeholders})\n"
        params.extend(pollutants)

    if pattern_types:
        placeholders = ",".join("?" for _ in pattern_types)
        sql += f"  AND s.pattern_type IN ({placeholders})\n"
        params.extend(pattern_types)

    if date_from:
        sql += "  AND s.start_date >= ?\n"
        params.append(date_from)

    if date_to:
        sql += "  AND s.end_date <= ?\n"
        params.append(date_to)

    sql += "  ORDER BY s.year, si.state, si.county, s.start_date"

    return sql, params


# ---------------------------------------------------------------------------
# DataFrame helpers (used by Streamlit / notebooks)
# ---------------------------------------------------------------------------

_DF_COLUMNS = [
    "ID", "DatasetKey", "ShapeletID", "SiteKey",
    "State", "County", "SiteNum", "Latitude", "Longitude",
    "ParameterCode", "Year", "StartDate", "EndDate",
    "LengthDays", "PatternType", "DataType", "Quality",
    "ShapeletValues", "SourceFile",
]


def query_to_dataframe(
    conn: sqlite3.Connection,
    sql: str,
    params: list[Any],
) -> pd.DataFrame:
    """
    Run the export query and return results as a pandas DataFrame.

    This avoids writing to disk — useful for in-app previews.
    """
    df = pd.read_sql_query(sql, conn, params=params)
    df.columns = _DF_COLUMNS
    return df


def site_summary_dataframe(
    conn: sqlite3.Connection,
    *,
    years: list[int] | None = None,
    pollutants: list[str] | None = None,
) -> pd.DataFrame:
    """Return the site-level summary as a DataFrame."""
    sql = """
        SELECT
            si.site_key,
            si.state,
            si.county,
            si.site_num,
            si.latitude,
            si.longitude,
            COUNT(*)            AS shapelet_count,
            AVG(s.quality)      AS avg_quality,
            MIN(s.quality)      AS min_quality,
            MAX(s.quality)      AS max_quality,
            MIN(s.start_date)   AS earliest_date,
            MAX(s.end_date)     AS latest_date,
            GROUP_CONCAT(DISTINCT s.parameter_code) AS pollutants,
            GROUP_CONCAT(DISTINCT s.year)            AS years
        FROM shapelets s
        LEFT JOIN sites si ON s.site_key = si.site_key
        WHERE 1=1
    """
    params: list[Any] = []
    if years:
        placeholders = ",".join("?" for _ in years)
        sql += f"  AND s.year IN ({placeholders})\n"
        params.extend(years)
    if pollutants:
        placeholders = ",".join("?" for _ in pollutants)
        sql += f"  AND s.parameter_code IN ({placeholders})\n"
        params.extend(pollutants)
    sql += "  GROUP BY si.site_key ORDER BY si.state, si.county"

    df = pd.read_sql_query(sql, conn, params=params)
    df.columns = [
        "SiteKey", "State", "County", "SiteNum",
        "Latitude", "Longitude",
        "ShapeletCount", "AvgQuality", "MinQuality", "MaxQuality",
        "EarliestDate", "LatestDate", "Pollutants", "Years",
    ]
    return df


# ---------------------------------------------------------------------------
# CSV writing
# ---------------------------------------------------------------------------

# Column spec: (csv_header, description, ArcGIS type hint)
_CSV_COLUMNS = [
    ("ID",              "Auto-increment row ID",            "LONG"),
    ("DatasetKey",      "Full dataset identifier",          "TEXT"),
    ("ShapeletID",      "Shapelet index within dataset",    "SHORT"),
    ("SiteKey",         "Site identifier (state_county_#)", "TEXT"),
    ("State",           "US state name",                    "TEXT"),
    ("County",          "County name",                      "TEXT"),
    ("SiteNum",         "EPA site number",                  "SHORT"),
    ("Latitude",        "Site latitude  (WGS-84)",          "DOUBLE"),
    ("Longitude",       "Site longitude (WGS-84)",          "DOUBLE"),
    ("ParameterCode",   "EPA AQS parameter code",           "TEXT"),
    ("Year",            "Observation year",                  "SHORT"),
    ("StartDate",       "Shapelet start (ISO-8601)",        "DATE"),
    ("EndDate",         "Shapelet end   (ISO-8601)",        "DATE"),
    ("LengthDays",      "Shapelet window in days",          "SHORT"),
    ("PatternType",     "Time-series pattern label",        "TEXT"),
    ("DataType",        "Aggregation / transform method",   "TEXT"),
    ("Quality",         "Shapelet quality score",           "DOUBLE"),
    ("ShapeletValues",  "JSON array of daily values",       "TEXT"),
    ("SourceFile",      "Originating pickle filename",      "TEXT"),
]


def _format_row(row: tuple) -> list[str]:
    """
    Convert a raw SQLite row tuple into ArcGIS-friendly string values.

    - Dates stay ISO-8601
    - Floats keep full precision
    - None → empty string
    """
    formatted = []
    for val in row:
        if val is None:
            formatted.append("")
        elif isinstance(val, float):
            formatted.append(f"{val}")
        else:
            formatted.append(str(val))
    return formatted


def write_csv(
    conn: sqlite3.Connection,
    sql: str,
    params: list[Any],
    out_path: Path,
    *,
    expand_values: bool = False,
    max_expand: int = 31,
) -> int:
    """
    Execute *sql* and write results to a UTF-8 CSV at *out_path*.

    Parameters
    ----------
    conn : sqlite3.Connection
    sql, params : from :func:`build_export_query`
    out_path : Path
        Destination CSV file.
    expand_values : bool
        If True, explode ShapeletValues JSON into individual Day_1 … Day_N
        columns instead of a single JSON text column.
    max_expand : int
        Maximum number of day columns when *expand_values* is True.

    Returns
    -------
    int
        Number of data rows written.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cursor = conn.execute(sql, params)
    rows_written = 0

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # ── Header ──
        if expand_values:
            base_headers = [c[0] for c in _CSV_COLUMNS if c[0] != "ShapeletValues"]
            day_headers = [f"Day_{i+1}" for i in range(max_expand)]
            writer.writerow(base_headers + day_headers)
        else:
            writer.writerow([c[0] for c in _CSV_COLUMNS])

        # ── Data rows ──
        for raw_row in cursor:
            row_list = list(raw_row)

            if expand_values:
                # ShapeletValues is at index 17 in the SELECT
                json_vals = row_list[17]
                values = json.loads(json_vals) if json_vals else []
                # Pad / truncate to max_expand columns
                padded = (values + [None] * max_expand)[:max_expand]

                base_row = row_list[:17] + row_list[18:]  # skip JSON col
                formatted = _format_row(tuple(base_row))
                formatted += [f"{v}" if v is not None else "" for v in padded]
            else:
                formatted = _format_row(tuple(row_list))

            writer.writerow(formatted)
            rows_written += 1

    return rows_written


def write_site_summary_csv(
    conn: sqlite3.Connection,
    out_path: Path,
    *,
    years: list[int] | None = None,
    pollutants: list[str] | None = None,
) -> int:
    """
    Write a site-level summary CSV (one row per site) with aggregate stats.

    Useful for creating a single point layer in ArcGIS with per-site metrics.
    """
    sql = """
        SELECT
            si.site_key,
            si.state,
            si.county,
            si.site_num,
            si.latitude,
            si.longitude,
            COUNT(*)            AS shapelet_count,
            AVG(s.quality)      AS avg_quality,
            MIN(s.quality)      AS min_quality,
            MAX(s.quality)      AS max_quality,
            MIN(s.start_date)   AS earliest_date,
            MAX(s.end_date)     AS latest_date,
            GROUP_CONCAT(DISTINCT s.parameter_code) AS pollutants,
            GROUP_CONCAT(DISTINCT s.year)            AS years
        FROM shapelets s
        LEFT JOIN sites si ON s.site_key = si.site_key
        WHERE 1=1
    """
    params: list[Any] = []

    if years:
        placeholders = ",".join("?" for _ in years)
        sql += f"  AND s.year IN ({placeholders})\n"
        params.extend(years)
    if pollutants:
        placeholders = ",".join("?" for _ in pollutants)
        sql += f"  AND s.parameter_code IN ({placeholders})\n"
        params.extend(pollutants)

    sql += "  GROUP BY si.site_key ORDER BY si.state, si.county"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    cursor = conn.execute(sql, params)
    rows_written = 0

    headers = [
        "SiteKey", "State", "County", "SiteNum",
        "Latitude", "Longitude",
        "ShapeletCount", "AvgQuality", "MinQuality", "MaxQuality",
        "EarliestDate", "LatestDate",
        "Pollutants", "Years",
    ]

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in cursor:
            writer.writerow(_format_row(row))
            rows_written += 1

    return rows_written
