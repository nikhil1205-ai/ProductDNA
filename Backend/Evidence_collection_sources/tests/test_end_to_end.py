"""
End-to-End Integration Tests for Module 4 Evidence Collection & Structured Extraction Engine
"""

import pytest
import fitz  # PyMuPDF
from Evidence_collection_sources.services.evidence_extraction_service import EvidenceExtractionService
from Evidence_collection_sources.models.response_models import StructuredEvidence

def create_abb_pdf_bytes() -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (50, 50),
        "ABB ACS880 Industrial Drive Datasheet\n"
        "Manufacturer: ABB\n"
        "Model: ACS880-01-145A-3\n"
        "SKU: ACS880-01-145A-3\n"
        "Input voltage: 380-480 V\n"
        "Rated power: 75 kW\n"
        "Rated current: 145 A\n"
        "Mains frequency: 50/60 Hz\n"
        "Enclosure class: IP21\n"
        "The drive is designed for pumps, fans and conveyors."
    )
    bytes_out = doc.tobytes()
    doc.close()
    return bytes_out

def test_abb_acs880_end_to_end():
    service = EvidenceExtractionService()
    pdf_bytes = create_abb_pdf_bytes()

    # Input payload representing Module 2 AMBIGUOUS resolution
    module2_input = {
        "request_id": "REQ-20260816-5D846135",
        "identity": {
            "product_name": "ABB ACS880 Industrial Drive",
            "brand": "ABB",
            "manufacturer": "ABB",
            "model": "ACS880",
            "sku": "ACS880-01-145A-3",
            "category": "Industrial Drives"
        },
        "status": "AMBIGUOUS",
        "sources": [
            {
                "type": "pdf",
                "value": "acs880_datasheet.pdf",
                "name": "ACS880 Datasheet",
                "file_bytes": pdf_bytes
            },
            {
                "type": "text",
                "value": "Technical Notes: Mains frequency: 50/60 Hz. Wall-mounted drive.",
                "name": "technical_notes.txt"
            }
        ]
    }

    result = service.process(module2_input)

    assert isinstance(result, StructuredEvidence)
    assert result.request_id == "REQ-20260816-5D846135"
    assert result.product_identity.product_name == "ABB ACS880 Industrial Drive"
    assert len(result.sources) == 2
    assert result.processing_summary.sources_processed == 2
    assert result.processing_summary.attributes_extracted > 0
    assert result.status == "SUCCESS"

    # Check extracted attribute provenance
    attributes = {a.attribute: a for a in result.attributes}
    assert "voltage" in attributes
    assert attributes["voltage"].value == "380-480"
    assert attributes["voltage"].unit == "V"
    assert attributes["voltage"].source_id == "SRC-001"
    assert attributes["voltage"].page == 1
    assert "Input voltage: 380-480 V" in attributes["voltage"].evidence_text

def test_duplicate_source_handling():
    service = EvidenceExtractionService()
    pdf_bytes = create_abb_pdf_bytes()

    payload = {
        "request_id": "REQ-DUP-TEST",
        "identity": {"product_name": "ABB ACS880"},
        "sources": [
            {"type": "pdf", "value": "doc1.pdf", "file_bytes": pdf_bytes},
            {"type": "pdf", "value": "doc2.pdf", "file_bytes": pdf_bytes}  # Identical content
        ]
    }

    result = service.process(payload)
    assert len(result.sources) == 2
    assert result.sources[0].status.value == "processed"
    assert result.sources[1].status.value == "duplicate"
    assert len(result.processing_summary.warnings) > 0
