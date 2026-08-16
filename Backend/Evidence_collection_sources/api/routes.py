"""
Module 4 FastAPI Router Definitions
"""

import json
from typing import Optional, List

from ..models.source_models import SourceInput, SourceType
from ..models.response_models import StructuredEvidence, Module4Response
from ..services.evidence_extraction_service import EvidenceExtractionService

service = EvidenceExtractionService()

def run_module4_on_file(filename: str) -> dict:
    """
    Reads a resolved product JSON from input_data/Standard_input,
    generates a dummy source in input_data, runs Module 4 extraction,
    and returns the structured evidence result dictionary.
    """
    import os
    from pathlib import Path

    # Locate directories
    backend_dir = Path(__file__).resolve().parent.parent.parent
    standard_input_dir = backend_dir / "input_data" / "Standard_input"
    input_data_dir = backend_dir / "input_data"

    # Resolve input file path
    file_path = standard_input_dir / filename
    if not file_path.exists():
        # Try relative to backend dir or absolute path
        file_path = Path(filename)
        if not file_path.exists():
            file_path = backend_dir / filename
            if not file_path.exists():
                raise FileNotFoundError(f"Input file not found: {filename}")

    # Load Module 2 JSON data
    with open(file_path, "r", encoding="utf-8") as f:
        module2_data = json.load(f)

    identity = module2_data.get("identity") or module2_data.get("product_identity") or {}
    product_name = identity.get("product_name") or "Generic Product"
    model = identity.get("model") or ""
    brand = identity.get("brand") or ""

    # Read all files from input_data/organization_sources/
    organization_sources_dir = input_data_dir / "organization_sources"
    
    # Ensure directory exists
    organization_sources_dir.mkdir(parents=True, exist_ok=True)
    
    sources = []
    
    if organization_sources_dir.exists() and organization_sources_dir.is_dir():
        for source_file in organization_sources_dir.iterdir():
            if source_file.is_file():
                ext = source_file.suffix.lower()
                
                if ext == ".url" or "urls" in source_file.name.lower():
                    # Treat as a text file containing URLs
                    with open(source_file, "r", encoding="utf-8") as url_file:
                        for line in url_file:
                            url = line.strip()
                            if url.startswith("http"):
                                sources.append({
                                    "type": "url",
                                    "value": url,
                                    "name": url,
                                    "subtype": "website"
                                })
                elif ext == ".pdf":
                    sources.append({
                        "type": "pdf",
                        "value": str(source_file),
                        "name": source_file.name,
                        "subtype": "technical_manual"
                    })
                elif ext in [".csv", ".txt", ".md", ".json"]:
                    sources.append({
                        "type": "text",
                        "value": str(source_file),
                        "name": source_file.name,
                        "subtype": "technical_notes"
                    })

    # Build Module 4 request payload
    payload = {
        "request_id": module2_data.get("request_id"),
        "identity": identity,
        "status": module2_data.get("status"),
        "sources": sources
    }

    # Execute extraction service
    result = service.process(payload)
    
    # Return dictionary representation
    if hasattr(result, "model_dump"):
        return result.model_dump()
    return result.dict()

