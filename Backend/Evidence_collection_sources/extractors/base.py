"""
Module 4 Extractor Base & Provider Interfaces
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..models.document_models import Document
from ..models.extraction_models import ExtractedAttribute

class BaseExtractor(ABC):
    """
    Abstract Base Class for Attribute Extractors.
    Extracts structured product attributes from processed Document objects.
    """
    
    @abstractmethod
    def extract(self, document: Document) -> List[ExtractedAttribute]:
        """Extract attributes from document."""
        pass

class LLMExtractionProvider(ABC):
    """
    Interface for LLM Extraction Providers.
    Decouples LLM SDK implementation details (Gemini, OpenAI, Mock) from extraction pipeline logic.
    """
    
    @abstractmethod
    def extract_structured_attributes(
        self,
        document_text: str,
        source_id: str,
        product_context: Optional[Dict[str, Any]] = None
    ) -> List[ExtractedAttribute]:
        """Use LLM to extract structured attributes with evidence provenance."""
        pass
