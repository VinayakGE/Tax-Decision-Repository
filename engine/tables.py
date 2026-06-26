"""Tax Table loader. Provides lookup for TaxTable:2024.<file>.<path> references."""

import json
import os
from functools import lru_cache

_TABLES_DIR = os.path.join(os.path.dirname(__file__), "..", "tables")


@lru_cache(maxsize=None)
def _load(year: str, name: str) -> dict:
    path = os.path.join(_TABLES_DIR, year, f"{name}.json")
    with open(path) as f:
        return json.load(f)


def get(ref: str):
    """
    Resolve a TaxTable reference.
    ref format: "2024.tax_slabs.new_regime.slabs"
    Returns the value at the given path within the table file.
    """
    parts = ref.split(".")
    year = parts[0]
    file_name = parts[1]
    data = _load(year, file_name)
    for key in parts[2:]:
        data = data[key]
    return data
