"""
Comprehensive Module 3 Evidence Extraction Test Suite
Covers all 10 required architectural and extraction tests against the strict output schema.
"""

import pytest
from unittest.mock import MagicMock, patch

from Evidence_collection_sources_module_2.models.source_models import SourceInput, SourceType
from Evidence_extraction_module_3.services.evidence_extraction_service import EvidenceExtractionService
from Evidence_extraction_module_3.models.extraction_models import EvidenceType, ExtractionMethod
from Evidence_extraction_module_3.extractors.identifier_extractor import IdentifierExtractor
from Evidence_extraction_module_3.extractors.pattern_extractor import PatternExtractor
from Evidence_extraction_module_3.extractors.table_extractor import TableExtractor
from Evidence_extraction_module_3.extractors.llm_extractor import LLMExtractor, LLMExtractionProviderImpl
from Evidence_extraction_module_3.models.document_models import Document, TextBlock, Table, LocationInfo

@pytest.fixture
def service():
    return EvidenceExtractionService()

# -----------------------------------------------------------------------------
# Test 1 — Prose: Preserves source statement verbatim, NOT canonical Storage = 250 GB
# -----------------------------------------------------------------------------
def test_1_prose_preserves_raw_sentence(service):
    payload = {
        "product_id": "PROD-101",
        "sources": [
            {
                "type": "text",
                "value": "This phone has 250 GB storage.",
                "name": "Phone Spec"
            }
        ]
    }
    
    result = service.process(payload)
    
    assert result.status == "EXTRACTED"
    assert "PROD-101" == result.product_id
    
    text_data = result.evidence_data.get("text", {}).get("data", [])
    assert "This phone has 250 GB storage." in text_data
    assert "Storage = 250 GB" not in text_data

# -----------------------------------------------------------------------------
# Test 2 — Complex sentence: Preserves complex sentence without canonical attribute conversion
# -----------------------------------------------------------------------------
def test_2_complex_sentence_preserved(service):
    complex_text = "The rugged device continues to operate reliably in temperatures ranging from -20°C to 60°C."
    payload = {
        "product_id": "PROD-102",
        "sources": [
            {
                "type": "text",
                "value": complex_text,
                "name": "Rugged Phone Spec"
            }
        ]
    }
    
    result = service.process(payload)
    text_data = result.evidence_data.get("text", {}).get("data", [])
    
    assert complex_text in text_data
    assert "Operating Temperature = -20°C to 60°C" not in text_data

# -----------------------------------------------------------------------------
# Test 3 — Table: Tabular row converted into structured table evidence
# -----------------------------------------------------------------------------
def test_3_table_row_extraction(service):
    csv_content = "Specification,Value\nStorage,250 GB\nRAM,8 GB\nVoltage,24 VDC"
    payload = {
        "product_id": "PROD-103",
        "sources": [
            {
                "type": "text",
                "value": csv_content,
                "name": "specs.csv",
                "subtype": "csv"
            }
        ]
    }
    
    result = service.process(payload)
    text_data = result.evidence_data.get("text", {}).get("data", [])
    
    assert any("Storage: 250 GB" in d for d in text_data)
    assert any("RAM: 8 GB" in d for d in text_data)
    assert any("Voltage: 24 VDC" in d for d in text_data)

# -----------------------------------------------------------------------------
# Test 4 — Identifier: Explicit part numbers / SKU / GTIN extracted deterministically
# -----------------------------------------------------------------------------
def test_4_identifier_extraction(service):
    doc_text = "Manufacturer Part Number: ABC-1234\nSKU: SKU-99081\nModel Number: MOD-X500"
    payload = {
        "product_id": "PROD-104",
        "sources": [
            {
                "type": "text",
                "value": doc_text,
                "name": "Identifiers Doc"
            }
        ]
    }
    
    result = service.process(payload)
    text_data = result.evidence_data.get("text", {}).get("data", [])
    
    assert any("Manufacturer Part Number: ABC-1234" in d for d in text_data)
    assert any("SKU: SKU-99081" in d for d in text_data)
    assert any("Model Number: MOD-X500" in d for d in text_data)

# -----------------------------------------------------------------------------
# Test 5 — PDF Provenance: Page numbers are retained internally in extractor items
# -----------------------------------------------------------------------------
def test_5_pdf_provenance_page_number():
    doc = Document(
        document_id="DOC-001",
        source_id="SRC-001",
        text_blocks=[
            TextBlock(
                block_id="BLK-1",
                source_id="SRC-001",
                text="Manufacturer Part Number: XYZ-999",
                location=LocationInfo(page=4, section="Specifications")
            )
        ],
        raw_text="Manufacturer Part Number: XYZ-999",
        metadata={"source_type": "pdf"}
    )
    
    extractor = IdentifierExtractor()
    items = extractor.extract(doc)
    
    assert len(items) == 1
    assert items[0].page_number == 4
    assert items[0].source_type == "pdf"
    assert items[0].section == "Specifications"

# -----------------------------------------------------------------------------
# Test 6 — HTML Cleaning: Navigation, scripts, and footer noise removed
# -----------------------------------------------------------------------------
def test_6_html_noise_removal(service):
    html_content = """
    <html>
      <head><title>Product Specs</title></head>
      <body>
        <nav><a href="/home">Home</a><a href="/cart">Cart</a></nav>
        <div class="cookie-banner">Accept cookies to continue</div>
        <h1>Industrial Sensor</h1>
        <p>The sensor operates on 24 VDC power supply.</p>
        <script>console.log("analytics");</script>
        <footer>Copyright 2026. All rights reserved.</footer>
      </body>
    </html>
    """
    payload = {
        "product_id": "PROD-106",
        "sources": [
            {
                "type": "url",
                "value": "http://example.com/product",
                "metadata": {"text_content": html_content}
            }
        ]
    }
    
    result = service.process(payload)
    url_data = [t.lower() for t in result.evidence_data.get("url", {}).get("data", [])]
    
    # Verify core product evidence is present
    assert any("24 vdc" in t for t in url_data)
    
    # Verify noise was removed
    assert not any("accept cookies" in t for t in url_data)
    assert not any("console.log" in t for t in url_data)
    assert not any("all rights reserved" in t for t in url_data)

# -----------------------------------------------------------------------------
# Test 7 — Raw Wording: Evidence text is preserved verbatim and not paraphrased
# -----------------------------------------------------------------------------
def test_7_raw_wording_preserved(service):
    raw_sentence = "This phone has 250 GB storage."
    payload = {
        "product_id": "PROD-107",
        "sources": [
            {
                "type": "text",
                "value": raw_sentence
            }
        ]
    }
    
    result = service.process(payload)
    text_data = result.evidence_data.get("text", {}).get("data", [])
    
    assert raw_sentence in text_data
    assert "Phone provides 250 GB storage capacity." not in text_data

# -----------------------------------------------------------------------------
# Test 8 — No Hallucination: LLM Extractor failsafe rules
# -----------------------------------------------------------------------------
def test_8_llm_extractor_no_hallucination():
    provider = LLMExtractionProviderImpl()
    
    with patch.object(provider, '_call_langchain_api', return_value=["The device operates on 24 VDC input."]):
        sentences = provider.extract_semantic_evidence(
            document_text="The device operates on 24 VDC input.",
            source_id="SRC-001"
        )
        assert len(sentences) == 1
        assert sentences[0] == "The device operates on 24 VDC input."

# -----------------------------------------------------------------------------
# Test 9 — No LLM Availability: Works deterministically without LLM
# -----------------------------------------------------------------------------
def test_9_no_llm_availability_fallback(service):
    with patch("Evidence_extraction_module_3.extractors.llm_extractor.llm_config.gemini_api_key", None):
        payload = {
            "product_id": "PROD-109",
            "sources": [
                {
                    "type": "text",
                    "value": "Manufacturer Part Number: XYZ-100\nStorage: 250 GB"
                }
            ]
        }
        
        result = service.process(payload)
        assert result.status == "EXTRACTED"
        text_data = result.evidence_data.get("text", {}).get("data", [])
        assert len(text_data) >= 2

# -----------------------------------------------------------------------------
# Test 10 — Duplicate Evidence: Repeated document elements deduplicated
# -----------------------------------------------------------------------------
def test_10_duplicate_evidence_handling(service):
    repeated_text = "This phone has 250 GB storage.\nThis phone has 250 GB storage.\nThis phone has 250 GB storage."
    payload = {
        "product_id": "PROD-110",
        "sources": [
            {
                "type": "text",
                "value": repeated_text
            }
        ]
    }
    
    result = service.process(payload)
    text_data = result.evidence_data.get("text", {}).get("data", [])
    
    storage_matches = [t for t in text_data if t == "This phone has 250 GB storage."]
    # Should deduplicate down to 1 instance
    assert len(storage_matches) == 1
