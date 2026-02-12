# -*- coding: utf-8 -*-
"""
Pickle file loading utilities.

Handles loading shapelet data from standalone .pkl files, .zip-wrapped
pickles, and batch loading from a directory.
"""

from __future__ import annotations

import pickle
import zipfile
from pathlib import Path
from typing import Any


def load_single_pkl(file_path: str | Path) -> dict:
    """
    Load a single pickle file and return its contents.

    Parameters
    ----------
    file_path : str or Path
        Path to a .pkl file.

    Returns
    -------
    dict
        The deserialized pickle data (top-level dict with one dataset key).
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Pickle file not found: {file_path}")
    if not file_path.suffix == ".pkl":
        raise ValueError(f"Expected .pkl file, got: {file_path.suffix}")

    with open(file_path, "rb") as f:
        data = pickle.load(f)

    return data


def load_zipped_pkl(
    zip_path: str | Path,
    member: str | None = None,
) -> tuple[Any, str]:
    """
    Load a pickle from inside a zip archive.

    Parameters
    ----------
    zip_path : str or Path
        Path to the .zip file.
    member : str, optional
        Name of the .pkl member inside the zip.  If *None*, the first
        .pkl entry is used.

    Returns
    -------
    tuple[Any, str]
        (deserialized object, member name used)
    """
    zip_path = Path(zip_path)
    if not zip_path.exists():
        raise FileNotFoundError(f"Zip file not found: {zip_path}")

    with zipfile.ZipFile(zip_path, "r") as archive:
        pkl_members = [n for n in archive.namelist() if n.lower().endswith(".pkl")]
        if not pkl_members:
            raise ValueError("Zip file contains no .pkl entries")

        target = member or pkl_members[0]
        if target not in archive.namelist():
            raise ValueError(f"Member not found in zip: {target}")

        with archive.open(target, "r") as f:
            return pickle.load(f), target


def load_from_path(path: str | Path) -> dict:
    """
    Smart loader: dispatches to the right loader based on file extension.

    Parameters
    ----------
    path : str or Path
        Path to a .pkl or .zip file.

    Returns
    -------
    dict
        The deserialized pickle data.
    """
    path = Path(path)
    ext = path.suffix.lower()

    if ext == ".zip":
        data, _ = load_zipped_pkl(path)
        return data
    elif ext == ".pkl":
        return load_single_pkl(path)
    else:
        raise ValueError(f"Unsupported file type: {ext} (expected .pkl or .zip)")


def discover_files(
    directory: str | Path,
    extensions: tuple[str, ...] = (".pkl", ".zip"),
    recursive: bool = True,
) -> list[Path]:
    """
    Find all data files in a directory.

    Parameters
    ----------
    directory : str or Path
        Root directory to scan.
    extensions : tuple of str
        File extensions to include (case-insensitive).
    recursive : bool
        If True, search subdirectories as well.

    Returns
    -------
    list[Path]
        Sorted list of matching file paths.
    """
    directory = Path(directory)
    if not directory.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")

    files: list[Path] = []
    pattern = "**/*" if recursive else "*"
    for p in directory.glob(pattern):
        if p.is_file() and p.suffix.lower() in extensions:
            files.append(p)

    return sorted(files)
