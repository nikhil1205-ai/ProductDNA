"""
Module 4 URL / Website Content Processor
"""

import re
from typing import List
from bs4 import BeautifulSoup

from .base import BaseProcessor
from .content_cleaner import clean_whitespace, remove_duplicate_text_blocks
from ..models.source_models import Source, SourceInput
from ..models.document_models import Document, Section, TextBlock, Table, LocationInfo

class URLProcessor(BaseProcessor):
    """
    Processor for Web / HTML content.
    Extracts page title, main textual content, tables, and removes boilerplate noise.
    """
    
    def process(self, source: Source, source_input: SourceInput) -> Document:
        raw_bytes = source_input.file_bytes
        html_str = ""
        
        if raw_bytes:
            try:
                html_str = raw_bytes.decode("utf-8", errors="replace")
            except Exception:
                html_str = str(raw_bytes)
        elif source_input.metadata.get("text_content"):
            html_str = source_input.metadata["text_content"]
        else:
            html_str = source_input.value

        soup = BeautifulSoup(html_str, "html.parser")
        
        # Extract title
        title_tag = soup.find("title")
        doc_title = title_tag.get_text(strip=True) if title_tag else source.source_name
        if doc_title and source.metadata:
            source.metadata.title = doc_title

        # Remove irrelevant noise elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "svg"]):
            element.decompose()

        text_blocks: List[TextBlock] = []
        tables: List[Table] = []
        sections: List[Section] = []
        
        current_section = "General Overview"
        block_idx = 1
        table_idx = 1

        # Process main body elements
        body = soup.find("body") or soup
        
        # Extract tables
        for html_table in body.find_all("table"):
            headers = []
            rows = []
            kv_pairs = {}
            
            # Extract headers
            th_tags = html_table.find_all("th")
            if th_tags:
                headers = [th.get_text(strip=True) for th in th_tags]

            # Extract rows
            tr_tags = html_table.find_all("tr")
            for tr in tr_tags:
                tds = tr.find_all("td")
                if not tds:
                    continue
                row_vals = [td.get_text(strip=True) for td in tds]
                if len(row_vals) >= 2:
                    kv_pairs[row_vals[0]] = row_vals[1]
                rows.append(row_vals)

            if rows or headers:
                table_obj = Table(
                    table_id=f"TBL-{source.source_id}-{table_idx}",
                    source_id=source.source_id,
                    title=f"Table {table_idx}",
                    headers=headers,
                    rows=rows,
                    kv_pairs=kv_pairs,
                    location=LocationInfo(section=current_section, table_index=table_idx)
                )
                tables.append(table_obj)
                table_idx += 1
            
            # Decompose table so its text isn't duplicated in paragraph parsing
            html_table.decompose()

        # Extract text blocks per paragraph / heading
        for elem in body.find_all(["h1", "h2", "h3", "h4", "p", "li", "div"]):
            text = elem.get_text(strip=True)
            if not text or len(text) < 3:
                continue
                
            tag_name = elem.name.lower()
            if tag_name in ["h1", "h2", "h3", "h4"]:
                current_section = text
                continue
                
            # Avoid container divs with huge text if already processed
            if tag_name == "div" and elem.find(["p", "h1", "h2", "h3", "div"]):
                continue

            cleaned_text = clean_whitespace(text)
            if cleaned_text:
                text_blocks.append(
                    TextBlock(
                        block_id=f"BLK-{source.source_id}-{block_idx}",
                        source_id=source.source_id,
                        text=cleaned_text,
                        location=LocationInfo(section=current_section),
                        block_type="bullet_item" if tag_name == "li" else "paragraph"
                    )
                )
                block_idx += 1

        # Deduplicate blocks
        unique_blocks = remove_duplicate_text_blocks(text_blocks)
        
        # Build full text string
        raw_text = "\n\n".join([b.text for b in unique_blocks])

        return Document(
            document_id=f"DOC-{source.source_id}",
            source_id=source.source_id,
            title=doc_title,
            text_blocks=unique_blocks,
            tables=tables,
            raw_text=raw_text,
            metadata={"source_type": source.source_type, "content_type": "text/html"}
        )
