import csv
from pathlib import Path
from typing import List, Dict

def load_registry(csv_path: str) -> List[Dict[str, str]]:
    path = Path(csv_path)
    records: List[Dict[str, str]] = []
    
    if not path.exists():
        raise FileNotFoundError(f"Registry not found: {path}")
        
    with open(path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
            
    return records
