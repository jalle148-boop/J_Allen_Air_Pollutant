# -*- coding: utf-8 -*-
"""
Filename and dataset-key parsing utilities.

Extracts structured metadata from the naming conventions used in the
shapelet pickle files.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Filename parsing
# ---------------------------------------------------------------------------
# Filename example:
#   North Carolina_Beaufort_6_shapelets.pkl_2004_000.pkl
#
# Tokens (split on underscore, but state/county may contain spaces):
#   {State}_{County}_{SiteNum}_shapelets.pkl_{Year}_{Chunk}.pkl

_FILENAME_RE = re.compile(
    r"^(?P<state>.+?)_(?P<county>[A-Za-z ]+?)_(?P<site_num>\d+)"
    r"_shapelets\.pkl"
    r"_(?P<year>\d{4})"
    r"_(?P<chunk>\d{3})"
    r"\.pkl$"
)


def parse_filename(name: str | Path) -> dict[str, Any]:
    """
    Parse a shapelet pickle filename into metadata fields.

    Parameters
    ----------
    name : str or Path
        The filename (not full path).  e.g.
        ``North Carolina_Beaufort_6_shapelets.pkl_2004_000.pkl``

    Returns
    -------
    dict
        Keys: ``state``, ``county``, ``site_num`` (int), ``year`` (int),
        ``chunk`` (int).

    Raises
    ------
    ValueError
        If the filename does not match the expected pattern.
    """
    stem = Path(name).name  # ensure we only use the filename
    m = _FILENAME_RE.match(stem)
    if not m:
        raise ValueError(f"Filename does not match expected pattern: {stem}")

    return {
        "state": m.group("state"),
        "county": m.group("county"),
        "site_num": int(m.group("site_num")),
        "year": int(m.group("year")),
        "chunk": int(m.group("chunk")),
    }


# ---------------------------------------------------------------------------
# Dataset-key parsing
# ---------------------------------------------------------------------------
# Key example (from inside the pickle):
#   North Carolina_Beaufort_6_daily_42401_7d_2004_daily_zscore
#
# Tokens:
#   {State}_{County}_{SiteNum}_{Frequency}_{ParamCode}_{Duration}_{Year}_{AggMethod}
#
# AggMethod may itself contain underscores (e.g. "daily_zscore"), so we
# capture everything from the year onward and split once more.

_DATASET_KEY_RE = re.compile(
    r"^(?P<state>.+?)_(?P<county>[A-Za-z ]+?)_(?P<site_num>\d+)"
    r"_(?P<frequency>[a-z]+)"
    r"_(?P<parameter_code>\d+)"
    r"_(?P<duration>\w+)"
    r"_(?P<year>\d{4})"
    r"_(?P<agg_method>.+)$"
)


def parse_dataset_key(key: str) -> dict[str, Any]:
    """
    Parse the single top-level dictionary key from a shapelet pickle.

    Parameters
    ----------
    key : str
        e.g. ``North Carolina_Beaufort_6_daily_42401_7d_2004_daily_zscore``

    Returns
    -------
    dict
        Keys: ``state``, ``county``, ``site_num`` (int), ``frequency``,
        ``parameter_code``, ``duration``, ``year`` (int),
        ``agg_method``.

    Raises
    ------
    ValueError
        If the key does not match the expected pattern.
    """
    m = _DATASET_KEY_RE.match(key)
    if not m:
        raise ValueError(f"Dataset key does not match expected pattern: {key}")

    return {
        "state": m.group("state"),
        "county": m.group("county"),
        "site_num": int(m.group("site_num")),
        "frequency": m.group("frequency"),
        "parameter_code": m.group("parameter_code"),
        "duration": m.group("duration"),
        "year": int(m.group("year")),
        "agg_method": m.group("agg_method"),
    }
