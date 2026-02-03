# J_Allen_Air_Pollutant
Includes Air pollutant in NC from 2004-2024

## Environment setup
Use the setup script to create a local `.venv` and install dependencies from the requirements file.

- Script: [scripts/setup_venv.py](scripts/setup_venv.py)
- Requirements: [requirements.txt](requirements.txt)

If a `.venv` already exists but is incomplete, the setup script will recreate it and reinstall requirements.

To auto-activate the venv in VS Code PowerShell terminals, this repo includes:

- Activation script: [scripts/activate-venv.ps1](scripts/activate-venv.ps1)
- VS Code settings: [.vscode/settings.json](.vscode/settings.json)

The requirements include `pandas`, which supports importing common data formats and saving to a local `.pkl` file via Python's built-in `pickle` module.
