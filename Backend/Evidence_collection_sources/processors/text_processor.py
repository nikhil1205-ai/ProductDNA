"""
Module 4 Text Document Content Processor
"""

import re
from typing import List

from .base import BaseProcessor
from .content_cleaner import clean_whitespace, remove_duplicate_text_blocks
from ..models.source_models import Source, SourceInput, SourceStatus
from ..models.document_models import Document, Section, TextBlock, LocationInfo

class TextProcessor(BaseProcessor):
    """
    Processor for Plain Text / Technical Text documents.
    Segments sections by headers and creates TextBlock representations.
    """
    
    def process(self, source: Source, source_input: SourceInput) -> Document:
        text_content = source_input.metadata.get("text_content") or source_input.value or ""
        
        if source_input.file_bytes and not text_content:
            try:
                text_content = source_input.file_bytes.decode("utf-8", errors="replace")
            except Exception:
                text_content = str(source_input.file_bytes)

        text_content = clean_whitespace(text_content)
        if not text_content:
            source.status = SourceStatus.FAILED
            source.error_message = "EMPTY_TEXT_DOCUMENT: No readable text found."
            return Document(document_id=f"DOC-{source.source_id}", source_id=source.source_id)

        text_blocks: List[TextBlock] = []
        current_section = "General Specifications"
        block_idx = 1

        lines = text_content.split("\n")
        current_paragraph_lines: List[str] = []

        for line in lines:
            line_str = line.strip()
            if not line_str:
                if current_paragraph_lines:
                    para_text = " ".join(current_paragraph_lines)
                    text_blocks.append(
                        TextBlock(
                            block_id=f"BLK-{source.source_id}-{block_idx}",
                            source_id=source.source_id,
                            text=para_text,
                            location=LocationInfo(section=current_section),
                            block_type="paragraph"
                        )
                    )
                    block_idx += 1
                    current_paragraph_lines = []
                continue

            # Detect markdown headers or section labels
            header_match = re.match(r"^(#{1,4}\s+|[A-Z\s]{4,30}:|===|---)", line_str)
            if header_match or (len(line_str) < 50 and line_str.endswith(":")):
                if current_paragraph_lines:
                    para_text = " ".join(current_paragraph_lines)
                    text_blocks.append(
                        TextBlock(
                            block_id=f"BLK-{source.source_id}-{block_idx}",
                            source_id=source.source_id,
                            text=para_text,
                            location=LocationInfo(section=current_section),
                            block_type="paragraph"
                        )
                    )
                    block_idx += 1
                    current_paragraph_lines = []
                
                current_section = line_str.lstrip("#").strip().rstrip(":")
                continue

            current_paragraph_lines.append(line_str)

        if current_paragraph_lines:
            para_text = " ".join(current_paragraph_lines)
            text_blocks.append(
                TextBlock(
                    block_id=f"BLK-{source.source_id}-{block_idx}",
                    source_id=source.source_id,
                    text=para_text,
                    location=LocationInfo(section=current_section),
                    block_type="paragraph"
                )
            )

        unique_blocks = remove_duplicate_text_blocks(text_blocks)
        source.status = SourceStatus.PROCESSED

        return Document(
            document_id=f"DOC-{source.source_id}",
            source_id=source.source_id,
            title=source.source_name,
            text_blocks=unique_blocks,
            tables=[],
            raw_text=text_content
        )
