"""
Module 2 Resource Manager Service: Coordinates Resource Intake, Collection, Integrity Checking, Storage & Tracking
"""

from typing import List, Optional
from ..models.source_models import SourceInput, Source, SourceType, SourceStatus
from ..collectors.pdf_collector import PDFCollector
from ..collectors.url_collector import URLCollector
from ..collectors.text_collector import TextCollector
from .resource_store import ResourceStore

class ResourceManager:
    """
    Service responsible for managing the intake lifecycle of product resources.
    Integrates collectors, SHA-256 duplicate detection, local storage in organization_sources/data_sources, and manifest management.
    """

    def __init__(self, store: Optional[ResourceStore] = None):
        self.store = store or ResourceStore()
        self.pdf_collector = PDFCollector()
        self.url_collector = URLCollector()
        self.text_collector = TextCollector()

    def add_resource(self, source_input: SourceInput) -> Source:
        """
        Receives a resource request, invokes the appropriate collector,
        performs SHA-256 duplicate check, saves files under organization_sources/data_sources, and returns the registered Source.
        """
        request_id = source_input.request_id or "REQ-001"
        candidate_source_id = self.store.get_next_source_id()

        # Step 1: Collect using existing collector
        if source_input.type == SourceType.URL:
            source = self.url_collector.collect(source_input, candidate_source_id)
        elif source_input.type == SourceType.PDF:
            source = self.pdf_collector.collect(source_input, candidate_source_id)
        elif source_input.type == SourceType.TEXT:
            source = self.text_collector.collect(source_input, candidate_source_id)
        else:
            # Fallback for unknown type
            source = self.text_collector.collect(source_input, candidate_source_id)

        source.request_id = request_id

        # Step 2: Handle collection failures gracefully
        if source.status == SourceStatus.FAILED:
            self.store.save_source(source, file_bytes=source_input.file_bytes)
            return source

        # Step 3: SHA-256 Duplicate Check
        content_hash = source.metadata.content_hash
        if content_hash:
            existing_match = self.store.find_by_content_hash(content_hash, request_id=request_id)
            if existing_match:
                source.status = SourceStatus.DUPLICATE
                source.error_message = f"Duplicate resource detected. Matches existing resource '{existing_match.source_id}'."
                self.store.save_source(source, file_bytes=source_input.file_bytes)
                return source

        # Step 4: Mark as PROCESSED and save to store
        source.status = SourceStatus.PROCESSED
        self.store.save_source(source, file_bytes=source_input.file_bytes)
        return source

    def get_resource(self, source_id: str) -> Optional[Source]:
        """
        Retrieves a single resource by source_id.
        """
        return self.store.get_source(source_id)

    def list_resources(self, request_id: Optional[str] = None) -> List[Source]:
        """
        Lists all registered resources, optionally filtered by request_id.
        """
        return self.store.list_sources(request_id=request_id)

    def delete_resource(self, source_id: str) -> bool:
        """
        Deletes a resource record and its stored files.
        """
        return self.store.delete_source(source_id)
