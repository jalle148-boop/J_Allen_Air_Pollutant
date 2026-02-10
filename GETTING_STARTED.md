# Getting Started

## Prerequisites
- Python installed and available on PATH.
- PowerShell on Windows (for auto-activating the venv).

## Setup Steps
1) Create or repair the local virtual environment and install dependencies:
   Run the setup script in [scripts/setup_venv.py](scripts/setup_venv.py).

2) **Configure project settings** by running the configuration setup:
   ```bash
   python scripts/setup_config.py
   ```
   This will prompt you to:
   - Select your database folder (where your data files are stored)
   - Optionally configure output path and other settings
   - Settings are saved to `.config` (not tracked by git)

3) If PowerShell says "running scripts is disabled," update the execution policy:
   - Check policies: Get-ExecutionPolicy -List
   - Allow scripts for current user: Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
   - Temporary for current session: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

4) Open a new PowerShell terminal in VS Code to auto-activate the venv.
   The activation script is [scripts/activate-venv.ps1](scripts/activate-venv.ps1) and the VS Code settings are in [.vscode/settings.json](.vscode/settings.json).

## Notes
- The requirements include `pandas`, which supports importing common data formats and saving to a local `.pkl` file via Python’s built-in `pickle` module.

## Inspect Pickle Structure
Use the structure inspector to understand nested data shapes before coding helpers.

Example (direct .pkl):
```bash
python scripts/inspect_pkl_structure.py --input data\raw\sample.pkl
```

Example (zip with a single .pkl):
```bash
python scripts/inspect_pkl_structure.py --input data\raw\sample.zip
```

Example (zip with multiple .pkl files):
```bash
python scripts/inspect_pkl_structure.py --input data\raw\sample.zip --zip-member path\inside\archive.pkl
```

Alternatively, run without `--input` to open an interactive file picker:
```bash
python scripts/inspect_pkl_structure.py
```

## Using Configuration in Your Scripts
The configuration system stores your database path and other settings. Use the `config.py` module to access these settings:

```python
from config import get_database_path, get_output_path, get_config_value

# Get database folder path
db_path = get_database_path()

# Get output folder path
output_path = get_output_path()

# Get specific config values
max_workers = get_config_value("max_workers", default=4)
verbose = get_config_value("verbose", default=False)
```

To view your current configuration:
```bash
python config.py
```

To update your configuration, re-run:
```bash
python scripts/setup_config.py
```