"""
Module 4 Content Cleaning & Text Normalization Utilities
"""

import re
import hashlib
from typing import List, Set
from ..models.document_models import TextBlock, Table

def clean_whitespace(text: str) -> str:
    """Normalize irregular whitespaces and line endings."""
    if not text:
        return ""
    # Replace carriage returns
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Trim leading/trailing spaces per line
    lines = [line.strip() for line in text.split("\n")]
    return "\n".join(lines).strip()

def remove_duplicate_text_blocks(blocks: List[TextBlock]) -> List[TextBlock]:
    """Remove exact duplicate text blocks based on content hash."""
    seen_hashes: Set[str] = set()
    unique_blocks: List[TextBlock] = []
    
    for block in blocks:
        normalized = clean_whitespace(block.text.lower())
        if not normalized or len(normalized) < 5:
            unique_blocks.append(block)
            continue
            
        block_hash = hashlib.md5(normalized.encode("utf-8")).hexdigest()
        if block_hash not in seen_hashes:
            seen_hashes.add(block_hash)
            unique_blocks.append(block)
            
    return unique_blocks

def normalize_unit_string(val_unit_str: str) -> str:
    """Basic unit/value representation cleanup (e.g., 380 - 480 V -> 380-480 V)."""
    if not val_unit_str:
        return ""
    # 380 - 480 V -> 380-480 V
    cleaned = re.sub(r"(\d+)\s*-\s*(\d+)", r"\1-\2", val_unit_str)
    # Fix spaces before common units
    cleaned = re.sub(r"(\d+)\s+(V|kV|W|kW|MW|A|mA|Hz|RPM|kg|g|m|cm|mm|bar|Pa|HP|nm|Nm)\b", r"\1 \2", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()
