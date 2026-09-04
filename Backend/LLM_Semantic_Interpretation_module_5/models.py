"""
Module 5 — Pydantic Models: Request, Response, and Delivery Record
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ─── Request ──────────────────────────────────────────────────────────────────

class Module5Request(BaseModel):
    """Input payload for Module 5 Semantic Interpretation."""
    product: Dict[str, Any] = Field(..., description="Selected Module 1 StandardProductInput JSON")
    organization: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Organization / Product Registry JSON (single matched record or dict of registry records)"
    )


# ─── Candidate Field ──────────────────────────────────────────────────────────

class CandidateField(BaseModel):
    """Single candidate field with provenance metadata."""
    field: str
    value: str = ""
    source: str = "LLM_INFERENCE"
    interpretation_type: str = "SEMANTIC"
    llm_confidence: float = 0.0
    requires_validation: bool = True


# ─── Classification Block ─────────────────────────────────────────────────────

class ClassificationResult(BaseModel):
    dept: str = ""
    class_: str = Field("", alias="class")
    fine: str = ""
    classpath: str = ""
    confidence: float = 0.0
    status: str = "CANDIDATE"

    model_config = {"populate_by_name": True}


# ─── Module 5 Response ────────────────────────────────────────────────────────

class Module5Response(BaseModel):
    request_id: str
    selected_product_id: str
    module: str = "MODULE_5"
    status: str = "CANDIDATE_GENERATED"
    processing_time_ms: float = 0.0
    populated_fields_count: int = 0
    inferred_fields_count: int = 0
    delivery_record: Dict[str, str] = Field(
        default_factory=dict,
        description="252-column flat candidate delivery record"
    )
    semantic_metadata: List[CandidateField] = Field(
        default_factory=list,
        description="Per-field provenance and confidence"
    )
    classification: ClassificationResult = Field(
        default_factory=ClassificationResult
    )
    error: Optional[str] = None
