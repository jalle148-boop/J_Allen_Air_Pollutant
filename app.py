# -*- coding: utf-8 -*-
"""
Streamlit web app for interactive ArcGIS CSV export.

Launch:
    streamlit run app.py
    streamlit run app.py -- --db path/to/air.db
"""

from __future__ import annotations

import io
import sqlite3
import sys
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import streamlit as st

# Project imports
from config import get_database_path, get_arcgis_inputs_path
from helpers.exporter import (
    build_export_query,
    get_available_pollutants,
    get_available_sites,
    get_available_years,
    get_available_pattern_types,
    get_date_range,
    get_row_count,
    query_to_dataframe,
    site_summary_dataframe,
    write_csv,
    write_site_summary_csv,
)

# ─────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────

st.set_page_config(
    page_title="ArcGIS CSV Exporter",
    page_icon="🗺️",
    layout="wide",
)


# ─────────────────────────────────────────────────────────
# Database connection (cached across reruns)
# ─────────────────────────────────────────────────────────

@st.cache_resource
def get_connection(db_path: str) -> sqlite3.Connection:
    """Open a read-only SQLite connection (cached for the session)."""
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def resolve_db_path() -> Path:
    """Resolve the database path from CLI args or config."""
    # Allow override via:  streamlit run app.py -- --db path/to/air.db
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--db" and i + 1 < len(args):
            return Path(args[i + 1])
    return get_database_path() / "air.db"


# ─────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────

def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Convert a DataFrame to UTF-8 CSV bytes for download."""
    buf = io.BytesIO()
    df.to_csv(buf, index=False, encoding="utf-8")
    return buf.getvalue()


# ─────────────────────────────────────────────────────────
# Main app
# ─────────────────────────────────────────────────────────

def main() -> None:
    st.title("🗺️ ArcGIS CSV Exporter")
    st.caption("Interactively filter the shapelet database and export ArcGIS-ready CSVs")

    # --- Connect ---
    db_path = resolve_db_path()
    if not db_path.exists():
        st.error(
            f"Database not found at `{db_path}`.\n\n"
            "Run the ingestion pipeline first: `python main.py`"
        )
        return

    conn = get_connection(str(db_path))

    total = get_row_count(conn)
    if total == 0:
        st.warning("Database is empty — run `python main.py` first.")
        return

    # ═══════════════════════════════════════════════════════
    # Sidebar – Database overview & filters
    # ═══════════════════════════════════════════════════════

    with st.sidebar:
        st.header("Database Overview")
        years = get_available_years(conn)
        sites = get_available_sites(conn)
        pollutants = get_available_pollutants(conn)
        pattern_types = get_available_pattern_types(conn)
        min_d, max_d = get_date_range(conn)

        col1, col2 = st.columns(2)
        col1.metric("Total Shapelets", f"{total:,}")
        col2.metric("Sites", len(sites))
        col1.metric("Pollutants", len(pollutants))
        col2.metric(
            "Years",
            f"{years[0]}–{years[-1]}" if years else "—",
        )
        st.caption(f"Date span: {min_d} → {max_d}")

        st.divider()
        st.header("Filters")

        # ── Years ──
        sel_years = st.multiselect(
            "Years",
            options=years,
            default=None,
            help="Leave empty for all years",
        )

        # ── Pollutants ──
        poll_options = {
            f"{p['parameter_code']}"
            + (f" ({p['name']})" if p["name"] != p["parameter_code"] else ""): p["parameter_code"]
            for p in pollutants
        }
        sel_poll_labels = st.multiselect(
            "Pollutants",
            options=list(poll_options.keys()),
            default=None,
            help="Leave empty for all pollutants",
        )
        sel_pollutants = [poll_options[l] for l in sel_poll_labels]

        # ── Sites ──
        site_options = {
            s["site_key"]: s["site_key"]
            for s in sites
        }
        sel_sites = st.multiselect(
            "Sites",
            options=list(site_options.keys()),
            default=None,
            help="Leave empty for all sites",
        )

        # ── Pattern types ──
        sel_ptypes = st.multiselect(
            "Pattern Types",
            options=pattern_types,
            default=None,
            help="Leave empty for all pattern types",
        )

        # ── Date range ──
        st.subheader("Date Range")
        use_date_filter = st.checkbox("Filter by date range")
        date_from = None
        date_to = None
        if use_date_filter:
            min_date = date.fromisoformat(min_d) if min_d else date(2000, 1, 1)
            max_date = date.fromisoformat(max_d) if max_d else date(2030, 12, 31)
            d_range = st.date_input(
                "Date range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
            )
            if isinstance(d_range, (list, tuple)) and len(d_range) == 2:
                date_from = d_range[0].isoformat()
                date_to = d_range[1].isoformat()

        st.divider()

        # ── Export options ──
        st.header("Export Options")
        expand_values = st.checkbox(
            "Expand shapelet values to Day_N columns",
            value=False,
            help="Spreads the JSON array into individual columns",
        )

    # ═══════════════════════════════════════════════════════
    # Build query & preview
    # ═══════════════════════════════════════════════════════

    sql, params = build_export_query(
        years=sel_years or None,
        sites=sel_sites or None,
        pollutants=sel_pollutants or None,
        pattern_types=sel_ptypes or None,
        date_from=date_from,
        date_to=date_to,
    )

    # Count matched rows
    count_sql = f"SELECT COUNT(*) FROM ({sql})"
    matched = conn.execute(count_sql, params).fetchone()[0]

    st.subheader(f"Matched Rows: {matched:,}")

    if matched == 0:
        st.info("No rows match your filters. Adjust the sidebar and try again.")
        return

    # ── Shapelet data preview ──
    tab_detail, tab_summary, tab_export = st.tabs([
        "📋 Detailed Preview",
        "📊 Site Summary",
        "💾 Export",
    ])

    # ── Tab 1: Detailed preview ──
    with tab_detail:
        preview_limit = st.slider(
            "Preview rows", min_value=5, max_value=min(500, matched),
            value=min(50, matched), step=5,
        )
        preview_sql = sql + f" LIMIT {preview_limit}"
        df_preview = query_to_dataframe(conn, preview_sql, params)
        st.dataframe(df_preview, width="stretch", hide_index=True)

        # Quick stats
        if "Quality" in df_preview.columns:
            c1, c2, c3 = st.columns(3)
            c1.metric("Avg Quality", f"{df_preview['Quality'].mean():.4f}")
            c2.metric("Min Quality", f"{df_preview['Quality'].min():.4f}")
            c3.metric("Max Quality", f"{df_preview['Quality'].max():.4f}")

    # ── Tab 2: Site summary ──
    with tab_summary:
        df_sites = site_summary_dataframe(
            conn,
            years=sel_years or None,
            pollutants=sel_pollutants or None,
        )
        if df_sites.empty:
            st.info("No site data for current filters.")
        else:
            st.dataframe(df_sites, width="stretch", hide_index=True)
            st.caption(f"{len(df_sites)} site(s)")

            # Map if lat/lon available
            map_df = df_sites[["Latitude", "Longitude"]].dropna()
            if not map_df.empty:
                map_df = map_df.rename(columns={
                    "Latitude": "lat", "Longitude": "lon",
                })
                st.map(map_df)

    # ── Tab 3: Export ──
    with tab_export:
        st.markdown("### Download CSVs")
        st.markdown(
            "Files are UTF-8 encoded with ISO-8601 dates — "
            "ready for **ArcGIS Pro** → *Add Data* → *XY Table to Point*."
        )

        col_d, col_s = st.columns(2)

        # -- Detailed CSV download --
        with col_d:
            st.markdown("**Detailed Shapelet CSV**")
            st.caption(f"{matched:,} rows, one per shapelet")
            if st.button("Prepare detailed CSV", key="prep_detail"):
                with st.spinner("Querying…"):
                    df_full = query_to_dataframe(conn, sql, params)

                    if expand_values:
                        max_len = (
                            df_full["LengthDays"].max()
                            if "LengthDays" in df_full.columns
                            else 31
                        )
                        max_len = int(max_len) if pd.notna(max_len) else 31

                        import json as _json
                        expanded_rows = []
                        for vals_json in df_full["ShapeletValues"]:
                            vals = _json.loads(vals_json) if vals_json else []
                            padded = (vals + [None] * max_len)[:max_len]
                            expanded_rows.append(padded)
                        day_cols = [f"Day_{i+1}" for i in range(max_len)]
                        df_days = pd.DataFrame(expanded_rows, columns=day_cols)
                        df_full = pd.concat([
                            df_full.drop(columns=["ShapeletValues"]),
                            df_days,
                        ], axis=1)

                csv_bytes = df_to_csv_bytes(df_full)
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                st.download_button(
                    "⬇️ Download detailed CSV",
                    data=csv_bytes,
                    file_name=f"shapelets_{ts}.csv",
                    mime="text/csv",
                )

        # -- Site summary CSV download --
        with col_s:
            st.markdown("**Site Summary CSV**")
            site_count = len(df_sites) if not df_sites.empty else 0
            st.caption(f"{site_count} site(s), aggregated stats")
            if not df_sites.empty:
                csv_sites = df_to_csv_bytes(df_sites)
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                st.download_button(
                    "⬇️ Download site summary CSV",
                    data=csv_sites,
                    file_name=f"site_summary_{ts}.csv",
                    mime="text/csv",
                )

        st.divider()

        # -- Save to disk --
        st.markdown("### Save to ArcGIS inputs folder")
        try:
            default_dir = str(get_arcgis_inputs_path())
        except SystemExit:
            default_dir = str(Path(__file__).parent / "exports")

        out_dir = st.text_input("Output directory", value=default_dir)

        if st.button("💾 Save CSVs to disk", type="primary"):
            out_path = Path(out_dir)
            out_path.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")

            max_expand = 31
            if expand_values:
                row = conn.execute(
                    "SELECT MAX(length_days) FROM shapelets"
                ).fetchone()
                if row and row[0]:
                    max_expand = row[0]

            detail_path = out_path / f"shapelets_{ts}.csv"
            n1 = write_csv(
                conn, sql, params, detail_path,
                expand_values=expand_values,
                max_expand=max_expand,
            )

            summary_path = out_path / f"site_summary_{ts}.csv"
            n2 = write_site_summary_csv(
                conn, summary_path,
                years=sel_years or None,
                pollutants=sel_pollutants or None,
            )

            st.success(
                f"Saved {n1:,} shapelet rows → `{detail_path}`\n\n"
                f"Saved {n2} site rows → `{summary_path}`"
            )

    # ═══════════════════════════════════════════════════════
    # Footer
    # ═══════════════════════════════════════════════════════
    st.divider()
    st.caption(
        "**ArcGIS Pro import tips:** "
        "Use *XY Table to Point* with Latitude/Longitude columns "
        "(GCS WGS 1984). Dates are ISO-8601. Encoding is UTF-8."
    )


if __name__ == "__main__":
    main()
