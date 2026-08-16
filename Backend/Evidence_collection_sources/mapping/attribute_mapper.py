"""
Module 4 Canonical Attribute Mapper
"""

import re
from typing import Optional
from .canonical_attributes import SYNONYM_MAP

class AttributeMapper:
    """
    Maps raw attribute names / labels extracted from sources to canonical attribute names.
    """
    
    @staticmethod
    def map_attribute(raw_name: str) -> str:
        if not raw_name:
            return "unknown_attribute"

        cleaned = raw_name.strip().lower()
        # Remove parenthetical units e.g. "Input Voltage (V)" -> "input voltage"
        cleaned = re.sub(r"\s*\([^)]*\)", "", cleaned).strip()
        # Remove colons or trailing symbols
        cleaned = cleaned.rstrip(":").strip()

        # 1. Exact match in dictionary
        if cleaned in SYNONYM_MAP:
            return SYNONYM_MAP[cleaned]

        # 2. Substring matching for known canonical terms
        for term, canonical in SYNONYM_MAP.items():
            if term in cleaned or cleaned in term:
                return canonical

        # 3. Fallback: Convert raw name to clean snake_case identifier
        snake = re.sub(r"[^a-zA-Z0-9]+", "_", cleaned).strip("_")
        return snake if snake else "attribute"
