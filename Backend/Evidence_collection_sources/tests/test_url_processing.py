"""
Unit Tests for URL Source Collection & Processing
"""

import pytest
from unittest.mock import patch, MagicMock
import requests

from Evidence_collection_sources.collectors.url_collector import URLCollector
from Evidence_collection_sources.processors.url_processor import URLProcessor
from Evidence_collection_sources.models.source_models import SourceInput, SourceType, SourceStatus

def test_invalid_url_format():
    collector = URLCollector()
    source_input = SourceInput(type=SourceType.URL, value="not-a-valid-url")
    source = collector.collect(source_input, "SRC-001")
    
    assert source.status == SourceStatus.FAILED
    assert "Invalid URL format" in source.error_message

@patch("requests.get")
def test_valid_url_processing(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.url = "https://example.com/abb-acs880"
    mock_resp.content = b"<html><head><title>ABB ACS880 Specs</title></head><body><h1>ABB ACS880 Drive</h1><p>Input voltage: 380-480 V</p></body></html>"
    mock_resp.headers = {"content-type": "text/html"}
    mock_get.return_value = mock_resp

    collector = URLCollector()
    processor = URLProcessor()

    source_input = SourceInput(type=SourceType.URL, value="https://example.com/abb-acs880")
    source = collector.collect(source_input, "SRC-001")

    assert source.status == SourceStatus.RECEIVED
    assert source.metadata.url == "https://example.com/abb-acs880"

    doc = processor.process(source, source_input)
    assert doc.title == "ABB ACS880 Specs"
    assert len(doc.text_blocks) > 0
    assert "Input voltage: 380-480 V" in doc.raw_text

@patch("requests.get")
def test_url_timeout(mock_get):
    mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")
    collector = URLCollector()
    source_input = SourceInput(type=SourceType.URL, value="https://example.com/timeout")
    source = collector.collect(source_input, "SRC-001")

    assert source.status == SourceStatus.FAILED
    assert "timed out" in source.error_message
