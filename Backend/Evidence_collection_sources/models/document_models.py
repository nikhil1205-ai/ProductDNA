"""
Module 4 Document Understanding Models
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class LocationInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    page: Optional[int] = Field(default=None, description="1-indexed page number if PDF")
    section: Optional[str] = Field(default=None, description="Section heading title")
    line_start: Optional[int] = Field(default=None)
    line_end: Optional[int] = Field(default=None)
    table_index: Optional[int] = Field(default=None)

class TextBlock(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    block_id: str
    source_id: str
    text: str
    location: LocationInfo = Field(default_factory=LocationInfo)
    block_type: str = Field(default="paragraph", description="paragraph, heading, bullet_item, code")

class Table(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    table_id: str
    source_id: str
    title: Optional[str] = None
    headers: List[str] = Field(default_factory=list)
    rows: List[List[str]] = Field(default_factory=list)
    kv_pairs: Dict[str, str] = Field(default_factory=dict, description="Extracted Key-Value attribute pairs")
    location: LocationInfo = Field(default_factory=LocationInfo)

class Section(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    section_id: str
    source_id: str
    title: str
    text_blocks: List[TextBlock] = Field(default_factory=list)
    tables: List[Table] = Field(default_factory=list)
    location: LocationInfo = Field(default_factory=LocationInfo)

class Document(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    document_id: str
    source_id: str
    title: Optional[str] = None
    sections: List[Section] = Field(default_factory=list)
    text_blocks: List[TextBlock] = Field(default_factory=list)
    tables: List[Table] = Field(default_factory=list)
    raw_text: str = Field(default="", description="Full concatenated text of document")
    metadata: Dict[str, Any] = Field(default_factory=dict)
