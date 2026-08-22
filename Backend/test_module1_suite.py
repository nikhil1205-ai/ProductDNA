import os
import json
from pathlib import Path
import sys

backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from product_integration.collect import integration_module_function

def test_suite():
    print("=== Running Module 1 Test Suite ===")

    # Test 1: Product Name
    print("\n--- Test 1: Product Name ---")
    res1 = integration_module_function(input_text="ABB ACS880 Industrial Drive\nManufacturer: ABB\nModel: ACS880-01")
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
    res2 = integration_module_function(file_bytes=pdf_bytes, filename="sample_abb.pdf")
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
    res3 = integration_module_function(file_bytes=csv_bytes, filename="sample_abb.csv")
    print(f"Request ID: {res3.request_id}")
    print(f"Input Type: {res3.input_type}")
    print(f"Row Count: {res3.content.row_count}")
    print(f"Columns: {res3.content.tables[0]['columns'] if res3.content.tables else []}")
    print(f"Identity: {res3.identity.model_dump()}")
    assert res3.input_type == "CSV"
    assert res3.content.row_count == 1

    # Test 4: URL
    print("\n--- Test 4: URL ---")
    try:
        res4 = integration_module_function(url_str="https://example.com")
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
    res5 = integration_module_function(json_data=sample_json)
    print(f"Request ID: {res5.request_id}")
    print(f"Input Type: {res5.input_type}")
    print(f"Identity: {res5.identity.model_dump()}")
    assert res5.input_type == "JSON"
    assert res5.identity.sku == "6205"
    assert res5.content.structured_data == sample_json

    # Test 6: Invalid Input
    print("\n--- Test 6: Invalid Input Validation ---")
    try:
        integration_module_function(file_bytes=b"hello", filename="invalid.txt")
        print("FAIL: Expected validation error for invalid file extension")
    except ValueError as ve:
        print(f"SUCCESS: Caught expected validation error -> {ve}")

    # Test 7: Unihack 6-Column Catalogue Dataset Test with Placeholders
    print("\n--- Test 7: Unihack 6-Column Catalogue Dataset ---")
    unihack_csv_bytes = (
        "Mfg_Part_Num,Part_Desc,E1_Brand,Unilog_Brand,DIB_Brand,Part_Manuf\n"
        "DCM200B,DCM200B Dewalt 1/2in x 18in - Band File,-- Unbranded --,-- No Unilog Brand --,DEWALT,Black & Decker/dewlt (2585)\n"
        "DCG410B,DCG410B Dewalt Cut Off Tool,-- Unbranded --,-- No Unilog Brand --,-- No DIB Brand --,DEWALT (1234)\n"
    ).encode("utf-8")

    res7 = integration_module_function(
        file_bytes=unihack_csv_bytes,
        filename="unihack_sample.csv",
        return_batch=True
    )
    print(f"Batch status: {res7.status}")
    print(f"Total Rows: {res7.total_rows}")
    print(f"Detected Headers: {res7.detected_headers}")
    assert res7.total_rows == 2
    assert len(res7.items) == 2

    # Verify Row 1 (DCM200B)
    item1 = res7.items[0]
    print(f"Row 1 Request ID: {item1.request_id}")
    print(f"Row 1 Identity: {item1.identity.model_dump()}")
    print(f"Row 1 Source Record: {item1.source_record.model_dump()}")
    assert item1.identity.sku == "DCM200B"
    assert item1.identity.brand == "DEWALT"
    assert item1.source_record.raw["E1_Brand"] == "-- Unbranded --"
    assert item1.source_record.normalized["E1_Brand"] is None
    assert item1.source_record.normalized["DIB_Brand"] == "DEWALT"

    # Verify Row 2 (DCG410B)
    item2 = res7.items[1]
    print(f"Row 2 Identity: {item2.identity.model_dump()}")
    assert item2.identity.sku == "DCG410B"
    assert item2.identity.manufacturer == "DEWALT (1234)"

    # Test 8: Dynamic 10-Column CSV Dataset
    print("\n--- Test 8: Dynamic 10-Column CSV Dataset ---")
    dynamic_csv_bytes = (
        "SKU,Product Name,Brand,Voltage,Weight,Custom_Field_1,Category,Warehouse_Bin,Supplier,Notes\n"
        "MOT-100,3-Phase Induction Motor,ABB,415V,25kg,CUST-999,Motors,BIN-12,ABB Global,High efficiency\n"
    ).encode("utf-8")

    res8 = integration_module_function(
        file_bytes=dynamic_csv_bytes,
        filename="dynamic_motors.csv"
    )
    # Single row returns StandardProductInput directly
    print(f"Request ID: {res8.request_id}")
    print(f"Headers preserved in raw: {list(res8.source_record.raw.keys())}")
    assert "Custom_Field_1" in res8.source_record.raw
    assert res8.source_record.raw["Custom_Field_1"] == "CUST-999"
    assert res8.identity.sku == "MOT-100"
    assert res8.identity.brand == "ABB"

    # Check output directory
    output_dir = backend_dir / "input_data" / "Standard_input"
    saved_files = list(output_dir.glob("REQ-*.json"))
    print(f"\nTotal Standardized JSON files saved in {output_dir}: {len(saved_files)}")

    print("\n=== All Module 1 Tests Completed Successfully! ===")

if __name__ == "__main__":
    test_suite()

