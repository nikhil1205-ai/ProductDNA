import io
import re
from typing import Dict, Any, List
import pandas as pd

KNOWN_PLACEHOLDERS = {
    "", "null", "-", "na", "n/a", "#n/a", "none",
    "-- unbranded --", "-- no unilog brand --", "-- no dib brand --",
    "-- no brand --", "-- unbranded brand --"
}

def to_snake_case(key: str) -> str:
    """Convert column headers conservatively to snake_case format."""
    s = str(key).strip()
    s = re.sub(r'[\s\-\.\/]+', '_', s)
    s = re.sub(r'(?<=[a-z0-9])([A-Z])', r'_\1', s)
    s = s.lower()
    s = re.sub(r'_+', '_', s).strip('_')
    return s or str(key).lower()

def normalize_cell_value(val: Any) -> Any:
    """Normalize known placeholder strings to None while preserving real content."""
    if val is None or pd.isna(val):
        return None
    val_str = str(val).strip()
    if val_str.lower() in KNOWN_PLACEHOLDERS:
        return None
    return val_str

def read_csv(file_bytes: bytes) -> Dict[str, Any]:
    """
    Read arbitrary CSV content bytes and return dynamic column headers,
    per-row raw & normalized records, and total row count.
    Avoids hardcoded column names and handles generic CSV formats cleanly.
    """
    if not file_bytes or len(file_bytes) == 0:
        raise ValueError("Empty CSV file provided.")

    try:
        # Decode bytes with fallback encoding support
        try:
            content_str = file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            content_str = file_bytes.decode('latin-1')

        # Read CSV with pandas (dtype=str to preserve raw strings like leading zeros)
        df = pd.read_csv(io.StringIO(content_str), dtype=str)
        
        columns: List[str] = [str(col).strip() for col in df.columns.tolist()]
        total_rows = len(df)

        row_records: List[Dict[str, Any]] = []

        for idx, row in df.iterrows():
            raw_dict: Dict[str, Any] = {}
            norm_dict: Dict[str, Any] = {}
            
            for col in columns:
                cell_val = row.get(col)
                if cell_val is None or pd.isna(cell_val):
                    raw_val = None
                else:
                    raw_val = str(cell_val)
                
                raw_dict[col] = raw_val
                norm_key = to_snake_case(col)
                norm_dict[norm_key] = normalize_cell_value(raw_val)

            row_record = {
                "row_number": idx + 1,
                "raw": raw_dict,
                "normalized": norm_dict
            }
            row_records.append(row_record)

        return {
            "columns": columns,
            "row_records": row_records,
            "row_count": total_rows,
            "column_count": len(columns)
        }
    except Exception as e:
        raise ValueError(f"Invalid or corrupted CSV content: {str(e)}")

