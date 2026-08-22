import os
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from product_integration.collect import integration_module_function
from product_integration.schemas.response_schema import StandardBatchResponse

csv_path = backend_dir / "input_data" / "Sample_input" / "Unihack_ Sample Dataset - Input.csv"

if not csv_path.exists():
    print(f"Error: Sample file not found at {csv_path}")
    sys.exit(1)

print(f"Loading sample CSV dataset from: {csv_path}")
with open(csv_path, "rb") as f:
    file_bytes = f.read()

res = integration_module_function(
    file_bytes=file_bytes,
    filename=csv_path.name,
    return_batch=True
)

if isinstance(res, StandardBatchResponse):
    print("\n==================================================")
    print("      MODULE 1 UNIHACK SAMPLE INTAKE SUMMARY      ")
    print("==================================================")
    print(f"Filename        : {res.filename}")
    print(f"Total Rows      : {res.total_rows}")
    print(f"Processed Count : {res.processed_count}")
    print(f"Successful Count: {res.successful_count}")
    print(f"Failed Count    : {res.failed_count}")
    print(f"Detected Headers: {res.detected_headers}")
    print("--------------------------------------------------")
    print(f"Sample First Record (Row 1):")
    if res.items:
        row1 = res.items[0]
        print(f"  Request ID    : {row1.request_id}")
        print(f"  Part Number   : {row1.identity.part_number}")
        print(f"  SKU           : {row1.identity.sku}")
        print(f"  Product Name  : {row1.identity.product_name}")
        print(f"  Brand         : {row1.identity.brand}")
        print(f"  Manufacturer  : {row1.identity.manufacturer}")
        print(f"  Raw E1_Brand  : {row1.source_record.raw.get('E1_Brand')}")
        print(f"  Norm e1_brand : {row1.source_record.normalized.get('e1_brand')}")
        print(f"  Status        : {row1.status}")
    print("==================================================")
    output_dir = backend_dir / "input_data" / "Standard_input"
    saved_files = list(output_dir.glob("REQ-*.json"))
    print(f"All {len(res.items)} records processed. Total standardized JSON files in {output_dir}: {len(saved_files)}\n")
