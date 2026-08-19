"""
Module 4 Extractor Base & Provider Interfaces
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..models.document_models import Document

class BaseExtractor(ABC):
    """
    Abstract Base Class for Evidence Extractors.
    Extracts plain text/sentence evidence from processed Document objects.
    """
    
    @abstractmethod
    def extract(self, document: Document) -> List[str]:
        """Extract evidence text/sentences from document."""
        pass

class LLMExtractionProvider(ABC):
    """
    Interface for LLM Extraction Providers.
    Decouples LLM SDK implementation details from extraction pipeline logic.
    """
    
    @abstractmethod
    def extract_semantic_evidence(
        self,
        document_text: str,
        source_id: str,
        product_context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Use LLM to extract semantic evidence statements."""
        pass
