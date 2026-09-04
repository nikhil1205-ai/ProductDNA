"""
Module 3 URL / HTML Content Evidence Line Extractor
"""

import uuid
from typing import List, Set
from .base import BaseExtractor
from ..models.document_models import Document
from ..models.extraction_models import EvidenceItem, EvidenceType, ExtractionMethod
from Evidence_collection_sources_module_2.models.source_models import SourceType

class URLExtractor(BaseExtractor):
    """
    URL Content Evidence Extractor.
    Extracts visible textual evidence statements strictly from URL web page documents,
    filtering out navigation and boilerplate text.
    """
    
    BOILERPLATE_KEYWORDS = {
        "cookie", "privacy policy", "terms of use", "all rights reserved",
        "copyright", "navigation", "javascript", "login", "register",
        "sign in", "cart", "checkout", "search"
    }

    def extract(self, document: Document) -> List[EvidenceItem]:
        src_type = document.metadata.get("source_type")
        if src_type not in (SourceType.URL, "url"):
            return []

        if not document.raw_text or len(document.raw_text.strip()) < 10:
            return []

        extracted: List[EvidenceItem] = []
        seen: Set[str] = set()

        for block in document.text_blocks:
            text = block.text.strip()
            if not text:
                continue

            lines = text.split("\n")
            for line_idx, line in enumerate(lines, start=1):
                line_clean = line.strip()
                if not line_clean or len(line_clean) < 15:
                    continue

                line_lower = line_clean.lower()
                if any(bp in line_lower for bp in self.BOILERPLATE_KEYWORDS):
                    continue

                if line_lower not in seen:
                    seen.add(line_lower)
                    item = EvidenceItem(
                        evidence_id=f"EV-URL-{uuid.uuid4().hex[:6].upper()}",
                        source_id=document.source_id,
                        source_type="url",
                        evidence_type=EvidenceType.SENTENCE if "." in line_clean else EvidenceType.LINE,
                        text=line_clean,
                        section=block.location.section,
                        line_number=block.location.line_start or line_idx,
                        extraction_method=ExtractionMethod.HTML_PARSER
                    )
                    extracted.append(item)

        return extracted
