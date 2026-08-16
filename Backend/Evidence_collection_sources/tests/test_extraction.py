"""
Unit Tests for Attribute Extraction (Regex, Table, LLM/Hybrid)
"""

import pytest
from Evidence_collection_sources.models.document_models import Document, TextBlock, Table, LocationInfo
from Evidence_collection_sources.extractors.pattern_extractor import PatternExtractor
from Evidence_collection_sources.extractors.table_extractor import TableExtractor
from Evidence_collection_sources.extractors.llm_extractor import LLMExtractor

def test_pattern_extractor():
    doc = Document(
        document_id="DOC-001",
        source_id="SRC-001",
        text_blocks=[
            TextBlock(
                block_id="BLK-1",
                source_id="SRC-001",
                text="Input voltage: 380-480 V\nRated power: 75 kW\nRated current: 145 A\nProtection: IP55",
                location=LocationInfo(page=1, section="Specs")
            )
        ]
    )
    
    extractor = PatternExtractor()
    attrs = extractor.extract(doc)

    assert len(attrs) >= 4
    attr_dict = {a.attribute: (a.value, a.unit) for a in attrs}
    
    assert "voltage" in attr_dict
    assert attr_dict["voltage"] == ("380-480", "V")
    assert "power" in attr_dict
    assert attr_dict["power"] == ("75", "kW")
    assert "current" in attr_dict
    assert attr_dict["current"] == ("145", "A")

def test_table_extractor():
    doc = Document(
        document_id="DOC-002",
        source_id="SRC-002",
        tables=[
            Table(
                table_id="TBL-1",
                source_id="SRC-002",
                kv_pairs={
                    "Bore Diameter": "25 mm",
                    "Outer Diameter": "52 mm",
                    "Limiting Speed": "14000 rpm"
                },
                location=LocationInfo(page=2)
            )
        ]
    )

    extractor = TableExtractor()
    attrs = extractor.extract(doc)

    assert len(attrs) == 3
    attr_names = [a.attribute for a in attrs]
    assert "bore_diameter" in attr_names
    assert "outer_diameter" in attr_names
    assert "limiting_speed" in attr_names

def test_llm_hybrid_fallback():
    doc = Document(
        document_id="DOC-003",
        source_id="SRC-003",
        raw_text="The drive is designed for pumps, fans and conveyors. Enclosure type is wall-mounted."
    )

    extractor = LLMExtractor()
    attrs = extractor.extract(doc)

    assert len(attrs) > 0
    attr_names = [a.attribute for a in attrs]
    assert "applications" in attr_names or "mounting_type" in attr_names
