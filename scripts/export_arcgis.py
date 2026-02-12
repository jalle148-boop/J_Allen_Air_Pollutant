# -*- coding: utf-8 -*-
"""
Interactive ArcGIS CSV Export Pipeline.

Connects to the shapelet SQLite database and walks the user through
selecting filters (years, sites, pollutants, date ranges) then writes
ArcGIS-ready CSV files to the configured export directory.

Usage
-----
    python scripts/export_arcgis.py              # interactive mode
    python scripts/export_arcgis.py --quick      # export everything, no prompts
    python scripts/export_arcgis.py --help       # show all options
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

# Ensure project root is on sys.path so helpers / config are importable
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from config import get_database_path, get_arcgis_inputs_path  # noqa: E402
from helpers.exporter import (                                  # noqa: E402
    build_export_query,
    get_available_pollutants,
    get_available_sites,
    get_available_years,
    get_available_pattern_types,
    get_date_range,
    get_row_count,
    write_csv,
    write_site_summary_csv,
)

# ── ANSI colours (Windows 10+ supports them in modern terminals) ──
_BOLD  = "\033[1m"
_CYAN  = "\033[96m"
_GREEN = "\033[92m"
_YELLOW = "\033[93m"
_RESET = "\033[0m"


# ═══════════════════════════════════════════════════════════════════
# CLI argument parsing
# ═══════════════════════════════════════════════════════════════════

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Export subsets of the shapelet database to ArcGIS-ready CSVs.",
    )
    p.add_argument(
        "--db", type=Path, default=None,
        help="Path to the SQLite database.  Default: <database_path>/air.db",
    )
    p.add_argument(
        "--out-dir", type=Path, default=None,
        help="Output directory for CSVs.  Default: arcgis_inputs_path from .config",
    )
    p.add_argument(
        "--quick", action="store_true",
        help="Skip interactive prompts — export ALL data in one shot.",
    )
    p.add_argument(
        "--expand-values", action="store_true",
        help="Expand shapelet JSON array into individual Day_N columns.",
    )
    return p.parse_args(argv)


# ═══════════════════════════════════════════════════════════════════
# Helpers for interactive prompts
# ═══════════════════════════════════════════════════════════════════

def _hr(char: str = "─", width: int = 60) -> str:
    return char * width


def _prompt(msg: str, default: str = "") -> str:
    """Prompt the user with an optional default value."""
    suffix = f" [{default}]" if default else ""
    raw = input(f"{_CYAN}{msg}{suffix}: {_RESET}").strip()
    return raw if raw else default


def _prompt_yes_no(msg: str, default: bool = True) -> bool:
    hint = "Y/n" if default else "y/N"
    raw = _prompt(f"{msg} ({hint})", "y" if default else "n")
    return raw.lower() in ("y", "yes", "1", "true")


def _pick_many(
    label: str,
    items: list[dict],
    display_key: str,
    value_key: str,
) -> list[str] | None:
    """
    Show a numbered list; let the user type comma-separated indices.
    Returns selected values or None (= all / no filter).
    """
    print(f"\n{_BOLD}{label}{_RESET}")
    print(f"  0) {_YELLOW}(all — no filter){_RESET}")
    for i, item in enumerate(items, start=1):
        print(f"  {i}) {item[display_key]}")

    raw = _prompt("Enter numbers separated by commas, or 0 for all", "0")
    if raw == "0":
        return None

    chosen: list[str] = []
    for token in raw.split(","):
        token = token.strip()
        if token.isdigit():
            idx = int(token) - 1
            if 0 <= idx < len(items):
                chosen.append(items[idx][value_key])
    return chosen if chosen else None


def _pick_years(available: list[int]) -> list[int] | None:
    """Interactive year picker — supports individual years and ranges."""
    print(f"\n{_BOLD}Available years:{_RESET}  {', '.join(map(str, available))}")
    raw = _prompt(
        "Enter years / ranges (e.g. 2004,2006-2010) or 'all'", "all"
    )
    if raw.lower() == "all":
        return None

    selected: set[int] = set()
    for token in raw.split(","):
        token = token.strip()
        if "-" in token:
            parts = token.split("-")
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                lo, hi = int(parts[0]), int(parts[1])
                selected.update(y for y in available if lo <= y <= hi)
        elif token.isdigit():
            y = int(token)
            if y in available:
                selected.add(y)
    return sorted(selected) if selected else None


def _pick_date_range(min_date: str, max_date: str) -> tuple[str | None, str | None]:
    """Prompt for optional start / end date bounds (ISO-8601)."""
    print(f"\n{_BOLD}Date range in database:{_RESET}  {min_date}  →  {max_date}")
    if not _prompt_yes_no("Filter by date range?", default=False):
        return None, None
    date_from = _prompt("Start date (YYYY-MM-DD), blank = no lower bound")
    date_to = _prompt("End date   (YYYY-MM-DD), blank = no upper bound")
    return (date_from or None), (date_to or None)


# ═══════════════════════════════════════════════════════════════════
# Export format picker
# ═══════════════════════════════════════════════════════════════════

def _pick_export_format() -> dict:
    """Let the user choose what kind of CSV(s) to generate."""
    print(f"\n{_BOLD}Export format:{_RESET}")
    print(f"  1) {_GREEN}Detailed shapelet CSV{_RESET}  — one row per shapelet (includes lat/lon for XY Table to Point)")
    print(f"  2) {_GREEN}Site summary CSV{_RESET}       — one row per site with aggregate statistics")
    print(f"  3) {_GREEN}Both{_RESET}                   — generate both files")
    raw = _prompt("Choose [1/2/3]", "3")
    return {
        "detailed": raw in ("1", "3"),
        "summary": raw in ("2", "3"),
    }


def _pick_value_expansion(length_days_max: int | None = None) -> bool:
    """Ask whether to expand the shapelet JSON array into Day_N columns."""
    hint = ""
    if length_days_max:
        hint = f" (max window = {length_days_max} days)"
    return _prompt_yes_no(
        f"Expand shapelet values into individual Day_N columns?{hint}",
        default=False,
    )


# ═══════════════════════════════════════════════════════════════════
# Database summary
# ═══════════════════════════════════════════════════════════════════

def print_db_overview(conn: sqlite3.Connection) -> None:
    """Print a compact overview of what the database contains."""
    total = get_row_count(conn)
    years = get_available_years(conn)
    sites = get_available_sites(conn)
    pollutants = get_available_pollutants(conn)
    min_d, max_d = get_date_range(conn)

    print(f"\n{'═' * 60}")
    print(f"  {_BOLD}DATABASE OVERVIEW{_RESET}")
    print(f"{'═' * 60}")
    print(f"  Total shapelets : {total:,}")
    print(f"  Years           : {years[0]}–{years[-1]}  ({len(years)} distinct)" if years else "  Years: none")
    print(f"  Sites           : {len(sites)}")
    print(f"  Pollutants      : {len(pollutants)}")
    print(f"  Date span       : {min_d}  →  {max_d}")
    print(f"{'═' * 60}")


# ═══════════════════════════════════════════════════════════════════
# Main interactive flow
# ═══════════════════════════════════════════════════════════════════

def interactive_export(conn: sqlite3.Connection, out_dir: Path, expand_cli: bool) -> None:
    """Walk the user through filter selection and write CSVs."""

    print_db_overview(conn)

    # 1) Years
    years = _pick_years(get_available_years(conn))

    # 2) Pollutants
    pollutants_raw = get_available_pollutants(conn)
    pollutant_items = [
        {
            "display": f"{p['parameter_code']}"
                       + (f"  ({p['name']})" if p["name"] != p["parameter_code"] else ""),
            "value": p["parameter_code"],
        }
        for p in pollutants_raw
    ]
    pollutants = _pick_many("Pollutants (parameter codes):", pollutant_items, "display", "value")

    # 3) Sites
    site_items = [
        {"display": f"{s['site_key']}  (lat {s['latitude']}, lon {s['longitude']})",
         "value": s["site_key"]}
        for s in get_available_sites(conn)
    ]
    sites = None
    if len(site_items) <= 80:
        sites = _pick_many("Monitoring sites:", site_items, "display", "value")
    else:
        print(f"\n{_BOLD}{len(site_items)} sites available.{_RESET}")
        if _prompt_yes_no("Filter by specific sites? (lists all)", default=False):
            sites = _pick_many("Monitoring sites:", site_items, "display", "value")

    # 4) Pattern types
    ptypes = get_available_pattern_types(conn)
    ptype_items = [{"display": pt, "value": pt} for pt in ptypes]
    pattern_types = _pick_many("Pattern types:", ptype_items, "display", "value") if ptype_items else None

    # 5) Date range
    min_d, max_d = get_date_range(conn)
    date_from, date_to = _pick_date_range(min_d, max_d)

    # 6) Export format
    fmt = _pick_export_format()

    # 7) Expand shapelet values?
    expand = expand_cli
    if fmt["detailed"] and not expand_cli:
        expand = _pick_value_expansion()

    # ── Preview row count before writing ──
    sql, params = build_export_query(
        years=years, sites=sites, pollutants=pollutants,
        pattern_types=pattern_types, date_from=date_from, date_to=date_to,
    )
    preview_count = conn.execute(
        f"SELECT COUNT(*) FROM ({sql})", params
    ).fetchone()[0]

    print(f"\n{_hr('─')}")
    print(f"  Matched rows: {_BOLD}{preview_count:,}{_RESET}")

    if preview_count == 0:
        print("  Nothing to export — try broader filters.")
        return

    if not _prompt_yes_no("Proceed with export?"):
        print("  Cancelled.")
        return

    # ── Build a descriptive filename tag ──
    tag_parts: list[str] = []
    if years:
        tag_parts.append(f"y{'_'.join(map(str, years))}")
    if pollutants:
        tag_parts.append(f"p{'_'.join(pollutants)}")
    if sites:
        tag_parts.append(f"s{len(sites)}sites")
    if date_from or date_to:
        tag_parts.append("datefilter")
    tag = "_".join(tag_parts) if tag_parts else "all"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ── Write CSVs ──
    written_files: list[tuple[str, int, Path]] = []

    if fmt["detailed"]:
        # Determine max_expand from the data if expanding
        max_expand = 31
        if expand:
            row = conn.execute(
                "SELECT MAX(length_days) FROM shapelets"
            ).fetchone()
            if row and row[0]:
                max_expand = row[0]

        fname = f"shapelets_{tag}_{timestamp}.csv"
        fpath = out_dir / fname
        n = write_csv(conn, sql, params, fpath, expand_values=expand, max_expand=max_expand)
        written_files.append(("Detailed shapelet CSV", n, fpath))

    if fmt["summary"]:
        fname = f"site_summary_{tag}_{timestamp}.csv"
        fpath = out_dir / fname
        n = write_site_summary_csv(conn, fpath, years=years, pollutants=pollutants)
        written_files.append(("Site summary CSV", n, fpath))

    # ── Report ──
    print(f"\n{'═' * 60}")
    print(f"  {_BOLD}{_GREEN}EXPORT COMPLETE{_RESET}")
    print(f"{'═' * 60}")
    for label, count, path in written_files:
        size_kb = path.stat().st_size / 1024
        print(f"  {label}")
        print(f"    Rows : {count:,}")
        print(f"    Size : {size_kb:,.1f} KB")
        print(f"    Path : {path}")
    print(f"{'═' * 60}")
    print()
    print(f"  {_BOLD}ArcGIS Pro import tips:{_RESET}")
    print("  • Encoding : UTF-8  (ArcGIS Pro default)")
    print("  • Dates    : ISO-8601 (YYYY-MM-DD)")
    if any("Detailed" in lbl for lbl, _, _ in written_files):
        print("  • Spatial  : Use 'XY Table to Point'")
        print("               with Latitude / Longitude")
        print("               CRS → GCS_WGS_1984")
    if any("summary" in lbl.lower() for lbl, _, _ in written_files):
        print("  • Summary  : One row per site")
    print()


# ═══════════════════════════════════════════════════════════════════
# Quick (non-interactive) export
# ═══════════════════════════════════════════════════════════════════

def quick_export(conn: sqlite3.Connection, out_dir: Path, expand: bool) -> None:
    """Export everything with sensible defaults — no prompts."""
    print_db_overview(conn)

    sql, params = build_export_query()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    max_expand = 31
    if expand:
        row = conn.execute("SELECT MAX(length_days) FROM shapelets").fetchone()
        if row and row[0]:
            max_expand = row[0]

    detail_path = out_dir / f"shapelets_all_{timestamp}.csv"
    n1 = write_csv(conn, sql, params, detail_path, expand_values=expand, max_expand=max_expand)

    summary_path = out_dir / f"site_summary_all_{timestamp}.csv"
    n2 = write_site_summary_csv(conn, summary_path)

    print(f"\n{_GREEN}Exported {n1:,} shapelet rows → {detail_path}{_RESET}")
    print(f"{_GREEN}Exported {n2:,} site rows     → {summary_path}{_RESET}\n")


# ═══════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════

def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    # Resolve database path
    db_path = args.db or (get_database_path() / "air.db")
    if not db_path.exists():
        print(f"Error: database not found at {db_path}", file=sys.stderr)
        print("Run the ingestion pipeline first:  python main.py", file=sys.stderr)
        sys.exit(1)

    # Resolve output directory
    try:
        out_dir = args.out_dir or get_arcgis_inputs_path()
    except SystemExit:
        # arcgis_inputs_path not configured — fall back to project exports/
        out_dir = _PROJECT_ROOT / "exports"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Connect
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys=ON;")

    try:
        if get_row_count(conn) == 0:
            print("Database is empty — nothing to export.")
            print("Run the ingestion pipeline first:  python main.py")
            sys.exit(0)

        if args.quick:
            quick_export(conn, out_dir, expand=args.expand_values)
        else:
            interactive_export(conn, out_dir, expand_cli=args.expand_values)
    except KeyboardInterrupt:
        print("\n\nExport cancelled.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
