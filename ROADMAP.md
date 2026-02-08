# ROADMAP

# To-do Items

- Document the structure of the data
- Create a target plan for the structure of our database


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

# Workflow Scaffold (helpers.py + main.py)

Goal: turn raw zipped pickle datasets into a clean, queryable database with clear metadata.

1) Inventory + data dictionary
- Identify all data files, file naming patterns, and what each token means.
- Map field names, units, and expected ranges.
- Define pollutant list and any lookup tables (e.g., site, state, county).

2) Ingestion scaffolding (helpers.py)
- `load_single_pkl(path)`: load one pickle safely and return a python object.
- `load_zipped_pkl(path)`: open .zip, extract pickle bytes, return object.
- `parse_dataset_name(name)`: split filename into metadata fields.
- `iter_records(obj)`: normalize nested structure into record dicts.
- `validate_record(record)`: basic schema + type checks.

3) Orchestration (main.py)
- Discover input files (directory scan, extension filters).
- For each file:
	- Parse filename into metadata.
	- Load dataset with helpers.
	- Flatten to rows with `iter_records`.
	- Validate and collect errors.
	- Write output to database.

4) Database target plan
- Tables:
	- `pollutants` (id, code, name, unit)
	- `sites` (id, state, county, site_code, lat, lon)
	- `observations` (id, pollutant_id, site_id, date, value, zscore)
	- `ingestion_runs` (id, source_file, loaded_at, status, error_count)
- Indexes on (`pollutant_id`, `site_id`, `date`).

5) Logging + reproducibility
- Log per file: counts, min/max dates, invalid rows.
- Write a small summary report (csv or markdown).
- Pin requirements in requirements.txt.

6) Testing and validation
- Unit tests for helpers: load, parse, flatten.
- Sanity checks: row counts vs expected weeks, missing dates.
- Manual spot check: one known file end-to-end.


---

# Step-by-step path

This section is the day-to-day workflow for the project.

Step 0: Confirm inputs
- Decide where raw data lives (folder path).
- List file types you expect: .pkl, .zip (with .pkl inside).
- Pick a small sample file for quick testing.

Step 1: Add the data dictionary
- Update this ROADMAP with what each filename token means.
- Create a short list of fields and units (from inside the pickle).
- Identify the time granularity (daily vs weekly) and how dates are stored.

Step 2: Implement helpers in small, testable pieces
- Build one function at a time in helpers.py.
- After each function, test it in a Python REPL or small script.

Step 3: Write the orchestration skeleton
- The goal is a single command that loads many files and writes to a database.
- Start with a dry-run mode that only prints counts and sample rows.

Step 4: Add the database writer
- Start with SQLite for simplicity (one local file).
- Write rows in batches (e.g., 500-1000 rows per insert).

Step 5: Validate
- Compare expected vs actual row counts.
- Check one known site/pollutant for a date range and confirm values.

Step 6: Document and hand off
- Update README or this ROADMAP with how to run the pipeline.


---

# Orchestration skeletons (for main.py)

## Suggested CLI flow

Example command (goal):

```bash
python main.py --input-dir data/raw --db data/air.db --dry-run
```

## Pseudocode outline

```python
def main():
	args = parse_args()
	files = discover_input_files(args.input_dir)

	run_id = start_ingestion_run(args.db, files)

	for path in files:
		meta = parse_dataset_name(path.name)
		obj = load_dataset(path)
		records = iter_records(obj, meta)

		valid_rows = []
		error_rows = []
		for rec in records:
			ok, err = validate_record(rec)
			if ok:
				valid_rows.append(rec)
			else:
				error_rows.append(err)

		if args.dry_run:
			print_summary(path, meta, valid_rows, error_rows)
		else:
			write_to_db(args.db, valid_rows, run_id, path)

		log_file_result(args.db, run_id, path, valid_rows, error_rows)

	finish_ingestion_run(args.db, run_id)
```

## Minimal CLI flags to support
- `--input-dir` path to raw files
- `--db` path to sqlite database file
- `--dry-run` do not write, just report counts
- `--limit` optional file count limit for fast tests


---

# Helpers scaffolding (for helpers.py)

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

