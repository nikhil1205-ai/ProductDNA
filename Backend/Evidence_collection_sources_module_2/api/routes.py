"""
Module 2 Product Resources & Evidence Router Definitions
"""

import json
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query, status

from ..models.source_models import SourceInput, Source, SourceType, SourceStatus
from ..services.resource_manager import ResourceManager

router = APIRouter(tags=["Product Resources & Evidence"])
resource_manager = ResourceManager()

@router.post(
    "/api/resources",
    response_model=Source,
    status_code=status.HTTP_201_CREATED,
    summary="Add a Product Resource (PDF, URL, or Text)"
)
async def add_resource(
    request_id: Optional[str] = Form(None),
    type: Optional[SourceType] = Form(None),
    value: Optional[str] = Form(None),
    name: Optional[str] = Form(None),
    subtype: Optional[str] = Form("technical_document"),
    file: Optional[UploadFile] = File(None)
):
    """
    Intake a product resource (PDF file upload, URL, or raw text),
    collect metadata, compute SHA-256 hash, detect duplicates, and store locally.
    """
    file_bytes = None
    filename = None
    res_type = type or SourceType.TEXT
    target_value = value or ""

    if file:
        filename = file.filename
        try:
            file_bytes = await file.read()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to read uploaded resource file: {str(e)}"
            )

        if not target_value:
            target_value = filename or "uploaded_resource"

        # Determine type from file extension if not explicitly set
        if filename and filename.lower().endswith(".pdf"):
            res_type = SourceType.PDF
        elif filename and (filename.lower().endswith(".txt") or filename.lower().endswith(".md")):
            res_type = SourceType.TEXT

    source_input = SourceInput(
        request_id=request_id or "REQ-001",
        type=res_type,
        value=target_value,
        name=name or filename or target_value,
        subtype=subtype or "technical_document",
        file_bytes=file_bytes
    )

    try:
        source = resource_manager.add_resource(source_input)
        return source
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Resource processing failed: {str(e)}"
        )

@router.get(
    "/api/resources",
    response_model=List[Source],
    summary="List Registered Product Resources"
)
async def list_resources(request_id: Optional[str] = Query(None, description="Filter resources by product request_id")):
    """
    Returns list of all registered resources associated with request_id (or all resources if omitted).
    """
    return resource_manager.list_resources(request_id=request_id)

@router.get(
    "/api/resources/{source_id}",
    response_model=Source,
    summary="Get Resource Details"
)
async def get_resource(source_id: str):
    """
    Retrieves details and status of a single registered resource by source_id.
    """
    source = resource_manager.get_resource(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource '{source_id}' not found."
        )
    return source

@router.delete(
    "/api/resources/{source_id}",
    summary="Delete Product Resource"
)
async def delete_resource(source_id: str):
    """
    Deletes a registered resource record and removes its stored physical file artifacts.
    """
    success = resource_manager.delete_resource(source_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource '{source_id}' not found or could not be deleted."
        )
    return {"status": "SUCCESS", "deleted_source_id": source_id}
