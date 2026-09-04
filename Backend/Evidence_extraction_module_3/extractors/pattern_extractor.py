"""
Module 3 Pattern Extractor (Deterministic Key-Value / Line Extractor)
"""

import re
import uuid
from typing import List, Set
from .base import BaseExtractor
from ..models.document_models import Document
from ..models.extraction_models import EvidenceItem, EvidenceType, ExtractionMethod

class PatternExtractor(BaseExtractor):
    """
    Deterministic Extractor using Generic Regex Patterns.
    Extracts explicit key-value evidence statements and structured specification lines.
    Returns EvidenceItem objects preserving source labels and values without canonical attribute mapping.
    """

    KV_LINE_PATTERN = re.compile(
        r"^([A-Za-z0-9\s\-_/()]{2,40})\s*[:=-]\s*(.+)$"
    )

    EMBEDDED_KV_PATTERN = re.compile(
        r"(?:^|(?<=\s))([A-Z0-9][A-Za-z0-9\s\-_/()]{1,40}\s*[:=-]\s*.*?\b(?:\.|(?=\s+[A-Z0-9][A-Za-z0-9\s\-_/()]{1,40}\s*[:=-]|\n|$)))"
    )

    def extract(self, document: Document) -> List[EvidenceItem]:
        if document.metadata.get("is_csv") or (document.title and document.title.lower().endswith(".csv")):
            return []

        extracted: List[EvidenceItem] = []
        seen: Set[str] = set()

        source_type = document.metadata.get("source_type", "text")

        for block in document.text_blocks:
            text = block.text.strip()
            if not text:
                continue

            lines = text.split("\n")
            for line_idx, line in enumerate(lines, start=1):
                line_clean = line.strip()
                if not line_clean:
                    continue

                m_line = self.KV_LINE_PATTERN.match(line_clean)
                if m_line:
                    key_part, val_part = m_line.group(1).strip(), m_line.group(2).strip()
                    if key_part and val_part and len(key_part) >= 2:
                        formatted = f"{key_part}: {val_part}"
                        if formatted.lower() not in seen:
                            seen.add(formatted.lower())
                            item = EvidenceItem(
                                evidence_id=f"EV-PAT-{uuid.uuid4().hex[:6].upper()}",
                                source_id=document.source_id,
                                source_type=str(source_type),
                                evidence_type=EvidenceType.LINE,
                                text=formatted,
                                raw_label=key_part,
                                raw_value=val_part,
                                page_number=block.location.page,
                                section=block.location.section,
                                line_number=block.location.line_start or line_idx,
                                extraction_method=ExtractionMethod.PATTERN_EXTRACTOR
                            )
                            extracted.append(item)
                        continue

                matches = self.EMBEDDED_KV_PATTERN.findall(line_clean)
                if matches:
                    for match in matches:
                        match_clean = match.strip()
                        if match_clean and match_clean.lower() not in seen:
                            seen.add(match_clean.lower())
                            
                            # Parse label and value if matching kv format
                            m_sub = self.KV_LINE_PATTERN.match(match_clean)
                            lbl = m_sub.group(1).strip() if m_sub else None
                            val = m_sub.group(2).strip() if m_sub else None

                            item = EvidenceItem(
                                evidence_id=f"EV-PAT-{uuid.uuid4().hex[:6].upper()}",
                                source_id=document.source_id,
                                source_type=str(source_type),
                                evidence_type=EvidenceType.LINE,
                                text=match_clean,
                                raw_label=lbl,
                                raw_value=val,
                                page_number=block.location.page,
                                section=block.location.section,
                                line_number=block.location.line_start or line_idx,
                                extraction_method=ExtractionMethod.PATTERN_EXTRACTOR
                            )
                            extracted.append(item)

        return extracted
