# Configuration System

This project uses a local `.config` file to store user-specific settings like database paths. This file is not tracked by git, so each user can have their own configuration.

## Quick Start

Run the setup script to configure your settings:
```bash
python scripts/setup_config.py
```

This will prompt you to:
1. Select your database folder (using a folder picker dialog)
2. Optionally configure output path
3. Set additional preferences (workers, logging, etc.)

## Configuration File

The configuration is stored as JSON in `.config` at the project root:

```json
{
  "database_path": "C:\\path\\to\\your\\database",
  "output_path": "C:\\path\\to\\output",
  "max_workers": 4,
  "verbose": false
}
```

See [.config.example](.config.example) for a template.

## Using Config in Your Code

Import the config module to access settings:

```python
from config import get_database_path, get_output_path, get_config_value

# Get paths
db_path = get_database_path()      # Returns Path object
output = get_output_path()         # Returns Path object

# Get other values
workers = get_config_value("max_workers", default=4)
verbose = get_config_value("verbose", default=False)
```

## Viewing Current Config

To see your current configuration:
```bash
python config.py
```

## Updating Configuration

Re-run the setup script anytime to update your settings:
```bash
python scripts/setup_config.py
```

The script will show your current settings and ask if you want to update them.

## Important Notes

- The `.config` file is **gitignored** - it will not be committed to the repository
- Each developer/user needs to run `setup_config.py` once to create their own `.config`
- If you see errors about missing configuration, run `setup_config.py`
- Never commit your `.config` file - it may contain local paths specific to your machine
