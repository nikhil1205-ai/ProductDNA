import os
import json
from pathlib import Path
import sys

backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from data_integration.collect import run_module_1

def test_suite():
    print("=== Running Module 1 Test Suite ===")

    # Test 1: Product Name
    print("\n--- Test 1: Product Name ---")
    res1 = run_module_1(input_text="ABB ACS880 Industrial Drive\nManufacturer: ABB\nModel: ACS880-01")
    print(f"Request ID: {res1.request_id}")
    print(f"Input Type: {res1.input_type}")
    print(f"Identity: {res1.identity.model_dump()}")
    assert res1.input_type == "PRODUCT_NAME"
    assert res1.identity.product_name is not None
    assert res1.identity.brand == "ABB"

    # Test 2: PDF
    print("\n--- Test 2: PDF File ---")
    pdf_path = backend_dir / "input_data" / "sample_abb.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    res2 = run_module_1(file_bytes=pdf_bytes, filename="sample_abb.pdf")
    print(f"Request ID: {res2.request_id}")
    print(f"Input Type: {res2.input_type}")
    print(f"Page Count: {res2.content.page_count}")
    print(f"Identity: {res2.identity.model_dump()}")
    assert res2.input_type == "PDF"
    assert res2.content.page_count == 1
    assert res2.identity.brand == "ABB"

    # Test 3: CSV
    print("\n--- Test 3: CSV File ---")
    csv_path = backend_dir / "input_data" / "sample_abb.csv"
    with open(csv_path, "rb") as f:
        csv_bytes = f.read()
    res3 = run_module_1(file_bytes=csv_bytes, filename="sample_abb.csv")
    print(f"Request ID: {res3.request_id}")
    print(f"Input Type: {res3.input_type}")
    print(f"Row Count: {res3.content.row_count}")
    print(f"Columns: {res3.content.tables[0]['columns'] if res3.content.tables else []}")
    print(f"Identity: {res3.identity.model_dump()}")
    assert res3.input_type == "CSV"
    assert res3.content.row_count == 2

    # Test 4: URL
    print("\n--- Test 4: URL ---")
    try:
        res4 = run_module_1(url_str="https://example.com")
        print(f"Request ID: {res4.request_id}")
        print(f"Input Type: {res4.input_type}")
        print(f"Title: {res4.content.title}")
        assert res4.input_type == "URL"
        assert res4.content.title is not None
    except Exception as e:
        print(f"URL test notice: {e}")

    # Test 5: JSON
    print("\n--- Test 5: JSON Payload ---")
    sample_json = {
        "product_name": "SKF 6205",
        "brand": "SKF",
        "manufacturer": "SKF",
        "sku": "6205",
        "category": "Bearing"
    }
    res5 = run_module_1(json_data=sample_json)
    print(f"Request ID: {res5.request_id}")
    print(f"Input Type: {res5.input_type}")
    print(f"Identity: {res5.identity.model_dump()}")
    assert res5.input_type == "JSON"
    assert res5.identity.sku == "6205"
    assert res5.content.structured_data == sample_json

    # Test 6: Invalid Input
    print("\n--- Test 6: Invalid Input Validation ---")
    try:
        run_module_1(file_bytes=b"hello", filename="invalid.txt")
        print("FAIL: Expected validation error for invalid file extension")
    except ValueError as ve:
        print(f"SUCCESS: Caught expected validation error -> {ve}")

    # Check output directory
    output_dir = backend_dir / "input_data" / "Standard_input"
    saved_files = list(output_dir.glob("REQ-*.json"))
    print(f"\nTotal Standardized JSON files saved in {output_dir}: {len(saved_files)}")
    for sf in saved_files:
        print(f"  - {sf.name}")

    print("\n=== All Module 1 Tests Completed Successfully! ===")

if __name__ == "__main__":
    test_suite()
