"""
Unit Tests for PDF Source Collection & Processing
"""

import pytest
import fitz  # PyMuPDF
from Evidence_collection_sources.collectors.pdf_collector import PDFCollector
from Evidence_collection_sources.processors.pdf_processor import PDFProcessor
from Evidence_collection_sources.models.source_models import SourceInput, SourceType, SourceStatus

def create_sample_pdf_bytes() -> bytes:
    """Helper to construct a valid PDF in memory using PyMuPDF."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "ABB ACS880 Industrial Drive Datasheet\nManufacturer: ABB\nModel: ACS880-01-145A-3\nInput voltage: 380-480 V\nRated power: 75 kW\nRated current: 145 A")
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes

def test_valid_pdf_processing():
    pdf_bytes = create_sample_pdf_bytes()
    collector = PDFCollector()
    processor = PDFProcessor()

    source_input = SourceInput(
        type=SourceType.PDF,
        value="sample_abb_datasheet.pdf",
        name="ABB Datasheet",
        file_bytes=pdf_bytes
    )
    
    source = collector.collect(source_input, "SRC-001")
    assert source.status == SourceStatus.RECEIVED
    assert source.metadata.page_count == 1

    doc = processor.process(source, source_input)
    assert source.status == SourceStatus.PROCESSED
    assert len(doc.text_blocks) > 0
    assert doc.text_blocks[0].location.page == 1
    assert "Input voltage: 380-480 V" in doc.raw_text

def test_corrupted_pdf_processing():
    corrupt_bytes = b"%PDF-1.4 Corrupted Invalid Header Structure"
    collector = PDFCollector()

    source_input = SourceInput(
        type=SourceType.PDF,
        value="corrupt.pdf",
        name="Corrupted Document",
        file_bytes=corrupt_bytes
    )
    
    source = collector.collect(source_input, "SRC-001")
    assert source.status == SourceStatus.FAILED
    assert "Corrupted" in source.error_message or "unreadable" in source.error_message
