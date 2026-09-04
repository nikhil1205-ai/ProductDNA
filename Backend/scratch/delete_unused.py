import shutil
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
mod2_dir = backend_dir / "Evidence_collection_sources_module_2"

files_to_remove = [
    mod2_dir / "config" / "llm_config.py",
    mod2_dir / "config" / "__init__.py",
    mod2_dir / "storage" / "resource_manifest.json",
]

dirs_to_remove = [
    mod2_dir / "config",
    mod2_dir / "storage" / "resources",
]

for f in files_to_remove:
    if f.exists():
        f.unlink()
        print(f"Deleted file: {f}")

for d in dirs_to_remove:
    if d.exists() and d.is_dir():
        try:
            shutil.rmtree(d)
            print(f"Deleted directory: {d}")
        except Exception as e:
            print(f"Could not remove directory {d}: {e}")

print("Cleanup completed successfully.")
