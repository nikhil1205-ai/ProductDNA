from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ResolutionData(BaseModel):
    status: str = Field(..., description="RESOLVED, AMBIGUOUS, UNRESOLVED")
    match_type: str = Field(..., description="EXACT_SKU, EXACT_PART_NUMBER, MANUFACTURER_MODEL, ALIAS, NO_MATCH")
    confidence: float = Field(..., description="Score from 0.0 to 1.0")
    product_id: Optional[str] = Field(None, description="Resolved Product ID")

class ProductIdentity(BaseModel):
    product_name: Optional[str] = None
    brand: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    sku: Optional[str] = None
    part_number: Optional[str] = None

class StandardProductInput(BaseModel):
    request_id: str
    input_type: str
    identity: ProductIdentity
    metadata: Dict[str, Any]
    content: Dict[str, Any]
    status: str
    resolution_data: Optional[ResolutionData] = None
