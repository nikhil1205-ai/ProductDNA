import io
from typing import Dict, Any, List
import pandas as pd

KNOWN_PLACEHOLDERS = {
    "", "null", "-", "na", "n/a", "#n/a", "none",
    "-- unbranded --", "-- no unilog brand --", "-- no dib brand --",
    "-- no brand --", "-- unbranded brand --"
}

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
        rows_sample: List[Dict[str, Any]] = []

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
                norm_dict[col] = normalize_cell_value(raw_val)

            row_record = {
                "row_number": idx + 1,
                "raw": raw_dict,
                "normalized": norm_dict
            }
            row_records.append(row_record)
            if idx < 100:
                rows_sample.append(raw_dict)

        # Build readable text summary of CSV header and first 10 rows
        text_lines = [f"CSV Header: {', '.join(columns)}"]
        for rr in row_records[:10]:
            row_items = [f"{k}: {v}" for k, v in rr["normalized"].items() if v is not None]
            text_lines.append(f"Row {rr['row_number']}: {', '.join(row_items)}")
        
        summary_text = "\n".join(text_lines)

        return {
            "columns": columns,
            "row_records": row_records,
            "rows": rows_sample,
            "row_count": total_rows,
            "column_count": len(columns),
            "summary_text": summary_text
        }
    except Exception as e:
        raise ValueError(f"Invalid or corrupted CSV content: {str(e)}")

