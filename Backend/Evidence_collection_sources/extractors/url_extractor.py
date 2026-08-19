from typing import List
from .base import BaseExtractor
from ..models.document_models import Document
from ..models.source_models import SourceType

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

    def extract(self, document: Document) -> List[str]:
        # URLExtractor MUST ONLY process actual URL sources
        src_type = document.metadata.get("source_type")
        if src_type not in (SourceType.URL, "url"):
            return []

        if not document.raw_text or len(document.raw_text.strip()) < 10:
            return []

        extracted: List[str] = []
        seen: set = set()

        for block in document.text_blocks:
            text = block.text.strip()
            if not text:
                continue

            lines = text.split("\n")
            for line in lines:
                line_clean = line.strip()
                if not line_clean or len(line_clean) < 15:
                    continue

                line_lower = line_clean.lower()
                # Skip boilerplate navigation / footer lines
                if any(bp in line_lower for bp in self.BOILERPLATE_KEYWORDS):
                    continue

                if line_lower not in seen:
                    seen.add(line_lower)
                    extracted.append(line_clean)

        return extracted

