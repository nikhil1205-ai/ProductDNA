"""
Module 4 Response & Request Models
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict

from .source_models import Source, SourceInput
from .extraction_models import ExtractedAttribute
from .document_models import Document

class ProductIdentity(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    product_name: Optional[str] = None
    brand: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    sku: Optional[str] = None
    part_number: Optional[str] = None
    category: Optional[str] = None

class ProcessingWarning(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    source_id: Optional[str] = None
    warning_code: str
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ProcessingSummary(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    sources_received: int = 0
    sources_processed: int = 0
    attributes_extracted: int = 0
    warnings: List[ProcessingWarning] = Field(default_factory=list)
    processing_time_seconds: float = 0.0

class StructuredEvidence(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    request_id: str
    product_identity: ProductIdentity
    sources: List[Source] = Field(default_factory=list)
    documents: List[Document] = Field(default_factory=list)
    attributes: List[ExtractedAttribute] = Field(default_factory=list)
    processing_summary: ProcessingSummary = Field(default_factory=ProcessingSummary)
    status: str = Field(default="SUCCESS", description="SUCCESS, PARTIAL_SUCCESS, FAILED")

class Module4Request(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    request_id: Optional[str] = Field(default=None, description="Optional request ID; will copy from Module 2 if provided")
    product: Optional[Dict[str, Any]] = Field(default=None, description="Module 2 resolved product dictionary or identity")
    sources: List[SourceInput] = Field(default_factory=list, description="User-provided sources list")

class Module4Response(StructuredEvidence):
    pass
