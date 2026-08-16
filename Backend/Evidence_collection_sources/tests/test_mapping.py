"""
Unit Tests for Canonical Attribute Mapping
"""

import pytest
from Evidence_collection_sources.mapping.attribute_mapper import AttributeMapper

def test_voltage_synonyms():
    assert AttributeMapper.map_attribute("Input Voltage") == "voltage"
    assert AttributeMapper.map_attribute("Supply Voltage (V)") == "voltage"
    assert AttributeMapper.map_attribute("Mains Voltage:") == "voltage"

def test_power_current_synonyms():
    assert AttributeMapper.map_attribute("Rated Power") == "power"
    assert AttributeMapper.map_attribute("Motor Power Output") == "power"
    assert AttributeMapper.map_attribute("Rated Current") == "current"

def test_bearing_synonyms():
    assert AttributeMapper.map_attribute("Bore Diameter") == "bore_diameter"
    assert AttributeMapper.map_attribute("Outer Diameter") == "outer_diameter"
    assert AttributeMapper.map_attribute("Limiting Speed") == "limiting_speed"

def test_fallback_snake_case():
    assert AttributeMapper.map_attribute("Custom Special Feature") == "custom_special_feature"
