"""
Module 2 Resource Store: Local Filesystem Storage & Lightweight Manifest Manager
"""

import json
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional

from ..models.source_models import Source, SourceStatus

STORAGE_DIR = Path(__file__).resolve().parent
RESOURCES_DIR = STORAGE_DIR / "resources"
MANIFEST_FILE = STORAGE_DIR / "resource_manifest.json"

class ResourceStore:
    """
    Local filesystem storage manager for Module 2 resources.
    Manages physical file artifacts under storage/resources/<source_id>/
    and tracks resource records in storage/resource_manifest.json.
    """

    def __init__(self):
        RESOURCES_DIR.mkdir(parents=True, exist_ok=True)
        if not MANIFEST_FILE.exists():
            self._write_manifest({})

    def _read_manifest(self) -> Dict[str, Any]:
        if not MANIFEST_FILE.exists():
            return {}
        try:
            with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _write_manifest(self, manifest: Dict[str, Any]) -> None:
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, default=str)

    def get_next_source_id(self) -> str:
        manifest = self._read_manifest()
        existing_ids = list(manifest.keys())
        max_num = 0
        for sid in existing_ids:
            if sid.startswith("SRC-"):
                try:
                    num = int(sid.replace("SRC-", ""))
                    if num > max_num:
                        max_num = num
                except ValueError:
                    pass
        return f"SRC-{max_num + 1:03d}"

    def save_source(self, source: Source, file_bytes: Optional[bytes] = None) -> Source:
        """
        Saves source object to the manifest and stores physical file bytes if provided.
        """
        manifest = self._read_manifest()
        
        # Physical storage directory for this source ID
        source_dir = RESOURCES_DIR / source.source_id
        source_dir.mkdir(parents=True, exist_ok=True)

        if file_bytes:
            raw_filename = source.metadata.filename or f"original.{source.source_type.value}"
            # Sanitize filename for OS filesystem compatibility
            import re
            filename = re.sub(r'[\\/*?:"<>|]', '_', raw_filename)
            file_path = source_dir / filename
            try:
                file_path.write_bytes(file_bytes)
            except Exception as e:
                print(f"Warning: Failed to write physical file for {source.source_id}: {e}")

        # Update manifest record
        if hasattr(source, "model_dump"):
            source_dict = source.model_dump(exclude_none=True)
        else:
            source_dict = source.dict(exclude_none=True)

        manifest[source.source_id] = source_dict
        self._write_manifest(manifest)
        return source

    def get_source(self, source_id: str) -> Optional[Source]:
        """
        Retrieves a single Source object by source_id.
        """
        manifest = self._read_manifest()
        data = manifest.get(source_id)
        if not data:
            return None
        return Source(**data)

    def list_sources(self, request_id: Optional[str] = None) -> List[Source]:
        """
        Lists all recorded sources, optionally filtered by request_id.
        """
        manifest = self._read_manifest()
        sources: List[Source] = []
        for data in manifest.values():
            try:
                src = Source(**data)
                if request_id is None or src.request_id == request_id:
                    sources.append(src)
            except Exception:
                continue
        # Sort by creation time / source_id
        sources.sort(key=lambda s: s.source_id)
        return sources

    def delete_source(self, source_id: str) -> bool:
        """
        Deletes a resource record from manifest and removes its physical directory.
        """
        manifest = self._read_manifest()
        if source_id not in manifest:
            return False

        del manifest[source_id]
        self._write_manifest(manifest)

        source_dir = RESOURCES_DIR / source_id
        if source_dir.exists() and source_dir.is_dir():
            try:
                shutil.rmtree(source_dir)
            except Exception as e:
                print(f"Warning: Failed to delete directory for {source_id}: {e}")

        return True

    def find_by_content_hash(self, content_hash: str, request_id: Optional[str] = None) -> Optional[Source]:
        """
        Finds an existing source record matching the given SHA-256 content_hash.
        """
        if not content_hash:
            return None
        manifest = self._read_manifest()
        for data in manifest.values():
            try:
                src = Source(**data)
                if src.metadata and src.metadata.content_hash == content_hash:
                    if request_id is None or src.request_id == request_id:
                        return src
            except Exception:
                continue
        return None
