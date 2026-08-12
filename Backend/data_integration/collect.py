import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, Union

from .services.validator import (
    validate_file_input,
    validate_url_input,
    validate_json_input,
    detect_input_type
)
from .readers.pdf_reader import read_pdf
from .readers.csv_reader import read_csv
from .readers.url_reader import read_url
from .readers.json_reader import read_json
from .services.metadata_service import (
    extract_file_metadata,
    extract_url_metadata,
    extract_text_or_json_metadata
)
from .services.identity_extractor import extract_identity
from .services.builder import build_standard_product_input
from .schemas.response_schema import StandardProductInput

# Output directory path as per project spec
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "input_data" / "Standard_input"

def generate_request_id() -> str:
    """Generate a unique request ID formatted as REQ-YYYYMMDD-HEX."""
    now_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    short_uuid = uuid.uuid4().hex[:8].upper()
    return f"REQ-{now_str}-{short_uuid}"

def run_module_1(
    file_bytes: Optional[bytes] = None,
    filename: Optional[str] = None,
    url_str: Optional[str] = None,
    json_data: Optional[Any] = None,
    input_text: Optional[str] = None,
    explicit_type: Optional[str] = None
) -> StandardProductInput:
    """
    Main Module 1 Orchestration function: Product Intake & Document Processing.
    Converts raw product input into a standardized Product Input Object,
    saves it to Backend/input_data/Standard_input/, and returns the object.
    """
    # 1. Generate unique request ID
    request_id = generate_request_id()

    # 2. Detect input type
    input_type = detect_input_type(
        file_name=filename,
        file_bytes=file_bytes,
        url_str=url_str,
        json_data=json_data,
        input_text=input_text,
        explicit_type=explicit_type
    )

    content_data: Dict[str, Any] = {}
    metadata_data: Dict[str, Any] = {}

    # 3. Validation, Reader Selection & Content/Metadata Extraction
    if input_type == "PDF":
        if not filename or not file_bytes:
            raise ValueError("PDF input requires file data and filename.")
        validate_file_input(filename, file_bytes)
        content_data = read_pdf(file_bytes)
        metadata_data = extract_file_metadata(filename, file_bytes, mime_type="application/pdf")

    elif input_type == "CSV":
        if not filename or not file_bytes:
            raise ValueError("CSV input requires file data and filename.")
        validate_file_input(filename, file_bytes)
        csv_res = read_csv(file_bytes)
        content_data = {
            "text": csv_res.get("summary_text"),
            "tables": [{
                "columns": csv_res.get("columns", []),
                "rows": csv_res.get("rows", []),
                "row_count": csv_res.get("row_count", 0),
                "column_count": csv_res.get("column_count", 0)
            }],
            "row_count": csv_res.get("row_count"),
            "column_count": csv_res.get("column_count")
        }
        metadata_data = extract_file_metadata(filename, file_bytes, mime_type="text/csv")

    elif input_type == "URL":
        target_url = url_str or input_text
        if not target_url:
            raise ValueError("URL input requires a target URL string.")
        valid_url = validate_url_input(target_url)
        url_res = read_url(valid_url)
        content_data = {
            "text": url_res.get("text"),
            "title": url_res.get("title"),
            "tables": [],
            "structured_data": None
        }
        metadata_data = extract_url_metadata(valid_url, mime_type=url_res.get("mime_type"))

    elif input_type == "JSON":
        raw_payload = json_data if json_data is not None else input_text
        validated_json = validate_json_input(raw_payload)
        json_res = read_json(validated_json)
        content_data = {
            "text": json_res.get("text"),
            "tables": [],
            "structured_data": json_res.get("structured_data")
        }
        metadata_data = extract_text_or_json_metadata("JSON", content_size=len(str(validated_json)))

    elif input_type == "PRODUCT_NAME":
        raw_text = input_text or filename or ""
        if not raw_text.strip():
            raise ValueError("Product name input cannot be empty.")
        content_data = {
            "text": raw_text.strip(),
            "tables": [],
            "structured_data": None
        }
        metadata_data = extract_text_or_json_metadata("PRODUCT_NAME", content_size=len(raw_text))

    else:
        raise ValueError(f"Unsupported input type '{input_type}'.")

    # 4. Identity Extraction
    identity_data = extract_identity(
        input_type=input_type,
        content=content_data,
        raw_input_text=input_text
    )

    # 5. Build Standard Product Input Object
    standard_object = build_standard_product_input(
        request_id=request_id,
        input_type=input_type,
        identity_data=identity_data,
        metadata_data=metadata_data,
        content_data=content_data,
        status="READY_FOR_RESOLUTION"
    )

    # 6. Save JSON output to Backend/input_data/Standard_input/
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    file_path = OUTPUT_DIR / f"{request_id}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(standard_object.model_dump_json(indent=2))

    return standard_object
