"""
Module 3 Identifier Extractor (Deterministic)
"""

import re
import uuid
from typing import List, Set
from .base import BaseExtractor
from ..models.document_models import Document
from ..models.extraction_models import EvidenceItem, EvidenceType, ExtractionMethod

class IdentifierExtractor(BaseExtractor):
    """
    Deterministic Extractor for Product Identifiers.
    Extracts explicit part numbers, model numbers, SKUs, GTIN, UPC, EAN, and catalog numbers.
    Preserves original label and value terminology without canonical attribute mapping.
    """

    IDENTIFIER_PATTERNS = [
        # Explicit Key-Value matches for product identifiers
        re.compile(
            r"(?i)\b(Manufacturer\s+Part\s+Number|Part\s+Number|Part\s+No|P/N|MPN|Model\s+Number|Model\s+No|Model|Catalog\s+Number|Catalog\s+No|SKU|UPC|EAN|GTIN|Alternate\s+Part\s+Number)\s*[:=-]\s*([A-Za-z0-9\-_/.]{2,50})"
        ),
    ]

    def extract(self, document: Document) -> List[EvidenceItem]:
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

                for pattern in self.IDENTIFIER_PATTERNS:
                    for match in pattern.finditer(line_clean):
                        raw_label = match.group(1).strip()
                        raw_value = match.group(2).strip()

                        if not raw_label or not raw_value:
                            continue

                        evidence_str = f"{raw_label}: {raw_value}"
                        dedup_key = evidence_str.lower()

                        if dedup_key not in seen:
                            seen.add(dedup_key)
                            item = EvidenceItem(
                                evidence_id=f"EV-ID-{uuid.uuid4().hex[:6].upper()}",
                                source_id=document.source_id,
                                source_type=str(source_type),
                                evidence_type=EvidenceType.IDENTIFIER,
                                text=evidence_str,
                                raw_label=raw_label,
                                raw_value=raw_value,
                                page_number=block.location.page,
                                section=block.location.section,
                                line_number=block.location.line_start or line_idx,
                                extraction_method=ExtractionMethod.IDENTIFIER_EXTRACTOR
                            )
                            extracted.append(item)

        return extracted
