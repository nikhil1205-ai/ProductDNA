"""
Module 3 Extractor Base & Provider Interfaces
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..models.document_models import Document
from ..models.extraction_models import EvidenceItem

class BaseExtractor(ABC):
    """
    Abstract Base Class for Evidence Extractors.
    Extracts structured EvidenceItem objects (or evidence statements) from processed Document objects.
    """
    
    @abstractmethod
    def extract(self, document: Document) -> List[EvidenceItem]:
        """Extract evidence units with provenance from document."""
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
        """Use LLM to extract source-grounded evidence sentences."""
        pass
