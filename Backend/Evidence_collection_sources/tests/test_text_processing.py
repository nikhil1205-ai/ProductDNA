"""
Unit Tests for Plain Text Document Collection & Processing
"""

import pytest
from Evidence_collection_sources.collectors.text_collector import TextCollector
from Evidence_collection_sources.processors.text_processor import TextProcessor
from Evidence_collection_sources.models.source_models import SourceInput, SourceType, SourceStatus

def test_plain_text_processing():
    text_content = """
# Technical Specifications
Brand: SKF
Model: 6205-2RSH
Bore diameter: 25 mm
Outer diameter: 52 mm
Width: 15 mm
Limiting speed: 14000 r/min
Weight: 0.13 kg
"""
    collector = TextCollector()
    processor = TextProcessor()

    source_input = SourceInput(
        type=SourceType.TEXT,
        value=text_content,
        name="skf_bearing_specs.txt"
    )

    source = collector.collect(source_input, "SRC-001")
    assert source.status == SourceStatus.RECEIVED

    doc = processor.process(source, source_input)
    assert source.status == SourceStatus.PROCESSED
    assert len(doc.text_blocks) > 0
    assert "Bore diameter: 25 mm" in doc.raw_text

def test_empty_text_processing():
    collector = TextCollector()
    source_input = SourceInput(type=SourceType.TEXT, value="   ")
    source = collector.collect(source_input, "SRC-001")

    assert source.status == SourceStatus.FAILED
    assert "Empty text content" in source.error_message
