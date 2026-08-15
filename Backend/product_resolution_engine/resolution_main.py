import os
from pathlib import Path
from typing import Dict, Any
import copy
import json

# Add the parent directory to the path so we can import modules
import sys
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR.parent) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR.parent))

from product_resolution_engine.registry_loader import load_registry
from product_resolution_engine.resolver import resolve

REGISTRY_PATH = CURRENT_DIR / "org_data" / "product_registry.csv"

def run_resolution(module1_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main runner function for Module 2.
    Takes Module 1 input JSON (as a dictionary), resolves it against the Product Registry,
    and returns the updated Module 2 output JSON.
    """
    # Create a copy to avoid mutating the original input if needed
    result = copy.deepcopy(module1_input)
    
    # Load registry
    records = load_registry(str(REGISTRY_PATH))
    
    # Extract identity
    identity = result.get("identity", {})
    
    # Resolve
    resolution_data = resolve(identity, records)
    
    # Update result
    result["resolution_data"] = resolution_data
    result["status"] = resolution_data.get("status", "UNRESOLVED")
    
    return result

if __name__ == "__main__":
    # Example usage / runner when executed directly
    
    # Read from stdin or provide a sample
    sample_input = {
      "request_id": "REQ-20260815-76B6CBA0",
      "input_type": "PDF",
      "identity": {
        "product_name": "ABB ACS880 Industrial Drive",
        "brand": "ABB",
        "manufacturer": "ABB",
        "model": "ACS880-01-145A-3",
        "sku": "3AUA000012345",
        "part_number": "3AUA000012345"
      },
      "metadata": {
        "filename": "sample_abb.pdf",
        "extension": ".pdf",
        "mime_type": "application/pdf",
        "size_bytes": 981,
        "created_at": "2026-08-15T15:43:14.960511+00:00",
        "checksum": "042516f464ddf5127a9b4caf1966f7d849a0f6b243ae9e93c266fa273bc6412e",
        "source_url": "",
        "retrieved_at": "null"
      },
      "content": {
        "text": "ABB ACS880 Industrial Drive\nManufacturer: ABB\nModel: ACS880-01-145A-3\nSKU: 3AUA000012345\nDescription: High performance wall-mounted single drive.",
        "title": "",
        "tables": [],
        "structured_data": "",
        "page_count": 1,
        "row_count": "",
        "column_count": ""
      },
      "status": "READY_FOR_RESOLUTION"
    }

    # print("Running Module 2 Resolution on Sample Input...")
    # resolved_output = run_resolution(sample_input)
    # print(json.dumps(resolved_output, indent=2))
