from typing import Optional, Dict, Any, Union
from pydantic import BaseModel, Field

class ProductInputRequest(BaseModel):
    """
    API payload for JSON-formatted requests to /api/product-input.
    Supports product_name, url, json_data, or general input_text.
    """
    input_type: Optional[str] = Field(None, description="Explicit input type: PDF, CSV, URL, JSON, PRODUCT_NAME")
    input_text: Optional[str] = Field(None, description="Raw text or URL or product name")
    product_name: Optional[str] = Field(None, description="Explicit product name")
    url: Optional[str] = Field(None, description="Explicit URL to process")
    json_data: Optional[Dict[str, Any]] = Field(None, description="Raw structured JSON object")

    class Config:
        json_schema_extra = {
            "example": {
                "input_type": "PRODUCT_NAME",
                "product_name": "ABB ACS880 Industrial Drive",
                "json_data": {
                    "brand": "ABB",
                    "sku": "ACS880-01-145A-3"
                }
            }
        }
