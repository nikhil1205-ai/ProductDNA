"""
Module 3 Table Extractor (Tabular Data Extractor)
"""

import uuid
from typing import List, Set
from .base import BaseExtractor
from ..models.document_models import Document
from ..models.extraction_models import EvidenceItem, EvidenceType, ExtractionMethod

class TableExtractor(BaseExtractor):
    """
    Direct Tabular Data Extractor.
    Extracts explicit table rows from tables (CSV, PDF, HTML) into structured evidence units.
    Preserves raw table provenance (page, table name, row index) and raw label/value pairs.
    """
    
    IGNORE_HEADERS = {"attribute", "parameter", "description", "specification", "feature", "item", "property"}

    def extract(self, document: Document) -> List[EvidenceItem]:
        extracted: List[EvidenceItem] = []
        seen: Set[str] = set()
        
        source_type = document.metadata.get("source_type", "text")

        for tbl in document.tables:
            tbl_name = tbl.title or f"Table {tbl.table_id}"
            
            if tbl.rows:
                for row_idx, row in enumerate(tbl.rows, start=1):
                    if not row or not any(cell.strip() for cell in row):
                        continue
                    
                    col0 = row[0].strip()
                    if not col0 or col0.lower() in self.IGNORE_HEADERS:
                        continue

                    raw_label = col0
                    raw_val = ""
                    item_str = ""

                    if len(row) >= 3:
                        val = row[1].strip()
                        unit = row[2].strip()
                        if val:
                            raw_val = f"{val} {unit}".strip() if unit else val
                            item_str = f"{raw_label}: {raw_val}"
                    elif len(row) == 2:
                        val = row[1].strip()
                        if val:
                            raw_val = val
                            item_str = f"{raw_label}: {raw_val}"

                    if item_str and item_str.lower() not in seen:
                        seen.add(item_str.lower())
                        item = EvidenceItem(
                            evidence_id=f"EV-TBL-{uuid.uuid4().hex[:6].upper()}",
                            source_id=document.source_id,
                            source_type=str(source_type),
                            evidence_type=EvidenceType.TABLE_ROW,
                            text=item_str,
                            raw_label=raw_label,
                            raw_value=raw_val if raw_val else None,
                            page_number=tbl.location.page,
                            section=tbl.location.section,
                            table_name=tbl_name,
                            row_number=row_idx,
                            extraction_method=ExtractionMethod.TABLE_EXTRACTOR
                        )
                        extracted.append(item)

            elif tbl.kv_pairs:
                for row_idx, (raw_key, raw_val) in enumerate(tbl.kv_pairs.items(), start=1):
                    key_clean = raw_key.strip()
                    val_clean = raw_val.strip()
                    if key_clean and val_clean and key_clean.lower() not in self.IGNORE_HEADERS:
                        item_str = f"{key_clean}: {val_clean}"
                        if item_str.lower() not in seen:
                            seen.add(item_str.lower())
                            item = EvidenceItem(
                                evidence_id=f"EV-TBL-{uuid.uuid4().hex[:6].upper()}",
                                source_id=document.source_id,
                                source_type=str(source_type),
                                evidence_type=EvidenceType.TABLE_ROW,
                                text=item_str,
                                raw_label=key_clean,
                                raw_value=val_clean,
                                page_number=tbl.location.page,
                                section=tbl.location.section,
                                table_name=tbl_name,
                                row_number=row_idx,
                                extraction_method=ExtractionMethod.TABLE_EXTRACTOR
                            )
                            extracted.append(item)

        return extracted
