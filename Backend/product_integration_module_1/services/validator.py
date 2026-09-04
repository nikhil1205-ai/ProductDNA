import os
import re
from typing import Dict, Any, Optional, Tuple, Union

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB limit
SUPPORTED_FILE_EXTENSIONS = {".pdf", ".csv"}

def validate_file_input(filename: str, file_bytes: bytes) -> Tuple[str, str]:
    """
    Validate uploaded file input. Returns (extension, detected_type).
    """
    if not filename:
        raise ValueError("Filename is missing from upload request.")

    if not file_bytes or len(file_bytes) == 0:
        raise ValueError(f"Uploaded file '{filename}' is empty (0 bytes).")

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise ValueError(f"File size ({len(file_bytes)} bytes) exceeds maximum limit of {MAX_FILE_SIZE_BYTES} bytes (50MB).")

    _, ext = os.path.splitext(filename.lower())
    if ext not in SUPPORTED_FILE_EXTENSIONS:
        raise ValueError(f"Unsupported file extension '{ext}'. Supported file types are: {', '.join(sorted(SUPPORTED_FILE_EXTENSIONS))}")

    detected_type = "PDF" if ext == ".pdf" else "CSV"
    return ext, detected_type

def validate_url_input(url_str: str) -> str:
    """
    Validate URL string format.
    """
    if not url_str or not url_str.strip():
        raise ValueError("URL string cannot be empty.")

    cleaned_url = url_str.strip()
    url_pattern = re.compile(r'^https?://[^\s/$.?#].[^\s]*$', re.IGNORECASE)

    if not url_pattern.match(cleaned_url):
        raise ValueError(f"Invalid URL structure: '{cleaned_url}'. Must begin with http:// or https://")

    return cleaned_url

def validate_json_input(raw_json: Union[str, bytes, dict, list]) -> Any:
    """
    Validate JSON structure or raw JSON string.
    """
    if raw_json is None:
        raise ValueError("JSON input payload is null or empty.")

    if isinstance(raw_json, (dict, list)):
        if not raw_json:
            raise ValueError("JSON payload contains an empty object or array.")
        return raw_json

    if isinstance(raw_json, (str, bytes)):
        if isinstance(raw_json, bytes):
            try:
                raw_str = raw_json.decode('utf-8')
            except UnicodeDecodeError:
                raise ValueError("JSON byte content is not valid UTF-8 text.")
        else:
            raw_str = raw_json

        if not raw_str.strip():
            raise ValueError("JSON text input cannot be empty.")

        import json
        try:
            return json.loads(raw_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string syntax: {str(e)}")

    raise ValueError("Invalid JSON input type.")

def detect_input_type(
    file_name: Optional[str] = None,
    file_bytes: Optional[bytes] = None,
    url_str: Optional[str] = None,
    json_data: Optional[Any] = None,
    input_text: Optional[str] = None,
    explicit_type: Optional[str] = None
) -> str:
    """
    Detect or confirm the input type (PDF, CSV, URL, JSON, PRODUCT_NAME).
    """
    if explicit_type and explicit_type.upper() in {"PDF", "CSV", "URL", "JSON", "PRODUCT_NAME"}:
        return explicit_type.upper()

    if file_bytes and file_name:
        _, ext = os.path.splitext(file_name.lower())
        if ext == ".pdf":
            return "PDF"
        elif ext == ".csv":
            return "CSV"

    if json_data is not None:
        return "JSON"

    if url_str and (url_str.strip().startswith("http://") or url_str.strip().startswith("https://")):
        return "URL"

    if input_text and input_text.strip():
        text = input_text.strip()
        if text.startswith("http://") or text.startswith("https://"):
            return "URL"
        if (text.startswith("{") and text.endswith("}")) or (text.startswith("[") and text.endswith("]")):
            try:
                import json
                json.loads(text)
                return "JSON"
            except Exception:
                pass
        return "PRODUCT_NAME"

    raise ValueError("Could not determine input type from request parameters.")
