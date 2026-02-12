# -*- coding: utf-8 -*-
"""
Inspect a CSV file and generate a comprehensive structure report.

Designed to document the column layout, data types, value ranges, and
overall shape of CSV files — particularly useful for identifying a
template schema for writing data to CSVs that ArcGIS Pro 3.5 can import.

Usage:
    python scripts/inspect_csv_structure.py --input path\\to\\file.csv
    python scripts/inspect_csv_structure.py --input path\\to\\file.csv --output report.txt
    python scripts/inspect_csv_structure.py --input path\\to\\file.csv --sample-rows 10
    python scripts/inspect_csv_structure.py   # Opens file dialog to select file interactively
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from tkinter import Tk, filedialog

import warnings

import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# File dialog helper
# ---------------------------------------------------------------------------

def prompt_for_file() -> str | None:
    """Open a file dialog to select a .csv file."""
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    file_path = filedialog.askopenfilename(
        title="Select a CSV file",
        filetypes=[
            ("CSV files", "*.csv"),
            ("Text files", "*.txt;*.tsv"),
            ("All files", "*.*"),
        ],
    )
    root.destroy()
    return file_path if file_path else None


# ---------------------------------------------------------------------------
# Analysis helpers
# ---------------------------------------------------------------------------

def _file_metadata(path: Path) -> list[str]:
    """Basic file-level info."""
    size = path.stat().st_size
    if size < 1024:
        size_label = f"{size} B"
    elif size < 1024 ** 2:
        size_label = f"{size / 1024:.1f} KB"
    else:
        size_label = f"{size / 1024 ** 2:.1f} MB"

    return [
        "FILE METADATA",
        f"  Path      : {path}",
        f"  Size      : {size_label}",
        f"  Extension : {path.suffix}",
    ]


def _shape_summary(df: pd.DataFrame) -> list[str]:
    """Row / column counts."""
    return [
        "SHAPE",
        f"  Rows    : {len(df):,}",
        f"  Columns : {len(df.columns)}",
    ]


def _column_types(df: pd.DataFrame) -> list[str]:
    """Per-column dtype table."""
    lines = ["COLUMN TYPES"]
    header = f"  {'#':<4} {'Column':<35} {'Pandas dtype':<18} {'ArcGIS-compatible type'}"
    lines.append(header)
    lines.append("  " + "─" * len(header.strip()))

    for idx, col in enumerate(df.columns):
        dtype = str(df[col].dtype)
        arc_type = _pandas_to_arcgis_type(df[col])
        lines.append(f"  {idx:<4} {col:<35} {dtype:<18} {arc_type}")

    return lines


def _pandas_to_arcgis_type(series: pd.Series) -> str:
    """
    Map a pandas Series dtype to the closest ArcGIS Pro field type.

    ArcGIS Pro 3.x field types:
        TEXT, SHORT, LONG, FLOAT, DOUBLE, DATE, BLOB, GUID, OID
    """
    dtype = series.dtype

    if pd.api.types.is_bool_dtype(dtype):
        return "SHORT (boolean 0/1)"
    if pd.api.types.is_integer_dtype(dtype):
        mn, mx = series.min(), series.max()
        if pd.isna(mn):
            return "LONG"
        if -32_768 <= mn and mx <= 32_767:
            return "SHORT"
        return "LONG"
    if pd.api.types.is_float_dtype(dtype):
        return "DOUBLE"
    if pd.api.types.is_datetime64_any_dtype(dtype):
        return "DATE"
    if pd.api.types.is_object_dtype(dtype):
        # Check if this looks like dates stored as strings
        if _looks_like_date(series):
            return "DATE (parsed from text)"
        return "TEXT"
    return "TEXT"


def _missing_values(df: pd.DataFrame) -> list[str]:
    """Null / NaN summary per column."""
    lines = ["MISSING VALUES"]
    total = len(df)
    any_missing = False

    for col in df.columns:
        n_missing = df[col].isna().sum()
        if n_missing > 0:
            any_missing = True
            pct = n_missing / total * 100
            lines.append(f"  {col:<35} {n_missing:>8,} missing  ({pct:.1f}%)")

    if not any_missing:
        lines.append("  No missing values detected.")

    return lines


def _numeric_summary(df: pd.DataFrame) -> list[str]:
    """Min / max / mean / std for numeric columns."""
    num_cols = df.select_dtypes(include="number").columns
    if len(num_cols) == 0:
        return ["NUMERIC SUMMARY", "  (no numeric columns)"]

    lines = ["NUMERIC SUMMARY"]
    header = f"  {'Column':<35} {'Min':>12} {'Max':>12} {'Mean':>12} {'Std':>12}"
    lines.append(header)
    lines.append("  " + "─" * len(header.strip()))

    for col in num_cols:
        s = df[col]
        lines.append(
            f"  {col:<35} "
            f"{s.min():>12.4g} "
            f"{s.max():>12.4g} "
            f"{s.mean():>12.4g} "
            f"{s.std():>12.4g}"
        )

    return lines


def _text_summary(df: pd.DataFrame) -> list[str]:
    """Unique counts and sample values for text / object columns."""
    obj_cols = df.select_dtypes(include="object").columns
    if len(obj_cols) == 0:
        return ["TEXT / CATEGORICAL SUMMARY", "  (no text columns)"]

    lines = ["TEXT / CATEGORICAL SUMMARY"]
    for col in obj_cols:
        n_unique = df[col].nunique(dropna=True)
        max_len = df[col].dropna().astype(str).str.len().max() if len(df[col].dropna()) > 0 else 0
        sample_vals = df[col].dropna().unique()[:5].tolist()
        lines.append(f"  {col}")
        lines.append(f"    Unique values : {n_unique:,}")
        lines.append(f"    Max length    : {max_len}")
        lines.append(f"    Sample values : {sample_vals}")

    return lines


def _date_summary(df: pd.DataFrame) -> list[str]:
    """Range info for datetime columns."""
    dt_cols = df.select_dtypes(include="datetime").columns
    if len(dt_cols) == 0:
        return ["DATE SUMMARY", "  (no datetime columns)"]

    lines = ["DATE SUMMARY"]
    for col in dt_cols:
        s = df[col].dropna()
        lines.append(f"  {col}")
        lines.append(f"    Min  : {s.min()}")
        lines.append(f"    Max  : {s.max()}")
        lines.append(f"    Span : {s.max() - s.min()}")

    return lines


def _duplicate_check(df: pd.DataFrame) -> list[str]:
    """Check for fully duplicated rows."""
    n_dup = df.duplicated().sum()
    lines = ["DUPLICATE ROWS"]
    if n_dup:
        lines.append(f"  {n_dup:,} fully duplicated row(s) detected.")
    else:
        lines.append("  No fully duplicated rows.")
    return lines


def _coordinate_columns(df: pd.DataFrame) -> list[str]:
    """
    Identify likely latitude / longitude columns — important for ArcGIS
    XY Event layers.
    """
    lines = ["COORDINATE / SPATIAL COLUMNS (ArcGIS XY detection)"]
    lat_candidates: list[str] = []
    lon_candidates: list[str] = []

    for col in df.columns:
        low = col.lower()
        if any(kw in low for kw in ("lat", "latitude", "y_coord", "ycoord")):
            lat_candidates.append(col)
        elif any(kw in low for kw in ("lon", "long", "longitude", "x_coord", "xcoord")):
            lon_candidates.append(col)

    if lat_candidates:
        lines.append(f"  Likely latitude column(s)  : {lat_candidates}")
    if lon_candidates:
        lines.append(f"  Likely longitude column(s) : {lon_candidates}")
    if not lat_candidates and not lon_candidates:
        lines.append("  No obvious lat/lon columns found by name.")
        lines.append("  Tip: ArcGIS Pro's 'XY Table to Point' tool expects columns")
        lines.append("       named Latitude/Longitude (or X/Y) with numeric values.")

    return lines


def _sample_rows(df: pd.DataFrame, n: int) -> list[str]:
    """Show first N rows as a formatted table."""
    lines = [f"SAMPLE ROWS (first {min(n, len(df))})"]
    sample = df.head(n).to_string(index=False, max_colwidth=40)
    for row in sample.split("\n"):
        lines.append(f"  {row}")
    return lines


def _arcgis_import_notes(df: pd.DataFrame) -> list[str]:
    """
    Actionable notes for importing this CSV into ArcGIS Pro 3.5.
    """
    lines = [
        "ARCGIS PRO 3.5 IMPORT NOTES",
        "  Import method: Map tab → Add Data → XY Table to Point (if spatial)",
        "                 or Add Data → Table (for non-spatial attribute join)",
        "",
    ]

    # Column name issues
    bad_names = [c for c in df.columns if " " in c or any(ch in c for ch in ".-/\\()[]{}!@#$%^&*")]
    if bad_names:
        lines.append("  ⚠  Columns with spaces or special characters (may cause issues):")
        for c in bad_names:
            safe = c.replace(" ", "_")
            for ch in ".-/\\()[]{}!@#$%^&*":
                safe = safe.replace(ch, "_")
            lines.append(f"     '{c}'  →  suggest renaming to '{safe}'")
        lines.append("")

    # Long column names (ArcGIS shapefile limit = 10 chars, but geodatabase = 64)
    long_names = [c for c in df.columns if len(c) > 64]
    if long_names:
        lines.append("  ⚠  Column names exceeding 64 characters (geodatabase limit):")
        for c in long_names:
            lines.append(f"     '{c}' ({len(c)} chars)")
        lines.append("")

    # Encoding tip
    lines.append("  Encoding: Ensure CSV is saved as UTF-8 (ArcGIS Pro default).")

    # Date format tip
    dt_obj_cols = [
        c for c in df.select_dtypes(include="object").columns
        if _looks_like_date(df[c])
    ]
    dt_native = list(df.select_dtypes(include="datetime").columns)
    all_date_cols = dt_native + dt_obj_cols
    if all_date_cols:
        lines.append(f"  Date columns detected: {all_date_cols}")
        lines.append("  Tip: ArcGIS Pro parses ISO-8601 dates (YYYY-MM-DD) most reliably.")

    return lines


def _looks_like_date(series: pd.Series) -> bool:
    """Heuristic: can the first 20 non-null values be parsed as dates?"""
    sample = series.dropna().head(20)
    if len(sample) == 0:
        return False
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            pd.to_datetime(sample, format="mixed")
        return True
    except (ValueError, TypeError):
        return False


# ---------------------------------------------------------------------------
# Report builder
# ---------------------------------------------------------------------------

def build_report(
    path: str,
    sample_rows: int,
    encoding: str,
    separator: str,
) -> str:
    """Load the CSV and assemble the full report string."""
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"File not found: {csv_path}")

    df = pd.read_csv(csv_path, encoding=encoding, sep=separator)

    sections: list[list[str]] = [
        ["CSV Structure Report", "=" * 60],
        _file_metadata(csv_path),
        _shape_summary(df),
        _column_types(df),
        _missing_values(df),
        _numeric_summary(df),
        _text_summary(df),
        _date_summary(df),
        _duplicate_check(df),
        _coordinate_columns(df),
        _sample_rows(df, sample_rows),
        _arcgis_import_notes(df),
    ]

    return "\n\n".join("\n".join(sec) for sec in sections) + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect a CSV file and generate a comprehensive structure report."
    )
    parser.add_argument(
        "--input",
        help="Path to a .csv file (will prompt if not provided)",
    )
    parser.add_argument(
        "--output",
        help="Optional path to write the report (prints to stdout by default)",
    )
    parser.add_argument(
        "--sample-rows",
        type=int,
        default=5,
        help="Number of sample rows to display (default: 5)",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="CSV file encoding (default: utf-8)",
    )
    parser.add_argument(
        "--separator",
        default=",",
        help="Column separator (default: comma)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    input_path = args.input
    if not input_path:
        print("No input file specified. Opening file dialog...")
        input_path = prompt_for_file()
        if not input_path:
            print("No file selected. Exiting.")
            sys.exit(1)
        print(f"Selected: {input_path}\n")

    report = build_report(
        input_path,
        sample_rows=args.sample_rows,
        encoding=args.encoding,
        separator=args.separator,
    )

    if args.output:
        out = Path(args.output)
        out.write_text(report, encoding="utf-8")
        print(f"Report written to {out}")
    else:
        print(report)


if __name__ == "__main__":
    main()
