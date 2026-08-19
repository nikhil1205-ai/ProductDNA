"""
Module 4 Deterministic Pattern & Regex Extractor
"""

import re
from typing import List, Dict, Any, Tuple
from .base import BaseExtractor
from ..models.document_models import Document, TextBlock
from ..models.extraction_models import ExtractedAttribute, ExtractionMethod
from ..mapping.attribute_mapper import AttributeMapper

class PatternExtractor(BaseExtractor):
    """
    Deterministic Extractor using Generic Regex Patterns.
    Extracts generic key-value pairs, numeric values with units, and standard identifiers.
    Independent of specific product domains.
    """
    
    IDENTIFIER_PATTERN = re.compile(
        r"^(SKU|Model|Part\s*Number|Part\s*No\.?|P/N|Catalog\s*Number|Product\s*Code|Item\s*Number)\s*[:=-]?\s*([A-Za-z0-9\-_]+)$",
        re.IGNORECASE
    )

    KV_PATTERN = re.compile(
        r"^([A-Za-z0-9\s\-_/()]{2,40})\s*[:=]\s*(.+)$"
    )

    VALUE_UNIT_PATTERN = re.compile(
        r"^([+\-]?\d+(?:\.\d+)?(?:(?:\s*(?:-|to|/)\s*)[+\-]?\d+(?:\.\d+)?)?)\s*([A-Za-z°%µ]+(?:/[A-Za-z]+)?)$"
    )

    def extract(self, document: Document) -> List[ExtractedAttribute]:
        extracted: List[ExtractedAttribute] = []
        seen_keys: set = set()

        for block in document.text_blocks:
            text = block.text
            lines = text.split("\n")
            for line in lines:
                line_clean = line.strip()
                if not line_clean:
                    continue

                raw_attr_name = None
                val = None
                unit = None
                confidence = 0.90

                # 1. Try Identifier Pattern
                id_match = self.IDENTIFIER_PATTERN.match(line_clean)
                if id_match:
                    raw_attr_name = id_match.group(1).strip()
                    val = id_match.group(2).strip()
                    confidence = 0.98
                else:
                    # 2. Try Generic Key-Value Pattern
                    kv_match = self.KV_PATTERN.match(line_clean)
                    if kv_match:
                        raw_attr_name = kv_match.group(1).strip()
                        raw_val = kv_match.group(2).strip()
                        
                        # Check if the value contains a numeric value and a unit
                        vu_match = self.VALUE_UNIT_PATTERN.match(raw_val)
                        if vu_match:
                            val = vu_match.group(1).strip()
                            unit = vu_match.group(2).strip()
                            confidence = 0.95
                        else:
                            val = raw_val
                            confidence = 0.90

                if raw_attr_name and val:
                    # Avoid duplicate extractions of identical attribute from same block
                    dedup_key = f"{raw_attr_name.lower()}:{val.lower()}:{block.location.page}"
                    if dedup_key in seen_keys:
                        continue
                    seen_keys.add(dedup_key)

                    canonical = AttributeMapper.map_attribute(raw_attr_name)
                    
                    extracted.append(
                        ExtractedAttribute(
                            attribute=canonical,
                            raw_attribute_name=raw_attr_name,
                            value=val,
                            unit=unit,
                            source_id=document.source_id,
                            page=block.location.page,
                            section=block.location.section,
                            evidence_text=line_clean,
                            extraction_method=ExtractionMethod.PATTERN_REGEX,
                            extraction_confidence=confidence
                        )
                    )

        return extracted
