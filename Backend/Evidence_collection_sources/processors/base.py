"""
Module 4 Processor Abstract Base Class
"""

from abc import ABC, abstractmethod
from ..models.source_models import Source, SourceInput
from ..models.document_models import Document

class BaseProcessor(ABC):
    """
    Abstract Base Class for Document Processors.
    Transforms acquired raw content into Document structures (TextBlocks, Tables, Sections).
    """
    
    @abstractmethod
    def process(self, source: Source, source_input: SourceInput) -> Document:
        """Process raw content into a structured Document object."""
        pass
