"""
Module 3 Table Extractor
"""

from typing import List
from .base import BaseExtractor
from ..models.document_models import Document

class TableExtractor(BaseExtractor):
    """
    Direct Tabular Data Extractor.
    Extracts key-value evidence text strings from tables (CSV, PDF, HTML).
    """
    
    IGNORE_HEADERS = {"attribute", "parameter", "description", "specification", "feature", "item", "property"}

    def extract(self, document: Document) -> List[str]:
        extracted: List[str] = []
        seen: set = set()
        
        for tbl in document.tables:
            if tbl.rows:
                for row in tbl.rows:
                    if not row or not any(cell.strip() for cell in row):
                        continue
                    
                    col0 = row[0].strip()
                    if not col0 or col0.lower() in self.IGNORE_HEADERS:
                        continue

                    item_str = ""
                    if len(row) >= 3:
                        val = row[1].strip()
                        unit = row[2].strip()
                        if val:
                            val_unit = f"{val} {unit}".strip() if unit else val
                            item_str = f"{col0}: {val_unit}"
                    elif len(row) == 2:
                        val = row[1].strip()
                        if val:
                            item_str = f"{col0}: {val}"

                    if item_str and item_str.lower() not in seen:
                        seen.add(item_str.lower())
                        extracted.append(item_str)
                        
            elif tbl.kv_pairs:
                for raw_key, raw_val in tbl.kv_pairs.items():
                    key_clean = raw_key.strip()
                    val_clean = raw_val.strip()
                    if key_clean and val_clean and key_clean.lower() not in self.IGNORE_HEADERS:
                        item_str = f"{key_clean}: {val_clean}"
                        if item_str.lower() not in seen:
                            seen.add(item_str.lower())
                            extracted.append(item_str)

        return extracted
