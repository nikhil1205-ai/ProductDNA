"""
Module 4 PDF Collector
"""

import os
import hashlib
from pathlib import Path
import fitz  # PyMuPDF

from .base import BaseSourceCollector
from ..models.source_models import SourceInput, Source, SourceMetadata, SourceType, SourceStatus, SourceOrigin

class PDFCollector(BaseSourceCollector):
    """
    Intake collector for PDF document sources.
    Handles file path or file bytes, checksum, and initial PDF metadata inspection.
    """
    
    def collect(self, source_input: SourceInput, source_id: str) -> Source:
        pdf_bytes = source_input.file_bytes
        filename = source_input.name or "document.pdf"
        
        # If value is a file path and file_bytes is None
        if not pdf_bytes and source_input.value:
            path = Path(source_input.value)
            if path.is_file():
                filename = path.name
                try:
                    pdf_bytes = path.read_bytes()
                    source_input.file_bytes = pdf_bytes
                except Exception as e:
                    return Source(
                        source_id=source_id,
                        source_type=SourceType.PDF,
                        source_subtype=source_input.subtype or "technical_datasheet",
                        source_name=filename,
                        origin=SourceOrigin.USER_PROVIDED,
                        status=SourceStatus.FAILED,
                        error_message=f"Failed to read PDF file '{path}': {str(e)}",
                        metadata=SourceMetadata(filename=filename)
                    )
            else:
                return Source(
                    source_id=source_id,
                    source_type=SourceType.PDF,
                    source_subtype=source_input.subtype or "technical_datasheet",
                    source_name=filename,
                    origin=SourceOrigin.USER_PROVIDED,
                    status=SourceStatus.FAILED,
                    error_message=f"PDF file not found at path: {source_input.value}",
                    metadata=SourceMetadata(filename=filename)
                )

        if not pdf_bytes:
            return Source(
                source_id=source_id,
                source_type=SourceType.PDF,
                source_subtype=source_input.subtype or "technical_datasheet",
                source_name=filename,
                origin=SourceOrigin.USER_PROVIDED,
                status=SourceStatus.FAILED,
                error_message="Empty PDF content provided.",
                metadata=SourceMetadata(filename=filename)
            )

        # Compute checksum
        content_hash = hashlib.sha256(pdf_bytes).hexdigest()
        size_bytes = len(pdf_bytes)

        # Inspect PDF metadata using PyMuPDF
        page_count = None
        doc_title = None
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            page_count = doc.page_count
            meta = doc.metadata or {}
            doc_title = meta.get("title") or None
            doc.close()
        except Exception as e:
            return Source(
                source_id=source_id,
                source_type=SourceType.PDF,
                source_subtype=source_input.subtype or "technical_datasheet",
                source_name=filename,
                origin=SourceOrigin.USER_PROVIDED,
                status=SourceStatus.FAILED,
                error_message=f"Corrupted or unreadable PDF: {str(e)}",
                metadata=SourceMetadata(
                    filename=filename,
                    content_type="application/pdf",
                    size_bytes=size_bytes,
                    content_hash=content_hash
                )
            )

        metadata = SourceMetadata(
            filename=filename,
            content_type="application/pdf",
            size_bytes=size_bytes,
            content_hash=content_hash,
            title=doc_title,
            page_count=page_count
        )

        return Source(
            source_id=source_id,
            source_type=SourceType.PDF,
            source_subtype=source_input.subtype or "technical_datasheet",
            source_name=filename,
            origin=SourceOrigin.USER_PROVIDED,
            status=SourceStatus.RECEIVED,
            metadata=metadata
        )
