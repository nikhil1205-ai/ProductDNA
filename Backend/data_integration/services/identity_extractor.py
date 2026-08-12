import re
from typing import Dict, Any, Optional

# List of known industrial & technology brands for deterministic keyword matching
KNOWN_BRANDS = [
    "ABB", "SKF", "Schneider Electric", "Schneider", "Siemens", "Allen-Bradley",
    "Allen Bradley", "Omron", "Bosch", "Eaton", "Mitsubishi", "Honeywell",
    "Danfoss", "Fluke", "Festo", "Parker", "Yokogawa", "Emerson", "Rockwell",
    "General Electric", "GE", "Texas Instruments", "STMicroelectronics", "Endress+Hauser",
    "Phoenix Contact", "Wago", "Weidmuller", "Keyence", "Sick", "Turck"
]

def extract_identity_from_dict(data: Dict[str, Any]) -> Dict[str, Optional[str]]:
    """
    Extract identity from structured JSON keys (case-insensitive matching).
    """
    normalized_keys = {str(k).lower().replace(" ", "_").replace("-", "_"): v for k, v in data.items()}

    def get_val(*key_options: str) -> Optional[str]:
        for opt in key_options:
            val = normalized_keys.get(opt)
            if val is not None and str(val).strip():
                return str(val).strip()
        return None

    product_name = get_val("product_name", "productname", "title", "name", "item_name", "description")
    brand = get_val("brand", "brand_name", "make", "vendor")
    manufacturer = get_val("manufacturer", "manufacturer_name", "mfr")
    model = get_val("model", "model_number", "model_no", "model_code", "series")
    sku = get_val("sku", "sku_id", "product_sku", "item_sku")
    part_number = get_val("part_number", "part_no", "mpn", "part_num", "catalog_number", "part_code")

    # Cross fill brand and manufacturer if one is missing
    if not brand and manufacturer:
        brand = manufacturer
    elif not manufacturer and brand:
        manufacturer = brand

    return {
        "product_name": product_name,
        "brand": brand,
        "manufacturer": manufacturer,
        "model": model,
        "sku": sku,
        "part_number": part_number
    }

def extract_identity_from_text(text: Optional[str], title: Optional[str] = None) -> Dict[str, Optional[str]]:
    """
    Extract basic product identity deterministically from raw text using regex patterns and keyword matching.
    Returns null for any field that cannot be reliably detected.
    """
    if not text and not title:
        return {
            "product_name": None,
            "brand": None,
            "manufacturer": None,
            "model": None,
            "sku": None,
            "part_number": None
        }

    combined_text = f"{title or ''}\n{text or ''}"

    product_name: Optional[str] = None
    brand: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    sku: Optional[str] = None
    part_number: Optional[str] = None

    # 1. Regex matching for explicit key-value labels
    brand_match = re.search(r'(?:Brand|Make|Vendor)\s*[:=\-]\s*([A-Za-z0-9\s&\.\-]+?)(?=\n|,|;|\s{2,}|$)', combined_text, re.IGNORECASE)
    if brand_match:
        brand = brand_match.group(1).strip()

    mfr_match = re.search(r'(?:Manufacturer|Mfr)\s*[:=\-]\s*([A-Za-z0-9\s&\.\-]+?)(?=\n|,|;|\s{2,}|$)', combined_text, re.IGNORECASE)
    if mfr_match:
        manufacturer = mfr_match.group(1).strip()

    model_match = re.search(r'(?:Model|Series|Model\s*(?:No|Number|\#))\s*[:=\-]\s*([A-Za-z0-9\-\/\.]+?)(?=\n|,|;|\s{2,}|$)', combined_text, re.IGNORECASE)
    if model_match:
        model = model_match.group(1).strip()

    sku_match = re.search(r'(?:SKU|Catalog\s*(?:No|Number|\#))\s*[:=\-]\s*([A-Za-z0-9\-\/\.]+?)(?=\n|,|;|\s{2,}|$)', combined_text, re.IGNORECASE)
    if sku_match:
        sku = sku_match.group(1).strip()

    part_match = re.search(r'(?:Part\s*(?:No|Number|\#)|MPN|P/N)\s*[:=\-]\s*([A-Za-z0-9\-\/\.]+?)(?=\n|,|;|\s{2,}|$)', combined_text, re.IGNORECASE)
    if part_match:
        part_number = part_match.group(1).strip()

    name_match = re.search(r'(?:Product\s*Name|Product|Title)\s*[:=\-]\s*([^\n,;]+)', combined_text, re.IGNORECASE)
    if name_match:
        product_name = name_match.group(1).strip()

    # 2. Known brand keyword fallback matching
    if not brand and not manufacturer:
        for b_candidate in KNOWN_BRANDS:
            pattern = r'\b' + re.escape(b_candidate) + r'\b'
            if re.search(pattern, combined_text, re.IGNORECASE):
                brand = b_candidate
                manufacturer = b_candidate
                break

    # 3. Model / SKU regex pattern heuristics (e.g. ACS880-01-145A-3, 6205-2RSH, ATV320U15N4B)
    if not model:
        model_pattern_match = re.search(r'\b([A-Z]{2,5}\d{2,4}[A-Z0-9\-]*)\b', combined_text)
        if model_pattern_match:
            candidate_model = model_pattern_match.group(1)
            # Ensure it's not a plain word
            if any(char.isdigit() for char in candidate_model):
                model = candidate_model

    if not sku:
        sku_pattern_match = re.search(r'\b(SKU[:\s\-]*[A-Za-z0-9\-]{4,18}|[0-9]{4,8}-[0-9A-Z]{2,6})\b', combined_text, re.IGNORECASE)
        if sku_pattern_match:
            sku = sku_pattern_match.group(1).replace("SKU:", "").replace("SKU", "").strip()

    # 4. Product Name heuristic determination
    if not product_name:
        if title and title.strip():
            product_name = title.strip()
        else:
            # Use first non-empty line of text if reasonably concise
            lines = [line.strip() for line in (text or '').splitlines() if line.strip()]
            if lines:
                first_line = lines[0]
                if len(first_line) <= 120:
                    product_name = first_line

    if not brand and manufacturer:
        brand = manufacturer
    elif not manufacturer and brand:
        manufacturer = brand

    return {
        "product_name": product_name,
        "brand": brand,
        "manufacturer": manufacturer,
        "model": model,
        "sku": sku,
        "part_number": part_number
    }

def extract_identity(
    input_type: str,
    content: Dict[str, Any],
    raw_input_text: Optional[str] = None
) -> Dict[str, Optional[str]]:
    """
    Main identity extraction router based on input type.
    """
    # 1. Structured JSON content
    if input_type == "JSON" and content.get("structured_data"):
        dict_identity = extract_identity_from_dict(content["structured_data"])
        # If product name or brand is missing, attempt text extraction on summary text
        text_identity = extract_identity_from_text(content.get("text"))
        return {
            "product_name": dict_identity.get("product_name") or text_identity.get("product_name"),
            "brand": dict_identity.get("brand") or text_identity.get("brand"),
            "manufacturer": dict_identity.get("manufacturer") or text_identity.get("manufacturer"),
            "model": dict_identity.get("model") or text_identity.get("model"),
            "sku": dict_identity.get("sku") or text_identity.get("sku"),
            "part_number": dict_identity.get("part_number") or text_identity.get("part_number"),
        }

    # 2. CSV content (first row or headers)
    if input_type == "CSV" and content.get("rows"):
        first_row = content["rows"][0]
        row_identity = extract_identity_from_dict(first_row)
        text_identity = extract_identity_from_text(content.get("summary_text"))
        return {
            "product_name": row_identity.get("product_name") or text_identity.get("product_name"),
            "brand": row_identity.get("brand") or text_identity.get("brand"),
            "manufacturer": row_identity.get("manufacturer") or text_identity.get("manufacturer"),
            "model": row_identity.get("model") or text_identity.get("model"),
            "sku": row_identity.get("sku") or text_identity.get("sku"),
            "part_number": row_identity.get("part_number") or text_identity.get("part_number"),
        }

    # 3. PDF, URL, or PRODUCT_NAME raw text
    text_to_analyze = content.get("text") or raw_input_text or ""
    title_to_analyze = content.get("title")
    return extract_identity_from_text(text_to_analyze, title=title_to_analyze)
