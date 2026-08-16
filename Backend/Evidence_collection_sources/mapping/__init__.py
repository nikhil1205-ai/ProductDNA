"""
Module 4 Attribute Mapping Package
"""

from .canonical_attributes import SYNONYM_MAP, CATEGORY_SCHEMAS
from .attribute_mapper import AttributeMapper

__all__ = [
    "SYNONYM_MAP",
    "CATEGORY_SCHEMAS",
    "AttributeMapper"
]
