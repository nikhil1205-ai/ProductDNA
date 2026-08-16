"""
Module 4 Canonical Attribute Registry & Synonym Mapping Definitions
"""

from typing import Dict, List, Set

# Canonical attribute names mapping dictionary
SYNONYM_MAP: Dict[str, str] = {
    # Voltage
    "voltage": "voltage",
    "input voltage": "voltage",
    "supply voltage": "voltage",
    "mains voltage": "voltage",
    "rated voltage": "voltage",
    "nominal voltage": "voltage",
    "operating voltage": "voltage",
    "voltage range": "voltage",
    "v_in": "voltage",
    "v_rated": "voltage",

    # Current
    "current": "current",
    "input current": "current",
    "rated current": "current",
    "nominal current": "current",
    "mains current": "current",
    "max current": "current",
    "output current": "current",

    # Power
    "power": "power",
    "rated power": "power",
    "motor power": "power",
    "power output": "power",
    "nominal power": "power",
    "output power": "power",
    "capacity": "power",

    # Frequency
    "frequency": "frequency",
    "mains frequency": "frequency",
    "supply frequency": "frequency",
    "operating frequency": "frequency",
    "input frequency": "frequency",

    # Weight
    "weight": "weight",
    "net weight": "weight",
    "mass": "weight",
    "product weight": "weight",
    "gross weight": "weight",
    "shipping weight": "weight",

    # Dimensions
    "dimensions": "dimensions",
    "size": "dimensions",
    "outer dimensions": "dimensions",
    "overall dimensions": "dimensions",
    "enclosure size": "dimensions",
    "height x width x depth": "dimensions",

    # Protection / IP Rating
    "ip rating": "ip_rating",
    "degree of protection": "ip_rating",
    "enclosure class": "ip_rating",
    "protection rating": "ip_rating",
    "ip class": "ip_rating",

    # Efficiency
    "efficiency": "efficiency",
    "efficiency level": "efficiency",
    "ie class": "efficiency",
    "energy efficiency": "efficiency",

    # Temperature
    "operating temperature": "operating_temperature",
    "ambient temperature": "operating_temperature",
    "temperature range": "operating_temperature",
    "temp range": "operating_temperature",

    # Applications
    "applications": "applications",
    "target applications": "applications",
    "suitable for": "applications",
    "use cases": "applications",

    # Bearing specific attributes
    "bore diameter": "bore_diameter",
    "inner diameter": "bore_diameter",
    "d": "bore_diameter",
    "outer diameter": "outer_diameter",
    "d_out": "outer_diameter",
    "width": "width",
    "b": "width",
    "load rating": "load_rating",
    "dynamic load rating": "load_rating",
    "static load rating": "load_rating",
    "speed": "limiting_speed",
    "limiting speed": "limiting_speed",
    "reference speed": "reference_speed",

    # Identifiers
    "sku": "sku",
    "model": "model",
    "model number": "model",
    "part number": "part_number",
    "part_no": "part_number",
    "pn": "part_number",
    "serial number": "serial_number"
}

# Generic Category Schema Registry
CATEGORY_SCHEMAS: Dict[str, List[str]] = {
    "Industrial Drives": [
        "voltage", "frequency", "power", "current", "efficiency",
        "ip_rating", "dimensions", "weight", "operating_temperature", "applications"
    ],
    "Bearings": [
        "bore_diameter", "outer_diameter", "width", "load_rating",
        "limiting_speed", "reference_speed", "weight"
    ],
    "General": [
        "voltage", "power", "current", "dimensions", "weight", "sku", "model", "part_number"
    ]
}
