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
    Deterministic Extractor using Regex Patterns.
    Extracts explicit numeric + unit technical specifications and standard identifiers.
    """
    
    PATTERNS: List[Tuple[str, str, float]] = [
        # (attribute_key, regex_pattern, confidence)
        ("voltage", r"(?:input|supply|mains|rated|nominal)?\s*voltage\s*[:=]?\s*(\d+(?:[.-]\d+)?)\s*(V|kV|VAC|VDC)\b", 0.99),
        ("power", r"(?:rated|motor|output|nominal)?\s*power\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(kW|MW|W|HP)\b", 0.99),
        ("current", r"(?:rated|input|nominal|max)?\s*current\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(A|mA)\b", 0.99),
        ("frequency", r"(?:mains|supply|operating)?\s*frequency\s*[:=]?\s*(\d+(?:[.-]\d+)?)\s*(Hz)\b", 0.99),
        ("weight", r"(?:net|product|gross)?\s*weight\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(kg|g|lbs)\b", 0.99),
        ("ip_rating", r"\b(IP\s*\d{2})\b", 0.95),
        ("dimensions", r"(\d+(?:\.\d+)?\s*[xX×]\s*\d+(?:\.\d+)?\s*(?:[xX×]\s*\d+(?:\.\d+)?)?)\s*(mm|cm|m|in)\b", 0.95),
        ("bore_diameter", r"(?:bore|inner)\s*diameter\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(mm|in)\b", 0.99),
        ("outer_diameter", r"(?:outer|outside)\s*diameter\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(mm|in)\b", 0.99),
        ("limiting_speed", r"(?:limiting|reference|max)?\s*speed\s*[:=]?\s*(\d+(?:,\d+)?)\s*(r/min|rpm)\b", 0.95),
        ("sku", r"\bSKU\s*[:=]?\s*([A-Z0-9-]{5,25})\b", 0.98),
        ("model", r"\bModel\s*[:=]?\s*([A-Z0-9-]{4,25})\b", 0.95),
        ("part_number", r"\b(?:Part\s*Number|Part\s*No|P/N)\s*[:=]?\s*([A-Z0-9-]{5,25})\b", 0.98),
    ]

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

                for attr_key, pattern, confidence in self.PATTERNS:
                    match = re.search(pattern, line_clean, re.IGNORECASE)
                    if match:
                        groups = match.groups()
                        val = groups[0].strip()
                        unit = groups[1].strip() if len(groups) > 1 else None

                        # Avoid duplicate extractions of identical attribute from same block
                        dedup_key = f"{attr_key}:{val}:{block.location.page}"
                        if dedup_key in seen_keys:
                            continue
                        seen_keys.add(dedup_key)

                        canonical = AttributeMapper.map_attribute(attr_key)
                        
                        extracted.append(
                            ExtractedAttribute(
                                attribute=canonical,
                                raw_attribute_name=attr_key,
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
