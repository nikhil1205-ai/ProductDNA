"""
Module 4 Main Service Orchestrator: Evidence Extraction Service
"""

import time
import uuid
from typing import Dict, Any, List, Optional, Set

from ..models.source_models import SourceInput, Source, SourceType, SourceStatus, SourceOrigin
from ..models.document_models import Document
from ..models.extraction_models import ExtractedAttribute
from ..models.response_models import (
    StructuredEvidence,
    ProductIdentity,
    ProcessingSummary,
    ProcessingWarning,
    Module4Response
)
from ..collectors.url_collector import URLCollector
from ..collectors.pdf_collector import PDFCollector
from ..collectors.text_collector import TextCollector

from ..processors.url_processor import URLProcessor
from ..processors.pdf_processor import PDFProcessor
from ..processors.text_processor import TextProcessor

from ..extractors.pattern_extractor import PatternExtractor
from ..extractors.table_extractor import TableExtractor
from ..extractors.llm_extractor import LLMExtractor

ENABLE_HASH_DEDUPLICATION = True

class EvidenceExtractionService:
    """
    Main Service Orchestrator for Module 4.
    Receives resolved product information from Module 2 and user-provided sources,
    processes content, extracts attributes, maps canonical names, and returns Structured Evidence.
    """

    def __init__(self):
        # Collectors
        self.url_collector = URLCollector()
        self.pdf_collector = PDFCollector()
        self.text_collector = TextCollector()

        # Processors
        self.url_processor = URLProcessor()
        self.pdf_processor = PDFProcessor()
        self.text_processor = TextProcessor()

        # Extractors
        self.pattern_extractor = PatternExtractor()
        self.table_extractor = TableExtractor()
        self.llm_extractor = LLMExtractor()

    def process(self, request_payload: Dict[str, Any]) -> StructuredEvidence:
        """
        Orchestrate Module 4 Pipeline:
        Intake -> Processing -> Extraction -> Mapping -> Validation -> Output.
        """
        start_time = time.time()
        
        # 1. Parse Request ID & Product Identity from Module 2 input
        req_id = request_payload.get("request_id") or f"REQ-{uuid.uuid4().hex[:8].upper()}"
        
        identity_dict = request_payload.get("identity") or request_payload.get("product_identity") or {}
        if not identity_dict and "product" in request_payload and isinstance(request_payload["product"], dict):
            identity_dict = request_payload["product"]

        identity = ProductIdentity(
            product_name=identity_dict.get("product_name"),
            brand=identity_dict.get("brand"),
            manufacturer=identity_dict.get("manufacturer"),
            model=identity_dict.get("model"),
            sku=identity_dict.get("sku"),
            part_number=identity_dict.get("part_number"),
            category=identity_dict.get("category")
        )

        # 2. Extract sources from request payload
        user_source_inputs: List[SourceInput] = []
        raw_sources = request_payload.get("sources", [])
        
        for idx, src in enumerate(raw_sources):
            if isinstance(src, dict):
                src_obj = SourceInput(**src)
                user_source_inputs.append(src_obj)
            elif isinstance(src, SourceInput):
                user_source_inputs.append(src)

        # 3. Source Intake & Deduplication
        sources: List[Source] = []
        documents: List[Document] = []
        warnings: List[ProcessingWarning] = []
        seen_hashes: Set[str] = set()

        source_counter = 1
        
        for src_input in user_source_inputs:
            src_id = f"SRC-{source_counter:03d}"
            source_counter += 1
            
            # Step A: Collect
            if src_input.type == SourceType.URL:
                collected_source = self.url_collector.collect(src_input, src_id)
            elif src_input.type == SourceType.PDF:
                collected_source = self.pdf_collector.collect(src_input, src_id)
            else:
                collected_source = self.text_collector.collect(src_input, src_id)

            # Step B: Hash Deduplication
            if ENABLE_HASH_DEDUPLICATION and collected_source.metadata and collected_source.metadata.content_hash:
                chash = collected_source.metadata.content_hash
                if chash in seen_hashes:
                    collected_source.status = SourceStatus.DUPLICATE
                    collected_source.error_message = "Duplicate document detected; skipping reprocessing."
                    sources.append(collected_source)
                    warnings.append(
                        ProcessingWarning(
                            source_id=src_id,
                            warning_code="DUPLICATE_SOURCE",
                            message=f"Duplicate content for source '{collected_source.source_name}'"
                        )
                    )
                    continue
                seen_hashes.add(chash)

            sources.append(collected_source)

            # Check collection failures
            if collected_source.status == SourceStatus.FAILED:
                warnings.append(
                    ProcessingWarning(
                        source_id=src_id,
                        warning_code="SOURCE_INTAKE_FAILED",
                        message=collected_source.error_message or "Source intake failed."
                    )
                )
                continue

            # Step C: Document Processing
            if collected_source.source_type == SourceType.URL:
                doc = self.url_processor.process(collected_source, src_input)
            elif collected_source.source_type == SourceType.PDF:
                doc = self.pdf_processor.process(collected_source, src_input)
            else:
                doc = self.text_processor.process(collected_source, src_input)

            if collected_source.status == SourceStatus.FAILED:
                warnings.append(
                    ProcessingWarning(
                        source_id=src_id,
                        warning_code="DOCUMENT_PROCESSING_FAILED",
                        message=collected_source.error_message or "Document processing failed."
                    )
                )
                continue

            documents.append(doc)

        # 4. Structured Extraction across all processed documents
        all_attributes: List[ExtractedAttribute] = []
        
        for doc in documents:
            # Pattern Extraction
            pattern_attrs = self.pattern_extractor.extract(doc)
            all_attributes.extend(pattern_attrs)

            # Table Extraction
            table_attrs = self.table_extractor.extract(doc)
            all_attributes.extend(table_attrs)

            # LLM / Hybrid Extraction
            llm_attrs = self.llm_extractor.extract(doc)
            all_attributes.extend(llm_attrs)

        # 5. Deduplicate extracted attributes per source_id + canonical name
        unique_attributes: List[ExtractedAttribute] = []
        attr_dedup_keys: Set[str] = set()

        for attr in all_attributes:
            key = f"{attr.source_id}:{attr.attribute}:{str(attr.value).lower().strip()}"
            if key not in attr_dedup_keys:
                attr_dedup_keys.add(key)
                unique_attributes.append(attr)

        # 6. Build Processing Summary
        elapsed_seconds = round(time.time() - start_time, 3)
        processed_count = sum(1 for s in sources if s.status == SourceStatus.PROCESSED)

        summary = ProcessingSummary(
            sources_received=len(user_source_inputs),
            sources_processed=processed_count,
            attributes_extracted=len(unique_attributes),
            warnings=warnings,
            processing_time_seconds=elapsed_seconds
        )

        status_str = "SUCCESS"
        if processed_count == 0 and len(user_source_inputs) > 0:
            status_str = "FAILED"
        elif len(warnings) > 0:
            status_str = "PARTIAL_SUCCESS"

        return StructuredEvidence(
            request_id=req_id,
            product_identity=identity,
            sources=sources,
            attributes=unique_attributes,
            processing_summary=summary,
            status=status_str
        )
