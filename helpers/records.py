# -*- coding: utf-8 -*-
"""
Record flattening utilities.

Converts the nested pickle structure into flat record dictionaries
suitable for database insertion.
"""

from __future__ import annotations

import datetime
from typing import Any, Iterator

import numpy as np


def iter_records(
    data: dict,
    source_file: str | None = None,
) -> Iterator[dict[str, Any]]:
    """
    Yield one flat record dict per shapelet from a loaded pickle object.

    Each pickle contains ``{dataset_key: [shapelet_dict, ...]}``.
    This generator walks that structure and yields a normalized dict
    per shapelet.

    Parameters
    ----------
    data : dict
        A loaded pickle object (one top-level key).
    source_file : str, optional
        Original filename — attached to every record for traceability.

    Yields
    ------
    dict
        A flat record with the following keys:

        - ``dataset_key`` (str)
        - ``shapelet_id`` (int)
        - ``state`` (str)
        - ``county`` (str)
        - ``site_num`` (int)
        - ``latitude`` (float)
        - ``longitude`` (float)
        - ``year`` (int)
        - ``start_date`` (datetime.date)
        - ``end_date`` (datetime.date)
        - ``length_days`` (int)
        - ``pattern_type`` (str)
        - ``data_type`` (str)
        - ``quality`` (float)
        - ``shapelet_values`` (list[float])
        - ``source_file`` (str | None)
    """
    for dataset_key, shapelets in data.items():
        for shapelet in shapelets:
            yield _flatten_shapelet(dataset_key, shapelet, source_file)


def _flatten_shapelet(
    dataset_key: str,
    raw: dict[str, Any],
    source_file: str | None,
) -> dict[str, Any]:
    """
    Convert a single shapelet dict into a flat, serialisable record.

    Numpy scalars are cast to native Python types so they can be
    stored in SQLite without adapter issues.
    """
    return {
        # Identity / grouping
        "dataset_key": dataset_key,
        "shapelet_id": int(raw["shapelet_id"]),
        "source_file": source_file,
        # Location
        "state": str(raw["state"]),
        "county": str(raw["county"]),
        "site_num": _to_int(raw["site_num"]),
        "latitude": _to_float(raw["latitude"]),
        "longitude": _to_float(raw["longitude"]),
        "location": str(raw.get("location", "")),
        # Time
        "year": int(raw["year"]),
        "start_date": _to_date(raw["start_date"]),
        "end_date": _to_date(raw["end_date"]),
        "length_days": int(raw["length_days"]),
        # Classification
        "pattern_type": str(raw["pattern_type"]),
        "data_type": str(raw["data_type"]),
        # Quality & data
        "quality": _to_float(raw["quality"]),
        "shapelet_values": _ndarray_to_list(raw["shapelet"]),
    }


# ---------------------------------------------------------------------------
# Type-coercion helpers
# ---------------------------------------------------------------------------

def _to_float(value: Any) -> float:
    """Convert numpy float64 (or similar) to native float."""
    if isinstance(value, (np.floating, np.integer)):
        return float(value)
    return float(value)


def _to_int(value: Any) -> int:
    """Convert numpy int64 (or similar) to native int."""
    if isinstance(value, (np.integer,)):
        return int(value)
    return int(value)


def _to_date(value: Any) -> datetime.date:
    """Accept ``datetime.date`` or ``datetime.datetime``, return ``date``."""
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    raise TypeError(f"Cannot convert {type(value).__name__} to date")


def _ndarray_to_list(arr: Any) -> list[float]:
    """Convert a numpy ndarray to a plain Python list of floats."""
    if isinstance(arr, np.ndarray):
        return arr.tolist()
    return list(arr)
