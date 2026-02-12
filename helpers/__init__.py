# -*- coding: utf-8 -*-
"""
helpers — shapelet data ingestion toolkit.

Submodules
----------
loader      Load pickle files (.pkl, .zip).
parser      Parse filenames and dataset keys into metadata.
records     Flatten nested pickle data into record dicts.
validator   Validate records against the expected schema.
db          SQLite database writer and schema management.
"""

from helpers.loader import (
    discover_files,
    load_from_path,
    load_single_pkl,
    load_zipped_pkl,
)
from helpers.parser import parse_dataset_key, parse_filename
from helpers.records import iter_records
from helpers.validator import validate_record
from helpers.db import init_db, insert_shapelets, start_ingestion_run, finish_ingestion_run

__all__ = [
    # loader
    "discover_files",
    "load_from_path",
    "load_single_pkl",
    "load_zipped_pkl",
    # parser
    "parse_filename",
    "parse_dataset_key",
    # records
    "iter_records",
    # validator
    "validate_record",
    # db
    "init_db",
    "insert_shapelets",
    "start_ingestion_run",
    "finish_ingestion_run",
]
