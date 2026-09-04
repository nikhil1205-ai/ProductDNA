import os
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional

def extract_file_metadata(
    filename: str,
    file_bytes: bytes,
    mime_type: Optional[str] = None,
    row_number: Optional[int] = None,
    total_rows: Optional[int] = None,
    total_columns: Optional[int] = None
) -> Dict[str, Any]:
    """
    Generate dynamic metadata for uploaded file inputs.
    Calculates SHA-256 checksum, file size, extension, timestamp, and optional CSV row/column counts.
    """
    ext = os.path.splitext(filename)[1].lower() if filename else ""
    checksum = hashlib.sha256(file_bytes).hexdigest() if file_bytes else None

    if not mime_type:
        if ext == ".pdf":
            mime_type = "application/pdf"
        elif ext == ".csv":
            mime_type = "text/csv"
        else:
            mime_type = "application/octet-stream"

    res = {
        "filename": filename,
        "extension": ext,
        "mime_type": mime_type,
        "size_bytes": len(file_bytes) if file_bytes else 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "checksum": checksum,
        "source_url": None,
        "retrieved_at": None
    }
    if row_number is not None:
        res["row_number"] = row_number
    if total_rows is not None:
        res["total_rows"] = total_rows
    if total_columns is not None:
        res["total_columns"] = total_columns

    return res

def extract_url_metadata(url: str, mime_type: Optional[str] = "text/html") -> Dict[str, Any]:
    """
    Generate metadata for URL inputs.
    """
    return {
        "filename": None,
        "extension": None,
        "mime_type": mime_type or "text/html",
        "size_bytes": None,
        "created_at": None,
        "checksum": None,
        "source_url": url,
        "retrieved_at": datetime.now(timezone.utc).isoformat()
    }

def extract_text_or_json_metadata(payload_type: str, content_size: int = 0) -> Dict[str, Any]:
    """
    Generate metadata for JSON or raw text / Product Name inputs.
    """
    mime = "application/json" if payload_type == "JSON" else "text/plain"
    return {
        "filename": None,
        "extension": None,
        "mime_type": mime,
        "size_bytes": content_size,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "checksum": None,
        "source_url": None,
        "retrieved_at": None
    }
