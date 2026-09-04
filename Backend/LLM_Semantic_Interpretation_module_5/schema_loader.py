"""
Module 5 — Delivery Schema Loader
Loads the 252-column header list from the authoritative delivery CSV template.
All column names are sourced from the real file to prevent header drift.
"""

import csv
from pathlib import Path
from typing import List, Dict

_DELIVERY_CSV = (
    Path(__file__).resolve().parent.parent
    / "Output_data"
    / "Unihack_ Expected Output - Delivery Format.csv"
)


def load_delivery_headers() -> List[str]:
    """Return the ordered list of delivery schema column names."""
    if not _DELIVERY_CSV.exists():
        raise FileNotFoundError(f"Delivery format CSV not found: {_DELIVERY_CSV}")
    with open(_DELIVERY_CSV, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        headers = next(reader)
    return [h.strip() for h in headers]


def empty_delivery_record() -> Dict[str, str]:
    """Return an ordered dict with every delivery column set to empty string."""
    return {h: "" for h in load_delivery_headers()}
