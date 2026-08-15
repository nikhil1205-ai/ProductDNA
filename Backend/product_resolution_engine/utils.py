from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher
from .normalizer import normalize_fuzzy, normalize_text

# --- candidate_scorer.py ---
def score_candidate(match_type: str, candidate_count: int, fuzzy_ratio: float = 0.0) -> float:
    """
    Returns a normalized confidence score between 0.0 and 1.0.
    Higher weights for exact identifiers, lower for fuzzy/ambiguous.
    """
    if candidate_count == 0:
        return 0.0
        
    if match_type == "EXACT_SKU":
        return 1.0
    elif match_type == "EXACT_PART_NUMBER":
        return 0.95
    elif match_type == "MANUFACTURER_MODEL":
        if candidate_count == 1:
            return 0.90
        else:
            return 0.70
    elif match_type == "ALIAS":
        if candidate_count == 1:
            return round(min(fuzzy_ratio, 0.89), 2)
        else:
            return round(min(fuzzy_ratio * 0.8, 0.65), 2)
            
    return 0.0

# --- sku_matcher.py ---
def match_sku(sku: Optional[str], registry: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Finds all products matching the normalized SKU."""
    if not sku:
        return []
        
    input_sku = normalize_text(sku)
    if not input_sku:
        return []
        
    matches = []
    for record in registry:
        if normalize_text(record.get('sku', '')) == input_sku:
            matches.append(record)
    return matches

def match_part_number(part_number: Optional[str], registry: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Finds all products matching the normalized part number."""
    if not part_number:
        return []
        
    input_pn = normalize_text(part_number)
    if not input_pn:
        return []
        
    matches = []
    for record in registry:
        if normalize_text(record.get('part_number', '')) == input_pn:
            matches.append(record)
    return matches

# --- identity_matcher.py ---
def match_identity(manufacturer: Optional[str], brand: Optional[str], model: Optional[str], registry: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Finds products matching Manufacturer + Model exactly."""
    input_mfg = normalize_text(manufacturer) or normalize_text(brand)
    input_model = normalize_text(model)
    
    if not input_mfg or not input_model:
        return []
        
    matches = []
    for record in registry:
        reg_mfg = normalize_text(record.get('manufacturer', '')) or normalize_text(record.get('brand', ''))
        reg_model = normalize_text(record.get('model', ''))
        
        if reg_mfg == input_mfg and reg_model == input_model:
            matches.append(record)
            
    return matches

# --- alias_matcher.py ---
def match_alias(product_name: str, registry: List[Dict[str, str]], threshold: float = 0.85) -> List[Tuple[Dict[str, str], float]]:
    """Finds products using fuzzy match against product_name and aliases."""
    if not product_name:
        return []
        
    input_name = normalize_fuzzy(product_name)
    if not input_name:
        return []
        
    candidates = []
    for record in registry:
        reg_name = normalize_fuzzy(record.get('product_name', ''))
        
        name_ratio = SequenceMatcher(None, input_name, reg_name).ratio()
        
        alias_ratios = []
        aliases_str = record.get('aliases', '')
        if aliases_str:
            for alias in aliases_str.split(';'):
                normalized_alias = normalize_fuzzy(alias.strip())
                if normalized_alias:
                    alias_ratios.append(SequenceMatcher(None, input_name, normalized_alias).ratio())
                    
        max_alias_ratio = max(alias_ratios) if alias_ratios else 0.0
        
        best_ratio = max(name_ratio, max_alias_ratio)
        
        if best_ratio >= threshold:
            candidates.append((record, best_ratio))
            
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates
