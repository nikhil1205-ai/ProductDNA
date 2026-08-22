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
from .schemas.response_schema import StandardProductInput, StandardBatchResponse

import sys
if str(Path(__file__).resolve().parent.parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from product_resolution_engine.resolution_main import run_resolution

# Output directory path as per project spec
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "input_data" / "Standard_input"

def generate_request_id() -> str:
    """Generate a unique request ID formatted as REQ-YYYYMMDD-HEX."""
    now_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    short_uuid = uuid.uuid4().hex[:8].upper()
    return f"REQ-{now_str}-{short_uuid}"

def integration_module_function(
    file_bytes: Optional[bytes] = None,
    filename: Optional[str] = None,
    url_str: Optional[str] = None,
    json_data: Optional[Any] = None,
    input_text: Optional[str] = None,
    explicit_type: Optional[str] = None,
    return_batch: bool = False
) -> Union[StandardProductInput, StandardBatchResponse]:
    """
    Main Module 1 Orchestration function: Product Intake & Document Processing.
    Converts raw product input into standardized Product Input Objects.
    For CSV datasets, processes row-by-row, saving one JSON per product row.
    Saves results to Backend/input_data/Standard_input/ and returns result object.
    """
    # 1. Detect input type
    input_type = detect_input_type(
        file_name=filename,
        file_bytes=file_bytes,
        url_str=url_str,
        json_data=json_data,
        input_text=input_text,
        explicit_type=explicit_type
    )

    # Make sure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 2. CSV processing (row-by-row)
    if input_type == "CSV":
        if not filename or not file_bytes:
            raise ValueError("CSV input requires file data and filename.")
        validate_file_input(filename, file_bytes)
        csv_res = read_csv(file_bytes)
        
        row_records = csv_res.get("row_records", [])
        columns = csv_res.get("columns", [])
        total_rows = csv_res.get("row_count", 0)

        if not row_records:
            raise ValueError("CSV file contains no data rows.")

        items: List[StandardProductInput] = []

        for rr in row_records:
            req_id = generate_request_id()
            row_num = rr["row_number"]
            raw_row = rr["raw"]
            norm_row = rr["normalized"]

            # Content payload for this specific row
            content_data = {
                "text": f"CSV Row {row_num}: {', '.join([f'{k}: {v}' for k, v in norm_row.items() if v is not None])}",
                "title": f"Row {row_num} from {filename}",
                "tables": [{
                    "columns": columns,
                    "rows": [raw_row]
                }],
                "structured_data": norm_row,
                "row_count": total_rows,
                "column_count": len(columns)
            }

            # File metadata
            metadata_data = extract_file_metadata(filename, file_bytes, mime_type="text/csv")
            metadata_data["source_row"] = row_num

            # Conservative Identity Extraction for current row
            identity_data = extract_identity(
                input_type="CSV",
                content={
                    "normalized_row": norm_row,
                    "raw_row": raw_row,
                    "text": content_data["text"]
                }
            )

            # Source record (raw + normalized)
            source_record_data = {
                "row_number": row_num,
                "raw": raw_row,
                "normalized": norm_row
            }

            # Build StandardProductInput
            standard_obj = build_standard_product_input(
                request_id=req_id,
                input_type="CSV",
                identity_data=identity_data,
                metadata_data=metadata_data,
                content_data=content_data,
                source_record_data=source_record_data,
                status="READY_FOR_RESOLUTION"
            )

            # Invoke Module 2 Resolution safely
            try:
                resolved_dict = run_resolution(standard_obj.model_dump())
                standard_obj.resolution_data = resolved_dict.get("resolution_data")
                standard_obj.status = resolved_dict.get("status", standard_obj.status)
            except Exception as e:
                print(f"Warning: Module 2 resolution failed for {req_id} (Row {row_num}): {str(e)}")

            # Save individual JSON per product row
            file_path = OUTPUT_DIR / f"{req_id}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(standard_obj.model_dump_json(indent=2))

            items.append(standard_obj)

        if return_batch or len(items) > 1:
            return StandardBatchResponse(
                status="SUCCESS",
                total_rows=total_rows,
                processed_count=len(items),
                successful_count=len(items),
                failed_count=0,
                detected_headers=columns,
                filename=filename,
                items=items
            )
        else:
            return items[0]

    # 3. Single product input types (PDF, URL, JSON, PRODUCT_NAME)
    request_id = generate_request_id()
    content_data: Dict[str, Any] = {}
    metadata_data: Dict[str, Any] = {}

    if input_type == "PDF":
        if not filename or not file_bytes:
            raise ValueError("PDF input requires file data and filename.")
        validate_file_input(filename, file_bytes)
        content_data = read_pdf(file_bytes)
        metadata_data = extract_file_metadata(filename, file_bytes, mime_type="application/pdf")

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

    # Identity Extraction
    identity_data = extract_identity(
        input_type=input_type,
        content=content_data,
        raw_input_text=input_text
    )

    # Build Standard Product Input Object
    standard_object = build_standard_product_input(
        request_id=request_id,
        input_type=input_type,
        identity_data=identity_data,
        metadata_data=metadata_data,
        content_data=content_data,
        status="READY_FOR_RESOLUTION"
    )

    # Run Module 2 Resolution
    try:
        resolved_dict = run_resolution(standard_object.model_dump())
        standard_object.resolution_data = resolved_dict.get("resolution_data")
        standard_object.status = resolved_dict.get("status", standard_object.status)
    except Exception as e:
        print(f"Warning: Module 2 resolution failed for {request_id}: {str(e)}")

    # Save JSON output to Backend/input_data/Standard_input/
    file_path = OUTPUT_DIR / f"{request_id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(standard_object.model_dump_json(indent=2))

    return standard_object


if __name__ == "__main__":
    sample_csv_path = Path(__file__).resolve().parent.parent / "input_data" / "Sample_input" / "Unihack_ Sample Dataset - Input.csv"
    if sample_csv_path.exists():
        print(f"Processing sample CSV dataset: {sample_csv_path.name}")
        with open(sample_csv_path, "rb") as f:
            csv_bytes = f.read()
        res = integration_module_function(
            file_bytes=csv_bytes,
            filename=sample_csv_path.name,
            return_batch=True
        )
        if isinstance(res, StandardBatchResponse):
            print(f"=== Module 1 Intake Completed ===")
            print(f"Total Rows: {res.total_rows}")
            print(f"Processed: {res.processed_count}")
            print(f"Successful: {res.successful_count}")
            print(f"Failed: {res.failed_count}")
            print(f"Detected Headers ({len(res.detected_headers)}): {res.detected_headers}")
            print(f"Standardized Product JSON files saved to: {OUTPUT_DIR}")
    else:
        print(f"Sample CSV dataset file not found at: {sample_csv_path}")


