"""
Module 4 Extracted Attribute & Evidence Models
"""

from enum import Enum
from typing import Optional, Any, List
from pydantic import BaseModel, Field, ConfigDict

class ExtractionMethod(str, Enum):
    PDF_TEXT = "pdf_text"
    PATTERN_REGEX = "pattern_regex"
    TABLE_EXTRACTOR = "table_extractor"
    LLM_EXTRACTION = "llm_extraction"
    NLP_HYBRID = "nlp_hybrid"
    HTML_DOM = "html_dom"

class ExtractedAttribute(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    attribute: str = Field(description="Canonical attribute name e.g. voltage, weight, power")
    raw_attribute_name: Optional[str] = Field(default=None, description="Raw label extracted from source e.g. Input Voltage")
    value: Any = Field(description="Extracted value string or number e.g. 380-480")
    unit: Optional[str] = Field(default=None, description="Extracted unit e.g. V, kW, kg, mm")
    source_id: str = Field(description="ID of source where attribute was found")
    page: Optional[int] = Field(default=None, description="Page number if applicable")
    section: Optional[str] = Field(default=None, description="Section heading where found")
    evidence_text: str = Field(description="Exact snippet or sentence serving as evidence")
    extraction_method: ExtractionMethod = Field(default=ExtractionMethod.PATTERN_REGEX)
    extraction_confidence: float = Field(
        default=0.9,
        ge=0.0,
        le=1.0,
        description="Confidence that extraction accurately represents source content"
    )
    category: Optional[str] = Field(default=None, description="Product category context e.g. Industrial Drives")

class ExtractorEvidenceResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    extractor_data: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)

class EvidenceContainer(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    pattern_extractor: ExtractorEvidenceResult = Field(default_factory=ExtractorEvidenceResult)
    table_extractor: ExtractorEvidenceResult = Field(default_factory=ExtractorEvidenceResult)
    url_extractor: ExtractorEvidenceResult = Field(default_factory=ExtractorEvidenceResult)
    llm_extractor: ExtractorEvidenceResult = Field(default_factory=ExtractorEvidenceResult)
