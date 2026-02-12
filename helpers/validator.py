# -*- coding: utf-8 -*-
"""
Record validation utilities.

Checks that flat record dicts conform to the expected schema before
they are written to the database.
"""

from __future__ import annotations

import datetime
from typing import Any


# ---------------------------------------------------------------------------
# Schema definition
# ---------------------------------------------------------------------------

# (field_name, expected_type, required)
_SCHEMA: list[tuple[str, type | tuple[type, ...], bool]] = [
    ("dataset_key",      str,            True),
    ("shapelet_id",      int,            True),
    ("state",            str,            True),
    ("county",           str,            True),
    ("site_num",         int,            True),
    ("latitude",         float,          True),
    ("longitude",        float,          True),
    ("location",         str,            False),
    ("year",             int,            True),
    ("start_date",       datetime.date,  True),
    ("end_date",         datetime.date,  True),
    ("length_days",      int,            True),
    ("pattern_type",     str,            True),
    ("data_type",        str,            True),
    ("quality",          float,          True),
    ("shapelet_values",  list,           True),
    ("source_file",      (str, type(None)), False),
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate_record(record: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate a single flat record against the expected schema.

    Parameters
    ----------
    record : dict
        A flat record as produced by :func:`helpers.records.iter_records`.

    Returns
    -------
    tuple[bool, list[str]]
        ``(is_valid, errors)`` where *errors* is a list of human-readable
        strings describing any problems found.  Empty when valid.
    """
    errors: list[str] = []

    # --- Missing required fields ---
    for field, _, required in _SCHEMA:
        if required and field not in record:
            errors.append(f"missing required field: {field}")

    # --- Type checks ---
    for field, expected, _ in _SCHEMA:
        if field not in record:
            continue
        value = record[field]
        if value is None and not _:
            continue  # optional field, None is OK
        if not isinstance(value, expected):
            errors.append(
                f"{field}: expected {_type_label(expected)}, "
                f"got {type(value).__name__}"
            )

    # --- Domain checks ---
    if "year" in record and isinstance(record["year"], int):
        if not (1900 <= record["year"] <= 2100):
            errors.append(f"year out of range: {record['year']}")

    if "length_days" in record and isinstance(record["length_days"], int):
        if record["length_days"] < 1:
            errors.append(f"length_days must be >= 1, got {record['length_days']}")

    if "latitude" in record and isinstance(record["latitude"], float):
        if not (-90.0 <= record["latitude"] <= 90.0):
            errors.append(f"latitude out of range: {record['latitude']}")

    if "longitude" in record and isinstance(record["longitude"], float):
        if not (-180.0 <= record["longitude"] <= 180.0):
            errors.append(f"longitude out of range: {record['longitude']}")

    if (
        "start_date" in record
        and "end_date" in record
        and isinstance(record["start_date"], datetime.date)
        and isinstance(record["end_date"], datetime.date)
    ):
        if record["end_date"] < record["start_date"]:
            errors.append("end_date is before start_date")

    if "shapelet_values" in record and isinstance(record["shapelet_values"], list):
        if len(record["shapelet_values"]) == 0:
            errors.append("shapelet_values is empty")

    return (len(errors) == 0, errors)


def _type_label(t: type | tuple[type, ...]) -> str:
    """Pretty-print a type or tuple of types."""
    if isinstance(t, tuple):
        return " | ".join(x.__name__ for x in t)
    return t.__name__
