"""
Module 4 Text Collector
"""

import hashlib
from pathlib import Path

from .base import BaseSourceCollector
from ..models.source_models import SourceInput, Source, SourceMetadata, SourceType, SourceStatus, SourceOrigin

class TextCollector(BaseSourceCollector):
    """
    Intake collector for plain text / technical text document sources.
    Handles file path, file bytes, or raw string input.
    """
    
    def collect(self, source_input: SourceInput, source_id: str) -> Source:
        text_content = ""
        filename = source_input.name or "document.txt"
        
        if source_input.file_bytes:
            try:
                text_content = source_input.file_bytes.decode("utf-8", errors="replace")
            except Exception:
                text_content = str(source_input.file_bytes)
        elif source_input.value:
            path = Path(source_input.value)
            if path.is_file():
                filename = path.name
                try:
                    text_content = path.read_text(encoding="utf-8", errors="replace")
                except Exception as e:
                    return Source(
                        source_id=source_id,
                        source_type=SourceType.TEXT,
                        source_subtype=source_input.subtype or "technical_notes",
                        source_name=filename,
                        origin=SourceOrigin.USER_PROVIDED,
                        status=SourceStatus.FAILED,
                        error_message=f"Failed to read text file '{path}': {str(e)}",
                        metadata=SourceMetadata(filename=filename)
                    )
            else:
                text_content = source_input.value

        if not text_content.strip():
            return Source(
                source_id=source_id,
                source_type=SourceType.TEXT,
                source_subtype=source_input.subtype or "technical_notes",
                source_name=filename,
                origin=SourceOrigin.USER_PROVIDED,
                status=SourceStatus.FAILED,
                error_message="Empty text content provided.",
                metadata=SourceMetadata(filename=filename)
            )

        content_bytes = text_content.encode("utf-8")
        content_hash = hashlib.sha256(content_bytes).hexdigest()
        
        # Save decoded text on source_input for processor
        source_input.metadata["text_content"] = text_content

        metadata = SourceMetadata(
            filename=filename,
            content_type="text/plain",
            size_bytes=len(content_bytes),
            content_hash=content_hash
        )

        return Source(
            source_id=source_id,
            source_type=SourceType.TEXT,
            source_subtype=source_input.subtype or "technical_notes",
            source_name=filename,
            origin=SourceOrigin.USER_PROVIDED,
            status=SourceStatus.RECEIVED,
            metadata=metadata
        )
