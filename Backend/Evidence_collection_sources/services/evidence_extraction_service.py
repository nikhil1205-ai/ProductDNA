"""
Module 4 Main Service Orchestrator: Evidence Extraction Service
"""

import time
import uuid
import concurrent.futures
from typing import Dict, Any, List, Optional, Set

from ..models.source_models import SourceInput, Source, SourceType, SourceStatus, SourceOrigin
from ..models.document_models import Document
from ..models.extraction_models import ExtractorEvidenceResult, EvidenceContainer
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
from ..extractors.url_extractor import URLExtractor

ENABLE_HASH_DEDUPLICATION = True

class EvidenceExtractionService:
    """
    Main Service Orchestrator for Module 4.
    Receives resolved product information from Module 2 and user-provided sources,
    processes content, extracts evidence text across 4 extractors, and returns Structured Evidence.
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
        self.url_extractor = URLExtractor()

    def process(self, request_payload: Dict[str, Any]) -> StructuredEvidence:
        """
        Orchestrate Module 4 Pipeline:
        Intake -> Processing -> Evidence Extraction -> Evidence Output.
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

        # 3. Source Intake & Processing
        sources: List[Source] = []
        documents: List[Document] = []
        warnings: List[ProcessingWarning] = []
        seen_hashes: Set[str] = set()

        source_counter = 1
        source_name_map: Dict[str, str] = {}
        
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

            sources.append(collected_source)
            source_name_map[src_id] = collected_source.source_name

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

            # Step B: Document Processing
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

        # 4. Evidence Extraction across 4 Extractors
        pattern_data: List[str] = []
        pattern_sources: List[str] = []

        table_data: List[str] = []
        table_sources: List[str] = []

        url_data: List[str] = []
        url_sources: List[str] = []

        llm_data: List[str] = []
        llm_sources: List[str] = []

        for doc in documents:
            src_name = source_name_map.get(doc.source_id, doc.title or doc.source_id)

            # Pattern Extractor
            p_items = self.pattern_extractor.extract(doc)
            if p_items:
                pattern_data.extend(p_items)
                if src_name not in pattern_sources:
                    pattern_sources.append(src_name)

            # Table Extractor
            t_items = self.table_extractor.extract(doc)
            if t_items:
                table_data.extend(t_items)
                if src_name not in table_sources:
                    table_sources.append(src_name)

            # URL Extractor
            u_items = self.url_extractor.extract(doc)
            if u_items:
                url_data.extend(u_items)
                if src_name not in url_sources:
                    url_sources.append(src_name)

            # LLM Extractor
            l_items = self.llm_extractor.extract(doc)
            if l_items:
                llm_data.extend(l_items)
                if src_name not in llm_sources:
                    llm_sources.append(src_name)

        evidence = EvidenceContainer(
            pattern_extractor=ExtractorEvidenceResult(
                extractor_data=pattern_data,
                sources=pattern_sources
            ),
            table_extractor=ExtractorEvidenceResult(
                extractor_data=table_data,
                sources=table_sources
            ),
            url_extractor=ExtractorEvidenceResult(
                extractor_data=url_data,
                sources=url_sources
            ),
            llm_extractor=ExtractorEvidenceResult(
                extractor_data=llm_data,
                sources=llm_sources
            )
        )

        total_extracted = len(pattern_data) + len(table_data) + len(url_data) + len(llm_data)

        # 5. Build Processing Summary
        elapsed_seconds = round(time.time() - start_time, 3)
        processed_count = sum(1 for s in sources if s.status == SourceStatus.PROCESSED)

        summary = ProcessingSummary(
            sources_received=len(user_source_inputs),
            sources_processed=processed_count,
            evidence_items_extracted=total_extracted,
            warnings=warnings,
            processing_time_seconds=elapsed_seconds
        )

        return StructuredEvidence(
            request_id=req_id,
            product_identity=identity,
            evidence=evidence,
            processing_summary=summary
        )
