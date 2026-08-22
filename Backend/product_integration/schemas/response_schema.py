from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ProductIdentity(BaseModel):
    product_name: Optional[str] = Field(None, description="Extracted product name")
    brand: Optional[str] = Field(None, description="Extracted brand name")
    manufacturer: Optional[str] = Field(None, description="Extracted manufacturer name")
    model: Optional[str] = Field(None, description="Extracted model code/number")
    sku: Optional[str] = Field(None, description="Extracted SKU identifier")
    part_number: Optional[str] = Field(None, description="Extracted part number")

class ProductMetadata(BaseModel):
    filename: Optional[str] = Field(None, description="Source file name if uploaded file")
    extension: Optional[str] = Field(None, description="File extension e.g. .pdf, .csv")
    mime_type: Optional[str] = Field(None, description="MIME content type")
    size_bytes: Optional[int] = Field(None, description="File size in bytes")
    created_at: Optional[str] = Field(None, description="ISO timestamp when metadata created")
    checksum: Optional[str] = Field(None, description="SHA-256 hash of file content")
    source_url: Optional[str] = Field(None, description="URL source if URL input")
    retrieved_at: Optional[str] = Field(None, description="ISO timestamp when URL retrieved")

class ProductContent(BaseModel):
    text: Optional[str] = Field(None, description="Extracted raw text content")
    title: Optional[str] = Field(None, description="Extracted title e.g. webpage title")
    tables: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Extracted tabular data")
    structured_data: Optional[Dict[str, Any]] = Field(None, description="Preserved structured JSON data")
    page_count: Optional[int] = Field(None, description="PDF page count if applicable")
    row_count: Optional[int] = Field(None, description="CSV row count if applicable")
    column_count: Optional[int] = Field(None, description="CSV column count if applicable")

class SourceRecord(BaseModel):
    row_number: Optional[int] = Field(None, description="1-based row index from source dataset")
    raw: Dict[str, Any] = Field(default_factory=dict, description="Complete original row key-value data")
    normalized: Dict[str, Any] = Field(default_factory=dict, description="Row data with placeholders mapped to null")

class StandardProductInput(BaseModel):
    request_id: str = Field(..., description="Unique request identifier REQ-...")
    input_type: str = Field(..., description="Input type: PDF, CSV, URL, JSON, PRODUCT_NAME")
    identity: ProductIdentity = Field(..., description="Extracted product identity fields")
    source_record: Optional[SourceRecord] = Field(None, description="Raw vs normalized source record for tabular datasets")
    metadata: ProductMetadata = Field(..., description="Technical and source metadata")
    content: ProductContent = Field(..., description="Extracted content payload")
    status: str = Field("READY_FOR_RESOLUTION", description="Processing status for Module 2")
    resolution_data: Optional[Dict[str, Any]] = Field(None, description="Output from Module 2 Product Resolution")

class StandardBatchResponse(BaseModel):
    status: str = Field("SUCCESS", description="Batch execution status")
    total_rows: int = Field(0, description="Total rows in CSV dataset")
    processed_count: int = Field(0, description="Successfully processed row count")
    successful_count: int = Field(0, description="Successful row count")
    failed_count: int = Field(0, description="Failed row count")
    detected_headers: List[str] = Field(default_factory=list, description="Headers detected in CSV")
    filename: Optional[str] = Field(None, description="Uploaded CSV filename")
    items: List[StandardProductInput] = Field(default_factory=list, description="List of standard product input records")

class StandardErrorResponse(BaseModel):
    status: str = Field("ERROR", description="Status code string")
    error: str = Field(..., description="Human-readable error explanation")

