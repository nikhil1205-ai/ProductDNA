import csv
import io
import re
from typing import List

from .base import BaseProcessor
from .content_cleaner import clean_whitespace, remove_duplicate_text_blocks
from ..models.source_models import Source, SourceInput, SourceStatus
from ..models.document_models import Document, Section, TextBlock, Table, LocationInfo

class TextProcessor(BaseProcessor):
    """
    Processor for Plain Text, Technical Text, and CSV documents.
    Segments sections by headers and creates TextBlock / Table representations.
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
            return Document(
                document_id=f"DOC-{source.source_id}",
                source_id=source.source_id,
                metadata={"source_type": source.source_type}
            )

        # Check if file is a CSV or tabular file
        is_csv = source.source_name.lower().endswith(".csv") or source_input.subtype == "csv"
        if not is_csv and "\n" in text_content:
            first_line = text_content.strip().split("\n")[0]
            if "," in first_line and len(first_line.split(",")) >= 2 and ("attribute" in first_line.lower() or "value" in first_line.lower()):
                is_csv = True

        if is_csv:
            try:
                reader = list(csv.reader(io.StringIO(text_content)))
                if reader:
                    headers = [h.strip() for h in reader[0]]
                    rows = [[cell.strip() for cell in row] for row in reader[1:] if any(c.strip() for c in row)]
                    
                    kv_pairs = {}
                    for r in rows:
                        if len(r) >= 2 and r[0] and r[1]:
                            val_str = f"{r[1]} {r[2]}".strip() if len(r) >= 3 and r[2] else r[1]
                            kv_pairs[r[0]] = val_str

                    table_obj = Table(
                        table_id=f"TBL-{source.source_id}-1",
                        source_id=source.source_id,
                        title=source.source_name,
                        headers=headers,
                        rows=rows,
                        kv_pairs=kv_pairs
                    )
                    source.status = SourceStatus.PROCESSED
                    return Document(
                        document_id=f"DOC-{source.source_id}",
                        source_id=source.source_id,
                        title=source.source_name,
                        text_blocks=[],
                        tables=[table_obj],
                        raw_text=text_content,
                        metadata={"source_type": source.source_type, "is_csv": True}
                    )
            except Exception as e:
                print(f"CSV processing fallback to text: {e}")

        text_blocks: List[TextBlock] = []
        current_section = "General Specifications"
        block_idx = 1

        lines = text_content.split("\n")
        current_paragraph_lines: List[str] = []

        for line in lines:
            line_str = line.strip()
            if not line_str:
                if current_paragraph_lines:
                    para_text = "\n".join(current_paragraph_lines)
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
            if header_match or (len(line_str) < 50 and line_str.endswith(":") and not ":" in line_str[:-1]):
                if current_paragraph_lines:
                    para_text = "\n".join(current_paragraph_lines)
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
            para_text = "\n".join(current_paragraph_lines)
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
            raw_text=text_content,
            metadata={"source_type": source.source_type}
        )

