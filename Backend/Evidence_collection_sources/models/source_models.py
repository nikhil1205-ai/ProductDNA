"""
Module 4 Source Models
"""

from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict

class SourceType(str, Enum):
    URL = "url"
    PDF = "pdf"
    TEXT = "text"

class SourceOrigin(str, Enum):
    USER_PROVIDED = "user_provided"
    DISCOVERED = "discovered"

class SourceStatus(str, Enum):
    RECEIVED = "received"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    DUPLICATE = "duplicate"

class SourceMetadata(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    url: Optional[str] = None
    filename: Optional[str] = None
    content_type: Optional[str] = None
    size_bytes: Optional[int] = None
    content_hash: Optional[str] = None
    title: Optional[str] = None
    page_count: Optional[int] = None
    retrieved_at: Optional[str] = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class SourceInput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    type: SourceType = Field(description="Source type: url, pdf, or text")
    value: str = Field(description="URL string, file path, filename, or raw text content")
    name: Optional[str] = Field(default=None, description="Human readable name for source")
    subtype: Optional[str] = Field(default="technical_document", description="Subtype e.g. datasheet, website, notes")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    file_bytes: Optional[bytes] = Field(default=None, exclude=True, description="Optional raw binary content for uploaded files")

class Source(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    source_id: str = Field(description="Unique identifier e.g. SRC-001")
    source_type: SourceType
    source_subtype: str = Field(default="technical_document")
    source_name: str
    origin: SourceOrigin = Field(default=SourceOrigin.USER_PROVIDED)
    status: SourceStatus = Field(default=SourceStatus.RECEIVED)
    metadata: SourceMetadata = Field(default_factory=SourceMetadata)
    error_message: Optional[str] = None
