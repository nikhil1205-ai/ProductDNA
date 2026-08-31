"""
Module 3 Evidence Extraction Router Definitions
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status

from ..models.response_models import StructuredEvidence
from ..services.evidence_extraction_service import EvidenceExtractionService

router = APIRouter(tags=["Evidence Extraction (Module 3)"])
extraction_service = EvidenceExtractionService()

@router.post(
    "/api/evidence/extract",
    response_model=StructuredEvidence,
    summary="Run Downstream Evidence Extraction (Module 3)"
)
async def extract_evidence(payload: Dict[str, Any]):
    """
    Runs downstream evidence extraction on collected resources for a given product request.
    """
    try:
        result = extraction_service.process(payload)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evidence extraction failed: {str(e)}"
        )
