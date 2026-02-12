# -*- coding: utf-8 -*-
"""
Main ingestion pipeline.

Discovers shapelet pickle files, flattens them into records,
validates, and writes them to a SQLite database.

Usage examples
--------------
Dry run (print summary, don't write):
    python main.py --dry-run

Full ingestion with default config paths:
    python main.py

Override paths:
    python main.py --input-dir path/to/data --db path/to/air.db

Limit files processed (for quick testing):
    python main.py --limit 2 --dry-run
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from config import get_data_path, get_database_path, load_config
from helpers.loader import discover_files, load_from_path
from helpers.parser import parse_filename, parse_dataset_key
from helpers.records import iter_records
from helpers.validator import validate_record
from helpers.db import init_db, insert_shapelets, start_ingestion_run, finish_ingestion_run


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ingest shapelet pickle files into a SQLite database.",
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=None,
        help="Directory containing .pkl / .zip data files.  "
             "Defaults to data_path from .config.",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=None,
        help="Path to the SQLite database file.  "
             "Defaults to <database_path>/air.db.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and validate only — do not write to the database.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Process at most N files (useful for quick tests).",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print extra detail while running.",
    )
    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# Reporting helpers
# ---------------------------------------------------------------------------

def print_file_summary(
    path: Path,
    file_meta: dict,
    key_meta: dict,
    valid: list[dict],
    errors: list[tuple[dict, list[str]]],
) -> None:
    """Print a human-readable summary for one file."""
    print(f"\n{'─' * 60}")
    print(f"  File : {path.name}")
    print(f"  Key  : {key_meta}")
    print(f"  Valid: {len(valid)}   Errors: {len(errors)}")
    if valid:
        dates = [r["start_date"] for r in valid]
        print(f"  Dates: {min(dates)} → {max(dates)}")
    if errors:
        for rec, errs in errors[:3]:
            print(f"  ⚠ shapelet_id={rec.get('shapelet_id','?')}: {errs}")
        if len(errors) > 3:
            print(f"  ... and {len(errors) - 3} more errors")


def print_run_summary(
    total_files: int,
    total_valid: int,
    total_errors: int,
    db_path: Path | None,
) -> None:
    """Print the final pipeline summary."""
    print(f"\n{'═' * 60}")
    print("  PIPELINE SUMMARY")
    print(f"{'═' * 60}")
    print(f"  Files processed : {total_files}")
    print(f"  Valid records   : {total_valid}")
    print(f"  Error records   : {total_errors}")
    if db_path:
        print(f"  Database        : {db_path}")
    print(f"{'═' * 60}\n")


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run(args: argparse.Namespace) -> None:
    # Resolve input directory
    input_dir = args.input_dir or get_data_path()
    if not input_dir.is_dir():
        print(f"Error: input directory does not exist: {input_dir}", file=sys.stderr)
        sys.exit(1)

    # Resolve output database
    db_path: Path | None = None
    if not args.dry_run:
        db_path = args.db or (get_database_path() / "air.db")

    # Discover files
    files = discover_files(input_dir)
    if args.limit:
        files = files[: args.limit]

    if not files:
        print("No data files found in:", input_dir)
        sys.exit(0)

    print(f"Found {len(files)} file(s) in {input_dir}")

    # Open DB (if writing)
    conn = None
    run_id = None
    if db_path:
        conn = init_db(db_path)
        run_id = start_ingestion_run(conn)
        if args.verbose:
            print(f"Database: {db_path}  (run_id={run_id})")

    # Counters
    total_valid = 0
    total_errors = 0

    for path in files:
        # 1) Parse filename metadata
        try:
            file_meta = parse_filename(path.name)
        except ValueError as exc:
            print(f"  SKIP {path.name}: {exc}")
            total_errors += 1
            continue

        # 2) Load pickle
        try:
            data = load_from_path(path)
        except Exception as exc:
            print(f"  SKIP {path.name}: load error — {exc}")
            total_errors += 1
            continue

        # 3) Parse dataset key
        dataset_key = list(data.keys())[0]
        try:
            key_meta = parse_dataset_key(dataset_key)
        except ValueError:
            key_meta = {"raw_key": dataset_key}

        # 4) Flatten to records
        records = list(iter_records(data, source_file=path.name))

        # 5) Validate
        valid_records: list[dict] = []
        error_records: list[tuple[dict, list[str]]] = []

        for rec in records:
            ok, errs = validate_record(rec)
            if ok:
                valid_records.append(rec)
            else:
                error_records.append((rec, errs))

        total_valid += len(valid_records)
        total_errors += len(error_records)

        # 6) Report
        if args.verbose or args.dry_run:
            print_file_summary(path, file_meta, key_meta, valid_records, error_records)

        # 7) Write to DB
        if conn and valid_records:
            inserted = insert_shapelets(conn, valid_records)
            if args.verbose:
                print(f"  → inserted {inserted} rows")

    # Finalise
    if conn and run_id is not None:
        finish_ingestion_run(
            conn,
            run_id,
            total_files=len(files),
            total_rows=total_valid,
            error_count=total_errors,
        )
        conn.close()

    print_run_summary(len(files), total_valid, total_errors, db_path)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    args = parse_args()
    run(args)
