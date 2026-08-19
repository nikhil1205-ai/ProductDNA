"""
Module 4 PDF Document Content Processor
"""

import fitz  # PyMuPDF
import pdfplumber
import io
from typing import List, Dict

from .base import BaseProcessor
from .content_cleaner import clean_whitespace, remove_duplicate_text_blocks
from ..models.source_models import Source, SourceInput, SourceStatus
from ..models.document_models import Document, Section, TextBlock, Table, LocationInfo

class PDFProcessor(BaseProcessor):
    """
    Processor for PDF files.
    Extracts text blocks with page numbers, page-level sections, and tables using PyMuPDF & pdfplumber.
    """
    
    def process(self, source: Source, source_input: SourceInput) -> Document:
        pdf_bytes = source_input.file_bytes
        if not pdf_bytes:
            source.status = SourceStatus.FAILED
            source.error_message = "No PDF bytes provided to processor."
            return Document(document_id=f"DOC-{source.source_id}", source_id=source.source_id)

        text_blocks: List[TextBlock] = []
        tables: List[Table] = []
        full_text_parts: List[str] = []
        
        block_idx = 1
        table_idx = 1
        current_section = "Document Overview"

        # 1. Extract page-level text blocks using PyMuPDF
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            for page_num in range(1, doc.page_count + 1):
                page = doc.load_page(page_num - 1)
                page_text = page.get_text("text") or ""
                
                if page_text.strip():
                    full_text_parts.append(f"--- Page {page_num} ---\n{page_text}")
                    
                    # Split page into blocks / lines
                    paragraphs = page_text.split("\n\n")
                    for para in paragraphs:
                        cleaned = clean_whitespace(para)
                        if not cleaned or len(cleaned) < 3:
                            continue
                            
                        # Detect section headings (short lines in title case or uppercase)
                        first_line = cleaned.split("\n")[0].strip()
                        if len(first_line) < 60 and (first_line.isupper() or first_line.istitle() or ":" in first_line):
                            current_section = first_line

                        text_blocks.append(
                            TextBlock(
                                block_id=f"BLK-{source.source_id}-{block_idx}",
                                source_id=source.source_id,
                                text=cleaned,
                                location=LocationInfo(page=page_num, section=current_section),
                                block_type="paragraph"
                            )
                        )
                        block_idx += 1
            doc.close()
        except Exception as e:
            source.status = SourceStatus.FAILED
            source.error_message = f"Failed PyMuPDF processing: {str(e)}"

        # 2. Extract tables using pdfplumber
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page_idx, page in enumerate(pdf.pages, start=1):
                    extracted_tables = page.extract_tables()
                    for raw_tbl in extracted_tables:
                        if not raw_tbl:
                            continue
                            
                        headers = []
                        rows = []
                        kv_pairs: Dict[str, str] = {}
                        
                        # Process table rows
                        cleaned_tbl = [[str(cell or "").strip() for cell in row] for row in raw_tbl if any(row)]
                        if not cleaned_tbl:
                            continue
                            
                        # Determine if first row is header
                        if len(cleaned_tbl) > 1:
                            headers = cleaned_tbl[0]
                            rows = cleaned_tbl[1:]
                        else:
                            rows = cleaned_tbl

                        for r in rows:
                            if len(r) >= 2 and r[0] and r[1]:
                                kv_pairs[r[0]] = r[1]

                        tables.append(
                            Table(
                                table_id=f"TBL-{source.source_id}-{table_idx}",
                                source_id=source.source_id,
                                title=f"Table {table_idx} (Page {page_idx})",
                                headers=headers,
                                rows=rows,
                                kv_pairs=kv_pairs,
                                location=LocationInfo(page=page_idx, table_index=table_idx)
                            )
                        )
                        table_idx += 1
        except Exception as e:
            # Table extraction failure is not fatal if text was extracted
            pass

        # Check if text was extracted
        full_text = "\n\n".join(full_text_parts)
        if not full_text.strip():
            source.status = SourceStatus.FAILED
            source.error_message = "PDF_TEXT_EXTRACTION_FAILED: Scanned or image-only PDF without OCR text."
            return Document(
                document_id=f"DOC-{source.source_id}",
                source_id=source.source_id,
                title=source.source_name,
                text_blocks=[],
                tables=[],
                raw_text=""
            )

        unique_blocks = remove_duplicate_text_blocks(text_blocks)
        source.status = SourceStatus.PROCESSED

        return Document(
            document_id=f"DOC-{source.source_id}",
            source_id=source.source_id,
            title=source.source_name,
            text_blocks=unique_blocks,
            tables=tables,
            raw_text=full_text,
            metadata={"source_type": source.source_type, "page_count": len(full_text_parts)}
        )
