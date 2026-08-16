"""
Module 4 Structured Table Extractor
"""

import re
from typing import List, Optional, Tuple
from .base import BaseExtractor
from ..models.document_models import Document, Table
from ..models.extraction_models import ExtractedAttribute, ExtractionMethod
from ..mapping.attribute_mapper import AttributeMapper

class TableExtractor(BaseExtractor):
    """
    Direct Tabular Data Extractor.
    Extracts key-value attributes from PDF and HTML tables without unnecessary LLM calls.
    """
    
    def extract(self, document: Document) -> List[ExtractedAttribute]:
        extracted: List[ExtractedAttribute] = []
        
        for tbl in document.tables:
            # Process pre-parsed key-value pairs
            for raw_key, raw_val in tbl.kv_pairs.items():
                attr_obj = self._create_attribute_from_pair(
                    raw_key=raw_key,
                    raw_val=raw_val,
                    source_id=document.source_id,
                    page=tbl.location.page,
                    section=tbl.location.section or tbl.title
                )
                if attr_obj:
                    extracted.append(attr_obj)

            # Process 2-column rows if kv_pairs wasn't populated
            if not tbl.kv_pairs and tbl.rows:
                for row in tbl.rows:
                    if len(row) >= 2:
                        raw_key = row[0].strip()
                        raw_val = row[1].strip()
                        attr_obj = self._create_attribute_from_pair(
                            raw_key=raw_key,
                            raw_val=raw_val,
                            source_id=document.source_id,
                            page=tbl.location.page,
                            section=tbl.location.section or tbl.title
                        )
                        if attr_obj:
                            extracted.append(attr_obj)

        return extracted

    def _create_attribute_from_pair(
        self,
        raw_key: str,
        raw_val: str,
        source_id: str,
        page: Optional[int],
        section: Optional[str]
    ) -> Optional[ExtractedAttribute]:
        key_clean = raw_key.strip()
        val_clean = raw_val.strip()
        
        if not key_clean or not val_clean or len(key_clean) < 2 or len(val_clean) < 1:
            return None
            
        # Ignore header noise lines
        if key_clean.lower() in ["parameter", "description", "specification", "feature", "item"]:
            return None

        canonical = AttributeMapper.map_attribute(key_clean)
        
        # Split value and unit
        val_part, unit_part = self._split_value_unit(val_clean)
        
        evidence = f"{key_clean}: {val_clean}"

        return ExtractedAttribute(
            attribute=canonical,
            raw_attribute_name=key_clean,
            value=val_part,
            unit=unit_part,
            source_id=source_id,
            page=page,
            section=section,
            evidence_text=evidence,
            extraction_method=ExtractionMethod.TABLE_EXTRACTOR,
            extraction_confidence=0.98
        )

    def _split_value_unit(self, val_str: str) -> Tuple[str, Optional[str]]:
        match = re.match(r"^([0-9.,-]+)\s*([a-zA-Z°/%Ωμµ]+)$", val_str)
        if match:
            return match.group(1).strip(), match.group(2).strip()
        return val_str, None
