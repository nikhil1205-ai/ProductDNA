"""
Module 4 Collector & Retrieval Abstraction Interfaces
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from ..models.source_models import SourceInput, Source, SourceMetadata, SourceType, SourceStatus
from ..models.document_models import Document

class BaseSourceCollector(ABC):
    """
    Abstract Base Class for Source Intake Collectors.
    Handles acquisition and initial intake of product sources.
    """
    
    @abstractmethod
    def collect(self, source_input: SourceInput, source_id: str) -> Source:
        """Intake source and populate initial metadata."""
        pass

class BaseRetrievalService(ABC):
    """
    Future-ready Retrieval Service Interface.
    Enables future RAG, Vector Search, or Hybrid Search services without breaking Module 4 core.
    """
    
    @abstractmethod
    def retrieve_content(self, source: Source) -> Dict[str, Any]:
        """Retrieve raw content from acquired source."""
        pass

    @abstractmethod
    def search_relevant_chunks(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Stub for future vector/RAG chunk search."""
        pass

class DirectRetrievalService(BaseRetrievalService):
    """
    Direct Targeted Source Retrieval Service (Current Implementation).
    Directly fetches and retrieves source content without vector indexing.
    """
    
    def retrieve_content(self, source: Source) -> Dict[str, Any]:
        return {"source_id": source.source_id, "retrieval_method": "direct"}

    def search_relevant_chunks(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        # RAG is not implemented in prototype phase
        return []

class VectorRetrievalService(BaseRetrievalService):
    """Future Extension Stub: Vector Search Retrieval Service."""
    def retrieve_content(self, source: Source) -> Dict[str, Any]:
        raise NotImplementedError("Vector DB retrieval will be implemented in future phase.")
        
    def search_relevant_chunks(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        raise NotImplementedError("Vector DB search will be implemented in future phase.")

class RAGRetrievalService(BaseRetrievalService):
    """Future Extension Stub: RAG Hybrid Retrieval Service."""
    def retrieve_content(self, source: Source) -> Dict[str, Any]:
        raise NotImplementedError("RAG retrieval will be implemented in future phase.")
        
    def search_relevant_chunks(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        raise NotImplementedError("RAG search will be implemented in future phase.")
