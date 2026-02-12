# -*- coding: utf-8 -*-
"""
Configuration setup script for J_Allen_Air_Pollutant project.

This script prompts the user to configure project settings and stores them
in a local .config file (untracked by git).

Usage:
    python scripts/setup_config.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from tkinter import Tk, filedialog


def prompt_for_folder(title: str, initial_dir: str | None = None) -> str | None:
    """Open a folder selection dialog."""
    root = Tk()
    root.withdraw()  # Hide the main window
    root.attributes("-topmost", True)  # Bring dialog to front
    
    folder_path = filedialog.askdirectory(
        title=title,
        initialdir=initial_dir
    )
    root.destroy()
    return folder_path if folder_path else None


def prompt_for_text(prompt: str, default: str = "") -> str:
    """Prompt for text input via console."""
    user_input = input(f"{prompt} [{default}]: ").strip()
    return user_input if user_input else default


def load_existing_config(config_path: Path) -> dict:
    """Load existing configuration if it exists."""
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load existing config: {e}")
            return {}
    return {}


def save_config(config: dict, config_path: Path) -> None:
    """Save configuration to file."""
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        print(f"\n✓ Configuration saved to: {config_path}")
    except IOError as e:
        print(f"Error: Could not save configuration: {e}", file=sys.stderr)
        sys.exit(1)


def setup_configuration() -> dict:
    """Interactive configuration setup."""
    print("=" * 60)
    print("J_Allen_Air_Pollutant - Configuration Setup")
    print("=" * 60)
    print()
    
    # Get project root (parent of scripts directory)
    project_root = Path(__file__).parent.parent
    config_path = project_root / ".config"
    
    # Load existing config if available
    existing_config = load_existing_config(config_path)
    
    if existing_config:
        print("Found existing configuration:")
        for key, value in existing_config.items():
            print(f"  {key}: {value}")
        print()
        update = prompt_for_text("Update configuration? (y/n)", "n").lower()
        if update not in ("y", "yes"):
            print("Configuration unchanged.")
            return existing_config
        print()
    
    config = {}
    
    # Data path (required) — raw .pkl / .zip files
    print("Step 1: Data Path (raw pickle files)")
    print("-" * 60)
    print("Select the folder containing your raw .pkl / .zip data files.")
    existing_data_path = existing_config.get("data_path", "")
    initial_dir = existing_data_path if existing_data_path else None
    
    data_path = prompt_for_folder(
        "Select Data Folder",
        initial_dir=initial_dir
    )
    
    if not data_path:
        print("Error: Data path is required.", file=sys.stderr)
        sys.exit(1)
    
    config["data_path"] = data_path
    print(f"✓ Data path set to: {data_path}")
    print()
    
    # Database path (required) — SQLite output
    print("Step 2: Database Path (SQLite output)")
    print("-" * 60)
    print("Select the folder where the SQLite database will be stored.")
    existing_db_path = existing_config.get("database_path", "")
    
    db_path = prompt_for_folder(
        "Select Database Folder",
        initial_dir=existing_db_path if existing_db_path else str(project_root)
    )
    
    if not db_path:
        print("Error: Database path is required.", file=sys.stderr)
        sys.exit(1)
    
    config["database_path"] = db_path
    print(f"✓ Database path set to: {db_path}")
    print()
    
    # ArcGIS inputs path (optional)
    print("Step 3: ArcGIS Inputs Path (optional)")
    print("-" * 60)
    print("Select the folder for CSV exports destined for ArcGIS Pro.")
    existing_arc_path = existing_config.get("arcgis_inputs_path", "")
    
    use_arcgis = prompt_for_text("Configure ArcGIS inputs path? (y/n)", "n").lower()
    if use_arcgis in ("y", "yes"):
        arc_path = prompt_for_folder(
            "Select ArcGIS Inputs Folder",
            initial_dir=existing_arc_path if existing_arc_path else str(project_root)
        )
        if arc_path:
            config["arcgis_inputs_path"] = arc_path
            print(f"✓ ArcGIS inputs path set to: {arc_path}")
    else:
        config["arcgis_inputs_path"] = str(project_root / "to_arcgis")
        print(f"✓ Using default ArcGIS inputs path: {project_root / 'to_arcgis'}")
    print()
    
    # Optional: Additional settings
    print("Step 4: Additional Settings (optional)")
    print("-" * 60)
    
    # Max workers for parallel processing
    existing_workers = existing_config.get("max_workers", 4)
    workers_input = prompt_for_text("Max parallel workers", str(existing_workers))
    try:
        config["max_workers"] = int(workers_input)
    except ValueError:
        config["max_workers"] = existing_workers
    
    # Verbose logging
    existing_verbose = existing_config.get("verbose", False)
    verbose_input = prompt_for_text("Enable verbose logging? (y/n)", "y" if existing_verbose else "n")
    config["verbose"] = verbose_input.lower() in ("y", "yes")
    
    print()
    
    # Save configuration
    save_config(config, config_path)
    
    return config


def main() -> None:
    try:
        config = setup_configuration()
        print()
        print("=" * 60)
        print("Configuration complete!")
        print("=" * 60)
        print()
        print("Final configuration:")
        for key, value in config.items():
            print(f"  {key}: {value}")
        print()
        print("You can re-run this script anytime to update your configuration.")
    except KeyboardInterrupt:
        print("\n\nConfiguration cancelled by user.")
        sys.exit(1)


if __name__ == "__main__":
    main()
