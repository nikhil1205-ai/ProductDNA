"""
Command-line script to execute Module 4 extraction workflow on a file from Standard_input.
"""

import sys
import json
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from Evidence_collection_sources.api.routes import run_module4_on_file

def main():
    # Use default file if none provided
    filename = sys.argv[1] if len(sys.argv) > 1 else "REQ-20260816-2AD355E9.json"
    
    print(f"--- Running Module 4 Evidence Extraction on File: {filename} ---")
    try:
        result = run_module4_on_file(filename)
        print(json.dumps(result, indent=2))
        
        # Save output in Standard_input or input_data
        output_file = backend_dir / "input_data" / f"evidence_output_{filename}"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
            
        print(f"\n[SUCCESS] Structured Evidence saved to: {output_file}")
    except Exception as e:
        print(f"[ERROR] Failed to run Module 4: {str(e)}")

if __name__ == "__main__":
    main()
