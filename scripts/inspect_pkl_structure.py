# -*- coding: utf-8 -*-
"""
Inspect a pickle file and report its structure.

Usage:
    python scripts/inspect_pkl_structure.py --input path\to\file.pkl
    python scripts/inspect_pkl_structure.py --input path\to\file.pkl --output report.txt
    python scripts/inspect_pkl_structure.py --input path\to\file.zip
    python scripts/inspect_pkl_structure.py --input path\to\file.zip --zip-member data.pkl
    python scripts/inspect_pkl_structure.py   # Opens file dialog to select file interactively
"""

from __future__ import annotations

import argparse
import pickle
import sys
import zipfile
from collections.abc import Mapping, Sequence
from tkinter import Tk, filedialog
from typing import Any


def prompt_for_file() -> str | None:
    """Open a file dialog to select a .pkl or .zip file."""
    root = Tk()
    root.withdraw()  # Hide the main window
    root.attributes("-topmost", True)  # Bring dialog to front
    
    file_path = filedialog.askopenfilename(
        title="Select a pickle (.pkl) or zip file",
        filetypes=[
            ("Pickle files", "*.pkl"),
            ("Zip files", "*.zip"),
            ("All files", "*.*")
        ]
    )
    root.destroy()
    return file_path if file_path else None


def load_pickle(path: str) -> Any:
    with open(path, "rb") as handle:
        return pickle.load(handle)


def load_pickle_from_zip(path: str, member: str | None) -> tuple[Any, str]:
    with zipfile.ZipFile(path, "r") as archive:
        members = [name for name in archive.namelist() if name.lower().endswith(".pkl")]
        if not members:
            raise ValueError("Zip file contains no .pkl entries")

        target = member or members[0]
        if target not in archive.namelist():
            raise ValueError(f"Zip member not found: {target}")

        with archive.open(target, "r") as handle:
            return pickle.load(handle), target


def _is_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray))


def summarize(obj: Any, *, max_depth: int, max_items: int, _depth: int = 0, _seen: set[int] | None = None) -> list[str]:
    if _seen is None:
        _seen = set()

    lines: list[str] = []
    indent = "  " * _depth

    obj_id = id(obj)
    if obj_id in _seen:
        lines.append(f"{indent}- <cycle detected>")
        return lines
    _seen.add(obj_id)

    if _depth > max_depth:
        lines.append(f"{indent}- <max depth reached>")
        return lines

    if isinstance(obj, Mapping):
        lines.append(f"{indent}- dict (keys={len(obj)})")
        for idx, (key, value) in enumerate(obj.items()):
            if idx >= max_items:
                lines.append(f"{indent}  - <truncated keys at {max_items} items>")
                break
            lines.append(f"{indent}  - key: {repr(key)}")
            lines.extend(summarize(value, max_depth=max_depth, max_items=max_items, _depth=_depth + 2, _seen=_seen))
        return lines

    if _is_sequence(obj):
        lines.append(f"{indent}- list (len={len(obj)})")
        for idx, value in enumerate(obj[:max_items]):
            lines.append(f"{indent}  - index: {idx}")
            lines.extend(summarize(value, max_depth=max_depth, max_items=max_items, _depth=_depth + 2, _seen=_seen))
        if len(obj) > max_items:
            lines.append(f"{indent}  - <truncated items at {max_items} items>")
        return lines

    lines.append(f"{indent}- {type(obj).__name__}: {repr(obj)}")
    return lines


def build_report(path: str, max_depth: int, max_items: int, zip_member: str | None) -> str:
    if path.lower().endswith(".zip"):
        obj, member = load_pickle_from_zip(path, zip_member)
        source_label = f"{path}::{member}"
    else:
        obj = load_pickle(path)
        source_label = path
    header = [
        "Pickle Structure Report",
        f"Input: {source_label}",
        f"Max depth: {max_depth}",
        f"Max items per container: {max_items}",
        "",
        "Structure:",
    ]
    structure_lines = summarize(obj, max_depth=max_depth, max_items=max_items)
    return "\n".join(header + structure_lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect a pickle file and report its structure.")
    parser.add_argument("--input", help="Path to a .pkl or .zip file (will prompt if not provided)")
    parser.add_argument("--zip-member", help="Optional .pkl member inside a zip file")
    parser.add_argument("--output", help="Optional path to write the report")
    parser.add_argument("--max-depth", type=int, default=6, help="Maximum recursion depth")
    parser.add_argument("--max-items", type=int, default=5, help="Max items per container to display")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    
    # Get input file path - prompt if not provided
    input_path = args.input
    if not input_path:
        print("No input file specified. Opening file dialog...")
        input_path = prompt_for_file()
        if not input_path:
            print("No file selected. Exiting.")
            sys.exit(1)
        print(f"Selected: {input_path}\n")
    
    report = build_report(input_path, args.max_depth, args.max_items, args.zip_member)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(report)
    else:
        print(report)


if __name__ == "__main__":
    main()
