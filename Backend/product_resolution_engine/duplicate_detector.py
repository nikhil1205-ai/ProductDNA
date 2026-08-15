from typing import Dict, List, Any
from .normalizer import normalize_text

def detect_duplicates(registry: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Identifies potential duplicates based on SKU or Manufacturer+Model."""
    duplicates = []
    
    # O(n^2) is fine for a small prototype CSV
    seen = set()
    for i, r1 in enumerate(registry):
        for j, r2 in enumerate(registry):
            if i >= j:
                continue # avoid pairing with self or double counting
                
            sku1 = normalize_text(r1.get('sku'))
            sku2 = normalize_text(r2.get('sku'))
            
            mfg1 = normalize_text(r1.get('manufacturer') or r1.get('brand'))
            mfg2 = normalize_text(r2.get('manufacturer') or r2.get('brand'))
            
            model1 = normalize_text(r1.get('model'))
            model2 = normalize_text(r2.get('model'))
            
            reason = None
            if sku1 and sku2 and sku1 == sku2:
                reason = "Shared SKU"
            elif mfg1 and mfg2 and mfg1 == mfg2 and model1 and model2 and model1 == model2:
                reason = "Shared Manufacturer and Model"
                
            if reason:
                # check if product IDs are different
                if r1.get('product_id') != r2.get('product_id'):
                    pair_id = tuple(sorted([r1.get('product_id'), r2.get('product_id')]))
                    if pair_id not in seen:
                        seen.add(pair_id)
                        duplicates.append({
                            "reason": reason,
                            "product_1": r1.get('product_id'),
                            "product_2": r2.get('product_id'),
                            "details": f"{mfg1} {model1} | SKU: {sku1}"
                        })
                        
    return duplicates
