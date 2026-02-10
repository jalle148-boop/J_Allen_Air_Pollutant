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
    
    # Database path (required)
    print("Step 1: Database Path")
    print("-" * 60)
    print("Select the folder containing your database files.")
    existing_db_path = existing_config.get("database_path", "")
    initial_dir = existing_db_path if existing_db_path else None
    
    db_path = prompt_for_folder(
        "Select Database Folder",
        initial_dir=initial_dir
    )
    
    if not db_path:
        print("Error: Database path is required.", file=sys.stderr)
        sys.exit(1)
    
    config["database_path"] = db_path
    print(f"✓ Database path set to: {db_path}")
    print()
    
    # Optional: Output path
    print("Step 2: Output Path (optional)")
    print("-" * 60)
    print("Select the folder for output files (leave empty to use project root).")
    existing_output_path = existing_config.get("output_path", "")
    
    use_output = prompt_for_text("Configure output path? (y/n)", "n").lower()
    if use_output in ("y", "yes"):
        output_path = prompt_for_folder(
            "Select Output Folder",
            initial_dir=existing_output_path if existing_output_path else str(project_root)
        )
        if output_path:
            config["output_path"] = output_path
            print(f"✓ Output path set to: {output_path}")
    else:
        config["output_path"] = str(project_root)
        print(f"✓ Using default output path: {project_root}")
    print()
    
    # Optional: Additional settings
    print("Step 3: Additional Settings (optional)")
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
