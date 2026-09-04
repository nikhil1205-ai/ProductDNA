"""
Module 3 Evidence Extraction Models & Provenance Definitions
"""

from enum import Enum
from typing import Optional, Any, List, Dict
from pydantic import BaseModel, Field, ConfigDict

class ExtractionMethod(str, Enum):
    DOCUMENT_PARSER = "document_parser"
    HTML_PARSER = "html_parser"
    TEXT_PARSER = "text_parser"
    PATTERN_EXTRACTOR = "pattern_extractor"
    TABLE_EXTRACTOR = "table_extractor"
    IDENTIFIER_EXTRACTOR = "identifier_extractor"
    LLM = "llm"

class EvidenceType(str, Enum):
    SENTENCE = "sentence"
    LINE = "line"
    HEADING = "heading"
    BULLET = "bullet"
    TABLE_ROW = "table_row"
    IDENTIFIER = "identifier"

class EvidenceItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    evidence_id: str = Field(description="Unique evidence unit ID e.g. EV-001")
    source_id: str = Field(description="ID of the source resource e.g. SRC-001")
    source_type: str = Field(description="Source type: pdf, url, or text")
    evidence_type: EvidenceType = Field(default=EvidenceType.SENTENCE, description="Granularity/type of evidence")
    text: str = Field(description="Exact source-grounded evidence text statement")
    raw_label: Optional[str] = Field(default=None, description="Unmodified raw label if explicit e.g. Manufacturer Part Number")
    raw_value: Optional[str] = Field(default=None, description="Unmodified raw value if explicit e.g. 250 GB")
    page_number: Optional[int] = Field(default=None, description="1-indexed PDF page number or None")
    section: Optional[str] = Field(default=None, description="Section heading context or None")
    line_number: Optional[int] = Field(default=None, description="Line number in document or None")
    table_name: Optional[str] = Field(default=None, description="Table name/title or None")
    row_number: Optional[int] = Field(default=None, description="Row index in table or None")
    extraction_method: ExtractionMethod = Field(default=ExtractionMethod.DOCUMENT_PARSER)

class SourceGroupEvidence(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    data: List[str] = Field(default_factory=list, description="List of raw evidence text strings")
    page_number: Optional[int] = Field(default=None, description="Primary page number if single page, or None")
    extraction_method: str = Field(default="document_parser", description="Extraction method used")
    items: List[EvidenceItem] = Field(default_factory=list, description="Detailed evidence units with rich provenance")
