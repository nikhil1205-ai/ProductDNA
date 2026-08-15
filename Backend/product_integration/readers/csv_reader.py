import io
from typing import Dict, Any, List
import pandas as pd

def read_csv(file_bytes: bytes) -> Dict[str, Any]:
    """
    Read arbitrary CSV content bytes and return column headers, rows, and total row count.
    Avoids hardcoded column names and handles generic CSV formats cleanly.
    """
    if not file_bytes:
        raise ValueError("Empty CSV file provided.")

    try:
        # Decode bytes with fallback encoding support
        try:
            content_str = file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            content_str = file_bytes.decode('latin-1')

        # Read CSV with pandas
        df = pd.read_csv(io.StringIO(content_str))
        
        # Fill NaN values with empty string or null representation
        df = df.where(pd.notnull(df), None)

        columns: List[str] = [str(col).strip() for col in df.columns.tolist()]
        total_rows = len(df)

        # Convert up to 100 rows to dictionary list to avoid memory bloat on massive CSVs
        sample_df = df.head(100)
        rows: List[Dict[str, Any]] = sample_df.to_dict(orient='records')

        # Build readable text summary of CSV rows
        text_lines = [f"CSV Header: {', '.join(columns)}"]
        for idx, row in enumerate(rows[:10]):
            row_items = [f"{k}: {v}" for k, v in row.items() if v is not None]
            text_lines.append(f"Row {idx + 1}: {', '.join(row_items)}")
        
        summary_text = "\n".join(text_lines)

        return {
            "columns": columns,
            "rows": rows,
            "row_count": total_rows,
            "column_count": len(columns),
            "summary_text": summary_text
        }
    except Exception as e:
        raise ValueError(f"Invalid or corrupted CSV content: {str(e)}")
