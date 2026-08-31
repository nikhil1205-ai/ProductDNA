import os
import shutil
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
mod2_dir = backend_dir / "Evidence_collection_sources"

files_to_remove = [
    mod2_dir / "services" / "evidence_extraction_service.py",
    mod2_dir / "models" / "document_models.py",
    mod2_dir / "models" / "extraction_models.py",
    mod2_dir / "models" / "response_models.py",
]

dirs_to_remove = [
    mod2_dir / "config",
]

for f in files_to_remove:
    if f.exists():
        f.unlink()
        print(f"Deleted file: {f}")

for d in dirs_to_remove:
    if d.exists() and d.is_dir():
        shutil.rmtree(d)
        print(f"Deleted directory: {d}")

print("Cleanup complete!")
