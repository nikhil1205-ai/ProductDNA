"""
Module 5 — FastAPI Router
POST /api/module5/semantic-interpretation
"""

import logging
from fastapi import APIRouter, HTTPException

from .models import Module5Request, Module5Response
from .service import SemanticInterpretationService

logger = logging.getLogger("module5")

module5_router = APIRouter(prefix="/api/module5", tags=["Module 5 — Semantic Interpretation"])

_service = SemanticInterpretationService()


@module5_router.post(
    "/semantic-interpretation",
    response_model=Module5Response,
    summary="Semantic Interpretation (Module 5)",
    description=(
        "Accepts a selected Module 1 StandardProductInput and optional organization context. "
        "Returns a 252-column candidate delivery record with per-field provenance metadata and "
        "a classification result. All output is marked CANDIDATE and requires Module 6 validation."
    ),
)
async def semantic_interpretation(payload: Module5Request) -> Module5Response:
    logger.info("Module 5 | POST /api/module5/semantic-interpretation received")

    if not payload.product:
        raise HTTPException(status_code=422, detail="'product' field is required and must not be empty.")

    result = _service.interpret(
        product=payload.product,
        organization=payload.organization,
    )

    if result.status == "FAILED" and result.error:
        logger.error("Module 5 | FAILED: %s", result.error)
        raise HTTPException(status_code=500, detail=result.error)

    return result
