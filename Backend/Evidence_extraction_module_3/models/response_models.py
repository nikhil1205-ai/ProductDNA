"""
Module 3 Output & Request Models
"""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict

from Evidence_collection_sources_module_2.models.source_models import SourceInput

class ProductIdentity(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    brand: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    sku: Optional[str] = None
    part_number: Optional[str] = None
    category: Optional[str] = None

class StructuredEvidence(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    product_id: str = Field(default="PROD-UNKNOWN", description="Canonical or incoming product ID")
    source_ids: List[str] = Field(default_factory=list, description="List of processed source IDs")
    evidence_data: Dict[str, Any] = Field(default_factory=dict, description="Categorized evidence by source/method type")
    status: str = Field(default="EXTRACTED", description="EXTRACTED, PARTIAL, or FAILED")

class Module3Request(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    request_id: Optional[str] = Field(default=None, description="Optional request ID")
    product_id: Optional[str] = Field(default=None, description="Product ID e.g. PROD-001")
    product: Optional[Dict[str, Any]] = Field(default=None, description="Module 1/2 resolved product dictionary or identity")
    sources: List[Union[SourceInput, Dict[str, Any]]] = Field(default_factory=list, description="User-provided sources list")

class Module3Response(StructuredEvidence):
    pass
