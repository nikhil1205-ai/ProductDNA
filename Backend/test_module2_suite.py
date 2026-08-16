import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from product_resolution_engine.registry_loader import load_registry
from product_resolution_engine.resolver import resolve
from product_resolution_engine.resolution_main import REGISTRY_PATH

def test_module2():
    print("=== Running Module 2 Test Suite ===")
    
    registry = load_registry(str(REGISTRY_PATH))

    # Test 1 — Resolved
    print("\n--- Test 1: Resolved ---")
    identity1 = {"sku": "3AUA000012345"}
    res1 = resolve(identity1, registry)
    print(f"Result: {res1}")
    assert res1["status"] == "RESOLVED"
    assert res1["match_type"] == "EXACT_SKU"
    assert res1["product_id"] == "PDNA-001"
    assert res1["candidates"] == []

    # Test 2 — Ambiguous
    print("\n--- Test 2: Ambiguous (Manufacturer + Model) ---")
    identity2 = {
        "manufacturer": "ABB",
        "model": "ACS880",
        "sku": None
    }
    res2 = resolve(identity2, registry)
    print(f"Result: {res2}")
    assert res2["status"] == "AMBIGUOUS"
    assert res2["product_id"] is None
    assert len(res2["candidates"]) > 0
    # Check candidates sorted by score
    scores = [c["score"] for c in res2["candidates"]]
    assert scores == sorted(scores, reverse=True)
    # Check candidates contain product_id, product_name, sku, score
    for c in res2["candidates"]:
        assert "product_id" in c
        assert "product_name" in c
        assert "sku" in c
        assert "score" in c
        assert isinstance(c["score"], (int, float))
        print(f"  Candidate: {c}")

    # Test 3 — Unresolved
    print("\n--- Test 3: Unresolved ---")
    identity3 = {
        "product_name": "Completely Unknown Product",
        "sku": "UNKNOWN-999"
    }
    res3 = resolve(identity3, registry)
    print(f"Result: {res3}")
    assert res3["status"] == "UNRESOLVED"
    assert res3["product_id"] is None
    assert res3["candidates"] == []

    # Test 4 — Alias Ambiguity
    print("\n--- Test 4: Alias Ambiguity ---")
    identity4 = {
        "product_name": "ACS880 Drive"
    }
    res4 = resolve(identity4, registry)
    print(f"Result: {res4}")
    assert res4["status"] == "AMBIGUOUS"
    assert res4["match_type"] == "ALIAS"
    assert res4["product_id"] is None
    assert len(res4["candidates"]) >= 2
    # Check candidates structure and score sorting
    scores = [c["score"] for c in res4["candidates"]]
    assert scores == sorted(scores, reverse=True)
    for c in res4["candidates"]:
        assert "product_id" in c
        assert "product_name" in c
        assert "sku" in c
        assert "score" in c
        assert isinstance(c["score"], (int, float))
        print(f"  Candidate: {c}")

    print("\n=== All Module 2 Tests Passed! ===")

if __name__ == "__main__":
    test_module2()
