# ROADMAP

# To-do Items

- ~~Document the structure of the data~~ ✅ (see `data_structure_notes.md` and Data Dictionary below)
- ~~Create a target plan for the structure of our database~~ ✅ (see Database Schema below)
- Configure imports for ArcGIS Pro 3.5


# Brainstorming for database: 
- Top level: pollutants



Notes:

Data structure:

level 1:
key = North Carolina_Beaufort_6_daily_42401_7d_2004_daily_zscore
value = list

level 2:
bunch of dictionaries, one per week (total range of a year? 50 weeks?)

level 3 (in each mini dictionary)


---

# Data Dictionary

## Filename tokens

Example: `North Carolina_Beaufort_6_shapelets.pkl_2004_000.pkl`

| Token | Meaning | Example |
|---|---|---|
| State | US state name | `North Carolina` |
| County | County name | `Beaufort` |
| Site num | EPA monitoring site number | `6` |
| (literal) | Fixed label | `shapelets.pkl` |
| Year | Calendar year | `2004` |
| Chunk | File chunk index (zero-padded) | `000` |

## Dataset key tokens (inside the pickle)

Example: `North Carolina_Beaufort_6_daily_42401_7d_2004_daily_zscore`

| Token | Meaning | Example |
|---|---|---|
| State | US state name | `North Carolina` |
| County | County name | `Beaufort` |
| Site num | EPA monitoring site number | `6` |
| Frequency | Sampling frequency | `daily` |
| Parameter code | EPA AQS parameter code | `42401` (SO₂) |
| Duration | Shapelet window length | `7d` |
| Year | Calendar year | `2004` |
| Agg method | Aggregation / normalization | `daily_zscore` |

## Shapelet record fields (15 keys per dict)

| Field | Type | Description |
|---|---|---|
| `shapelet` | ndarray | Shapelet values (length = `length_days`) |
| `length_days` | int | Window size in days (e.g. 7) |
| `quality` | float64 | Shapelet quality score |
| `start_date` | datetime.date | Start of the window |
| `end_date` | datetime.date | End of the window |
| `location` | str | `"{State}_{County}_{SiteNum}"` |
| `year` | int | Calendar year |
| `shapelet_id` | int | Index within the file (0–49) |
| `pattern_type` | str | e.g. `"daily_42401"` |
| `data_type` | str | e.g. `"daily_site_zscore"` |
| `latitude` | float64 | Site latitude |
| `longitude` | float64 | Site longitude |
| `state` | str | US state name |
| `county` | str | County name |
| `site_num` | int64 | EPA monitoring site number |


---

# Workflow Scaffold (helpers.py + main.py)

Goal: turn raw zipped pickle datasets into a clean, queryable database with clear metadata.

1) Inventory + data dictionary
- ~~Identify all data files, file naming patterns, and what each token means.~~ ✅
- ~~Map field names, units, and expected ranges.~~ ✅
- ~~Define pollutant list and any lookup tables (e.g., site, state, county).~~ ✅

2) Ingestion scaffolding (helpers/)
- ~~`load_single_pkl(path)`: load one pickle safely and return a python object.~~ ✅ `helpers/loader.py`
- ~~`load_zipped_pkl(path)`: open .zip, extract pickle bytes, return object.~~ ✅ `helpers/loader.py`
- ~~`parse_dataset_name(name)`: split filename into metadata fields.~~ ✅ `helpers/parser.py`
- ~~`iter_records(obj)`: normalize nested structure into record dicts.~~ ✅ `helpers/records.py`
- ~~`validate_record(record)`: basic schema + type checks.~~ ✅ `helpers/validator.py`

3) Orchestration (main.py)
- ~~Discover input files (directory scan, extension filters).~~ ✅
- ~~For each file:~~ ✅
	- ~~Parse filename into metadata.~~
	- ~~Load dataset with helpers.~~
	- ~~Flatten to rows with `iter_records`.~~
	- ~~Validate and collect errors.~~
	- ~~Write output to database.~~

4) Database target plan
- ~~Tables:~~ ✅ Implemented in `helpers/db.py`
	- ~~`pollutants` (parameter_code, name, unit)~~
	- ~~`sites` (site_key, state, county, site_num, latitude, longitude)~~
	- ~~`shapelets` (id, dataset_key, shapelet_id, site_key, parameter_code, year, dates, quality, values, ...)~~
	- ~~`ingestion_runs` (id, started_at, finished_at, status, total_files, total_rows, error_count)~~
- ~~Indexes on (site_key), (year), (start_date, end_date).~~ ✅

5) Logging + reproducibility
- ~~Log per file: counts, min/max dates, invalid rows.~~ ✅ (via `--verbose` flag)
- Write a small summary report (csv or markdown).
- ~~Pin requirements in requirements.txt.~~ ✅

6) Testing and validation
- Unit tests for helpers: load, parse, flatten.
- Sanity checks: row counts vs expected weeks, missing dates.
- ~~Manual spot check: one known file end-to-end.~~ ✅ (3 files, 150 records, 0 errors)


---

# Database Schema

```
┌──────────────┐       ┌──────────────────────────────────────────┐
│  pollutants  │       │              shapelets                   │
├──────────────┤       ├──────────────────────────────────────────┤
│ parameter_code (PK)◄─┤ parameter_code (FK)                     │
│ name         │       │ id (PK, auto)                            │
│ unit         │       │ dataset_key                              │
└──────────────┘       │ shapelet_id                              │
                       │ site_key (FK) ──────►┌───────────────┐   │
┌──────────────────┐   │ year                 │    sites       │   │
│ ingestion_runs   │   │ start_date           ├───────────────┤   │
├──────────────────┤   │ end_date             │ site_key (PK) │   │
│ id (PK, auto)    │   │ length_days          │ state         │   │
│ started_at       │   │ pattern_type         │ county        │   │
│ finished_at      │   │ data_type            │ site_num      │   │
│ status           │   │ quality              │ latitude      │   │
│ total_files      │   │ shapelet_values (JSON)│ longitude     │   │
│ total_rows       │   │ source_file          └───────────────┘   │
│ error_count      │   └──────────────────────────────────────────┘
└──────────────────┘
```


---

# Step-by-step path

This section is the day-to-day workflow for the project.

Step 0: Confirm inputs ✅
- ~~Decide where raw data lives (folder path).~~ → `.config` file with `data_path`
- ~~List file types you expect: .pkl, .zip (with .pkl inside).~~ → `.pkl` files confirmed
- ~~Pick a small sample file for quick testing.~~ → 3 sample files available

Step 1: Add the data dictionary ✅
- ~~Update this ROADMAP with what each filename token means.~~ → see Data Dictionary above
- ~~Create a short list of fields and units (from inside the pickle).~~ → see `data_structure_notes.md`
- ~~Identify the time granularity (daily vs weekly) and how dates are stored.~~ → daily, `datetime.date`

Step 2: Implement helpers in small, testable pieces ✅
- ~~Build one function at a time in helpers.py.~~ → reorganized into `helpers/` package
- ~~After each function, test it in a Python REPL or small script.~~ → tested end-to-end

Step 3: Write the orchestration skeleton ✅
- ~~The goal is a single command that loads many files and writes to a database.~~
- ~~Start with a dry-run mode that only prints counts and sample rows.~~

Step 4: Add the database writer ✅
- ~~Start with SQLite for simplicity (one local file).~~ → `air.db`
- ~~Write rows in batches (e.g., 500-1000 rows per insert).~~ → 500-row batch default

Step 5: Validate ✅ (initial pass)
- ~~Compare expected vs actual row counts.~~ → 3 files × 50 shapelets = 150 rows ✓
- ~~Check one known site/pollutant for a date range and confirm values.~~ → Beaufort site confirmed
- Unit tests still needed for ongoing CI.

Step 6: Document and hand off (in progress)
- ~~Update README or this ROADMAP with how to run the pipeline.~~ → see below


---

# How to run the pipeline

```bash
# Dry run — parse and validate, no DB writes
python main.py --dry-run --verbose

# Full ingestion using paths from .config
python main.py --verbose

# Override paths manually
python main.py --input-dir path/to/data --db path/to/air.db

# Limit files for quick testing
python main.py --limit 2 --dry-run
```

## CLI flags

| Flag | Description |
|---|---|
| `--input-dir PATH` | Directory with .pkl / .zip files (default: `data_path` from `.config`) |
| `--db PATH` | SQLite database file (default: `<database_path>/air.db`) |
| `--dry-run` | Parse & validate only, do not write to DB |
| `--limit N` | Process at most N files |
| `--verbose`, `-v` | Print detailed per-file output |


---

# Project structure

```
J_Allen_Air_Pollutant/
├── .config                  # Local paths (not committed)
├── config.py                # Config loader
├── main.py                  # CLI pipeline entry point
├── helpers/
│   ├── __init__.py          # Package re-exports
│   ├── loader.py            # Pickle / zip loading, file discovery
│   ├── parser.py            # Filename & dataset-key parsing
│   ├── records.py           # Flatten nested data → record dicts
│   ├── validator.py         # Schema & domain validation
│   └── db.py                # SQLite schema, writes, audit log
├── scripts/
│   ├── activate-venv.ps1
│   ├── inspect_pkl_structure.py
│   ├── setup_config.py
│   └── setup_venv.py
├── requirements.txt
├── data_structure_notes.md
├── ROADMAP.md               # ← you are here
└── README.md
```


---

# Helpers scaffolding (for helpers.py)

> **Note:** This section is kept for historical reference. The actual implementations
> are in `helpers/loader.py`, `helpers/parser.py`, `helpers/records.py`, and
> `helpers/validator.py`.

## Function targets and behavior

```python
def load_single_pkl(file_path):
	"""Return object from pickle at path."""

def load_zipped_pkl(zip_path):
	"""Return object from pickle inside a zip file."""

def parse_dataset_name(name):
	"""Parse filename tokens into metadata dict."""

def iter_records(obj, meta):
	"""Yield normalized record dicts from nested data."""

def validate_record(record):
	"""Return (ok, err). err is a string or dict."""
```

## Iteration pattern for nested data
- Level 1: dict key is dataset name
- Level 2: list of weekly dicts
- Level 3: each dict contains date/value pairs (confirm exact structure)

## Example record shape

```python
{
	"pollutant_code": "42401",
	"state": "North Carolina",
	"county": "Beaufort",
	"site_code": "6",
	"date": "2004-01-01",
	"value": 12.3,
	"zscore": -0.42,
}
```


---

# Notes and tips

- Work on one function at a time. Keep changes small.
- Use print statements or quick scripts to inspect data shapes.
- Commit early and often when a step works.
- If stuck, write down the exact error message and what file triggered it.

# Configure imports for ArcGIS

- The data need to be processed for input into ArcGIS Pro 3.5. The import structure is as follows: