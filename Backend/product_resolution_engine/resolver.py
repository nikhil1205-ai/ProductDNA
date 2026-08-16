from typing import Dict, Any, List
from .utils import match_sku, match_part_number, match_identity, match_alias, score_candidate

def resolve(identity: Dict[str, Any], registry_records: List[Dict[str, str]]) -> Dict[str, Any]:
    """Resolves the candidate identity against the registry using a series of matching functions."""
    
    # 1. Exact SKU Match
    sku_matches = match_sku(identity.get('sku'), registry_records)
    if len(sku_matches) == 1:
        return {
            "status": "RESOLVED",
            "match_type": "EXACT_SKU",
            "confidence": score_candidate("EXACT_SKU", 1),
            "product_id": sku_matches[0]['product_id'],
            "candidates": []
        }
    elif len(sku_matches) > 1:
        candidates = [
            {
                "product_id": m['product_id'],
                "product_name": m['product_name'],
                "sku": m.get('sku') or None,
                "score": score_candidate("EXACT_SKU", 1)
            }
            for m in sku_matches
        ]
        return {
            "status": "AMBIGUOUS",
            "match_type": "EXACT_SKU",
            "confidence": score_candidate("EXACT_SKU", len(sku_matches)),
            "product_id": None,
            "candidates": sorted(candidates, key=lambda x: x["score"], reverse=True)
        }
        
    # 2. Exact Part Number Match
    pn_matches = match_part_number(identity.get('part_number'), registry_records)
    if len(pn_matches) == 1:
        return {
            "status": "RESOLVED",
            "match_type": "EXACT_PART_NUMBER",
            "confidence": score_candidate("EXACT_PART_NUMBER", 1),
            "product_id": pn_matches[0]['product_id'],
            "candidates": []
        }
    elif len(pn_matches) > 1:
        candidates = [
            {
                "product_id": m['product_id'],
                "product_name": m['product_name'],
                "sku": m.get('sku') or None,
                "score": score_candidate("EXACT_PART_NUMBER", 1)
            }
            for m in pn_matches
        ]
        return {
            "status": "AMBIGUOUS",
            "match_type": "EXACT_PART_NUMBER",
            "confidence": score_candidate("EXACT_PART_NUMBER", len(pn_matches)),
            "product_id": None,
            "candidates": sorted(candidates, key=lambda x: x["score"], reverse=True)
        }
        
    # 3. Manufacturer + Model Match
    mm_matches = match_identity(
        manufacturer=identity.get('manufacturer'),
        brand=identity.get('brand'),
        model=identity.get('model'),
        registry=registry_records
    )
    if len(mm_matches) == 1:
        return {
            "status": "RESOLVED",
            "match_type": "MANUFACTURER_MODEL",
            "confidence": score_candidate("MANUFACTURER_MODEL", 1),
            "product_id": mm_matches[0]['product_id'],
            "candidates": []
        }
    elif len(mm_matches) > 1:
        candidates = [
            {
                "product_id": m['product_id'],
                "product_name": m['product_name'],
                "sku": m.get('sku') or None,
                "score": score_candidate("MANUFACTURER_MODEL", 1)
            }
            for m in mm_matches
        ]
        return {
            "status": "AMBIGUOUS",
            "match_type": "MANUFACTURER_MODEL",
            "confidence": score_candidate("MANUFACTURER_MODEL", len(mm_matches)),
            "product_id": None,
            "candidates": sorted(candidates, key=lambda x: x["score"], reverse=True)
        }
        
    # 4. Product Name / Alias Match
    alias_matches = match_alias(identity.get('product_name', ''), registry_records)
    if alias_matches:
        best_match, highest_ratio = alias_matches[0]
        # Check if there are ties
        top_candidates = [m for m in alias_matches if m[1] == highest_ratio]
        
        if len(top_candidates) == 1:
            return {
                "status": "RESOLVED",
                "match_type": "ALIAS",
                "confidence": score_candidate("ALIAS", 1, highest_ratio),
                "product_id": best_match['product_id'],
                "candidates": []
            }
        else:
            candidates = [
                {
                    "product_id": m[0]['product_id'],
                    "product_name": m[0]['product_name'],
                    "sku": m[0].get('sku') or None,
                    "score": score_candidate("ALIAS", 1, m[1])
                }
                for m in top_candidates
            ]
            return {
                "status": "AMBIGUOUS",
                "match_type": "ALIAS",
                "confidence": score_candidate("ALIAS", len(top_candidates), highest_ratio),
                "product_id": None,
                "candidates": sorted(candidates, key=lambda x: x["score"], reverse=True)
            }

    # 5. No Match
    return {
        "status": "UNRESOLVED",
        "match_type": "NO_MATCH",
        "confidence": score_candidate("NO_MATCH", 0),
        "product_id": None,
        "candidates": []
    }
