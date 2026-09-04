import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from Evidence_collection_sources_module_2.services.resource_manager import ResourceManager
from Evidence_collection_sources_module_2.models.source_models import SourceInput, SourceType

def test_storage():
    print("=== Testing Module 2 Storage in organization_sources/data_sources ===")
    manager = ResourceManager()
    
    # 1. Add Text Resource
    inp = SourceInput(
        request_id="REQ-TEST-001",
        type=SourceType.TEXT,
        value="Sample technical specifications for dishwashers.",
        name="dishwasher_specs.txt"
    )
    src = manager.add_resource(inp)
    print(f"Added source: {src.source_id}, status={src.status}")
    
    # Check directory
    data_sources_dir = backend_dir / "organization_sources" / "data_sources"
    manifest_path = data_sources_dir / "resource_manifest.json"
    res_dir = data_sources_dir / "resources" / src.source_id
    
    assert data_sources_dir.exists(), "data_sources directory was not created!"
    assert manifest_path.exists(), "resource_manifest.json was not created!"
    assert res_dir.exists(), f"Source directory {res_dir} was not created!"
    
    print(f"Manifest path: {manifest_path}")
    print(f"Source files directory: {res_dir}")
    print("Listing stored sources:")
    for s in manager.list_resources(request_id="REQ-TEST-001"):
        print(f" - {s.source_id}: {s.source_name} ({s.source_type.value})")

    # Clean up test source
    manager.delete_resource(src.source_id)
    print("Cleaned up test source successfully.")
    print("=== All Verification Checks Passed! ===")

if __name__ == "__main__":
    test_storage()
