import re
from typing import List
from .base import BaseExtractor
from ..models.document_models import Document

class PatternExtractor(BaseExtractor):
    """
    Deterministic Extractor using Generic Regex Patterns.
    Extracts individual key-value evidence statements and structured specification lines.
    Returns plain evidence text strings without canonical attribute mapping.
    """
    
    # Generic Key-Value pattern: Key (2-40 chars) followed by :, =, or - and Value
    KV_LINE_PATTERN = re.compile(
        r"^([A-Za-z0-9\s\-_/()]{2,40})\s*[:=-]\s*(.+)$"
    )

    # Regex for extracting embedded key-value pairs when multiple exist on one line or block
    EMBEDDED_KV_PATTERN = re.compile(
        r"(?:^|(?<=\s))([A-Z0-9][A-Za-z0-9\s\-_/()]{1,40}\s*[:=-]\s*.*?\b(?:\.|(?=\s+[A-Z0-9][A-Za-z0-9\s\-_/()]{1,40}\s*[:=-]|\n|$)))"
    )

    def extract(self, document: Document) -> List[str]:
        # CSV files are handled by TableExtractor
        if document.metadata.get("is_csv") or (document.title and document.title.lower().endswith(".csv")):
            return []

        extracted: List[str] = []
        seen: set = set()

        for block in document.text_blocks:
            text = block.text.strip()
            if not text:
                continue

            lines = text.split("\n")
            for line in lines:
                line_clean = line.strip()
                if not line_clean:
                    continue

                # Case A: Line is a single clean Key: Value pair
                m_line = self.KV_LINE_PATTERN.match(line_clean)
                if m_line:
                    key_part, val_part = m_line.group(1).strip(), m_line.group(2).strip()
                    if key_part and val_part and len(key_part) >= 2:
                        formatted = f"{key_part}: {val_part}"
                        if formatted.lower() not in seen:
                            seen.add(formatted.lower())
                            extracted.append(formatted)
                        continue

                # Case B: Embedded or concatenated key-value statements in a block/line
                matches = self.EMBEDDED_KV_PATTERN.findall(line_clean)
                if matches:
                    for match in matches:
                        match_clean = match.strip()
                        if match_clean and match_clean.lower() not in seen:
                            seen.add(match_clean.lower())
                            extracted.append(match_clean)

        return extracted

