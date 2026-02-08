# Getting Started

## Prerequisites
- Python installed and available on PATH.
- PowerShell on Windows (for auto-activating the venv).

## Setup Steps
1) Create or repair the local virtual environment and install dependencies:
   Run the setup script in [scripts/setup_venv.py](scripts/setup_venv.py).

2) If PowerShell says “running scripts is disabled,” update the execution policy:
   - Check policies: Get-ExecutionPolicy -List
   - Allow scripts for current user: Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
   - Temporary for current session: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

3) Open a new PowerShell terminal in VS Code to auto-activate the venv.
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