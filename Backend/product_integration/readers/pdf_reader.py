import io
from typing import Dict, Any, List
import fitz  # PyMuPDF
import pdfplumber

def read_pdf(file_bytes: bytes) -> Dict[str, Any]:
    """
    Extract text, page count, and tables from PDF bytes.
    Uses PyMuPDF for fast text extraction and pdfplumber for table extraction.
    """
    if not file_bytes:
        raise ValueError("Empty PDF file provided.")

    text_pages: List[str] = []
    page_count = 0
    tables: List[Dict[str, Any]] = []

    # Use PyMuPDF for text & page count
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        page_count = len(doc)
        for page_idx in range(page_count):
            page = doc.load_page(page_idx)
            page_text = page.get_text("text") or ""
            text_pages.append(page_text.strip())
        doc.close()
    except Exception as e:
        raise ValueError(f"Corrupted or unreadable PDF file: {str(e)}")

    full_text = "\n\n".join([p for p in text_pages if p])

    if not full_text.strip():
        full_text = "[WARNING: Limited or no text extracted from PDF. Pages may contain scanned images without OCR.]"

    # Extract tables using pdfplumber if available
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for i, page in enumerate(pdf.pages):
                extracted_tables = page.extract_tables()
                for t_idx, table in enumerate(extracted_tables):
                    if not table or len(table) < 2:
                        continue
                    # First row as headers, remaining as rows
                    headers = [str(col or f"col_{idx}").strip() for idx, col in enumerate(table[0])]
                    rows = []
                    for row in table[1:]:
                        row_dict = {}
                        for col_idx, cell in enumerate(row):
                            col_name = headers[col_idx] if col_idx < len(headers) else f"col_{col_idx}"
                            row_dict[col_name] = str(cell).strip() if cell is not None else ""
                        rows.append(row_dict)
                    tables.append({
                        "page": i + 1,
                        "table_index": t_idx + 1,
                        "columns": headers,
                        "rows": rows
                    })
    except Exception:
        # Fallback gracefully if pdfplumber table extraction fails
        pass

    return {
        "text": full_text,
        "page_count": page_count,
        "tables": tables
    }
