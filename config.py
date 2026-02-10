# -*- coding: utf-8 -*-
"""
Configuration loader module.

Provides utilities to load and access project configuration from .config file.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def get_project_root() -> Path:
    """Get the project root directory."""
    # Assumes this file is in the project root
    return Path(__file__).parent


def get_config_path() -> Path:
    """Get the path to the configuration file."""
    return get_project_root() / ".config"


def load_config() -> dict[str, Any]:
    """
    Load configuration from .config file.
    
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If .config file doesn't exist
        json.JSONDecodeError: If .config file is invalid
    """
    config_path = get_config_path()
    
    if not config_path.exists():
        print(f"Error: Configuration file not found at {config_path}", file=sys.stderr)
        print("Please run: python scripts/setup_config.py", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid configuration file: {e}", file=sys.stderr)
        print("Please re-run: python scripts/setup_config.py", file=sys.stderr)
        sys.exit(1)


def get_database_path() -> Path:
    """
    Get the database path from configuration.
    
    Returns:
        Path object pointing to the database directory
    """
    config = load_config()
    db_path = config.get("database_path")
    
    if not db_path:
        print("Error: database_path not found in configuration", file=sys.stderr)
        sys.exit(1)
    
    path = Path(db_path)
    if not path.exists():
        print(f"Warning: Database path does not exist: {path}", file=sys.stderr)
    
    return path


def get_output_path() -> Path:
    """
    Get the output path from configuration.
    
    Returns:
        Path object pointing to the output directory
    """
    config = load_config()
    output_path = config.get("output_path", str(get_project_root()))
    return Path(output_path)


def get_config_value(key: str, default: Any = None) -> Any:
    """
    Get a specific configuration value.
    
    Args:
        key: Configuration key
        default: Default value if key not found
        
    Returns:
        Configuration value or default
    """
    config = load_config()
    return config.get(key, default)


# Example usage
if __name__ == "__main__":
    try:
        config = load_config()
        print("Current configuration:")
        print(json.dumps(config, indent=2))
        print()
        print(f"Database path: {get_database_path()}")
        print(f"Output path: {get_output_path()}")
    except SystemExit:
        pass
