"""
Module 3 Service Orchestrator: Evidence Extraction Service
"""

import time
import uuid
import re
from typing import Dict, Any, List, Optional, Set
from pathlib import Path

from Evidence_collection_sources_module_2.models.source_models import SourceInput, Source, SourceType, SourceStatus
from Evidence_collection_sources_module_2.collectors.url_collector import URLCollector
from Evidence_collection_sources_module_2.collectors.pdf_collector import PDFCollector
from Evidence_collection_sources_module_2.collectors.text_collector import TextCollector
from Evidence_collection_sources_module_2.services.resource_manager import ResourceManager

from ..models.document_models import Document
from ..models.extraction_models import EvidenceItem, EvidenceType, ExtractionMethod
from ..models.response_models import StructuredEvidence

from ..processors.url_processor import URLProcessor
from ..processors.pdf_processor import PDFProcessor
from ..processors.text_processor import TextProcessor

from ..extractors.pattern_extractor import PatternExtractor
from ..extractors.table_extractor import TableExtractor
from ..extractors.llm_extractor import LLMExtractor
from ..extractors.url_extractor import URLExtractor
from ..extractors.identifier_extractor import IdentifierExtractor

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "input_data" / "Module_3_Extracted_Evidence_data"

class EvidenceExtractionService:
    """
    Main Service Orchestrator for Evidence Extraction (Module 3).
    Intakes Module 2 collected resources, parses documents, extracts source-grounded evidence units,
    saves structured output JSON to Backend/input_data/Module_3_Extracted_Evidence_data/,
    and returns Structured Evidence matching the strict output schema.
    """

    def __init__(self):
        self.resource_manager = ResourceManager()
        self.url_collector = URLCollector()
        self.pdf_collector = PDFCollector()
        self.text_collector = TextCollector()

        self.url_processor = URLProcessor()
        self.pdf_processor = PDFProcessor()
        self.text_processor = TextProcessor()

        self.identifier_extractor = IdentifierExtractor()
        self.pattern_extractor = PatternExtractor()
        self.table_extractor = TableExtractor()
        self.url_extractor = URLExtractor()
        self.llm_extractor = LLMExtractor()

    def process(self, request_payload: Dict[str, Any]) -> StructuredEvidence:
        product_id = request_payload.get("product_id") or request_payload.get("product", {}).get("product_id") or "PROD-001"

        user_source_inputs: List[SourceInput] = []
        raw_sources = request_payload.get("sources", [])
        
        for idx, src in enumerate(raw_sources):
            if isinstance(src, dict):
                src_obj = SourceInput(**src)
                user_source_inputs.append(src_obj)
            elif isinstance(src, SourceInput):
                user_source_inputs.append(src)

        sources: List[Source] = []
        documents: List[Document] = []

        source_counter = 1
        
        for src_input in user_source_inputs:
            src_id = f"SRC-{source_counter:03d}"
            source_counter += 1
            
            if src_input.type == SourceType.URL:
                collected_source = self.url_collector.collect(src_input, src_id)
            elif src_input.type == SourceType.PDF:
                collected_source = self.pdf_collector.collect(src_input, src_id)
            else:
                collected_source = self.text_collector.collect(src_input, src_id)

            sources.append(collected_source)

            if collected_source.status == SourceStatus.FAILED:
                continue

            if collected_source.source_type == SourceType.URL:
                doc = self.url_processor.process(collected_source, src_input)
            elif collected_source.source_type == SourceType.PDF:
                doc = self.pdf_processor.process(collected_source, src_input)
            else:
                doc = self.text_processor.process(collected_source, src_input)

            if collected_source.status == SourceStatus.FAILED:
                continue

            documents.append(doc)

        all_extracted_items: List[EvidenceItem] = []
        seen_texts: Set[str] = set()

        # Deterministic and fallback extraction per document
        for doc in documents:
            doc_src_type = str(doc.metadata.get("source_type", "text")).lower()
            doc_parser_method = (
                ExtractionMethod.DOCUMENT_PARSER if doc_src_type == "pdf"
                else ExtractionMethod.HTML_PARSER if doc_src_type == "url"
                else ExtractionMethod.TEXT_PARSER
            )

            # 1. Deterministic Identifier Extraction
            try:
                id_items = self.identifier_extractor.extract(doc)
                for item in id_items:
                    dedup_key = item.text.strip().lower()
                    if dedup_key not in seen_texts:
                        seen_texts.add(dedup_key)
                        all_extracted_items.append(item)
            except Exception:
                pass

            # 2. Deterministic Pattern Extraction (Key-Value lines)
            try:
                p_items = self.pattern_extractor.extract(doc)
                for item in p_items:
                    dedup_key = item.text.strip().lower()
                    if dedup_key not in seen_texts:
                        seen_texts.add(dedup_key)
                        all_extracted_items.append(item)
            except Exception:
                pass

            # 3. Deterministic Table Extraction
            try:
                t_items = self.table_extractor.extract(doc)
                for item in t_items:
                    dedup_key = item.text.strip().lower()
                    if dedup_key not in seen_texts:
                        seen_texts.add(dedup_key)
                        all_extracted_items.append(item)
            except Exception:
                pass

            # 4. Deterministic URL Line Noise Filtering (if URL)
            if doc_src_type == "url":
                try:
                    u_items = self.url_extractor.extract(doc)
                    for item in u_items:
                        dedup_key = item.text.strip().lower()
                        if dedup_key not in seen_texts:
                            seen_texts.add(dedup_key)
                            all_extracted_items.append(item)
                except Exception:
                    pass

            # 5. Prose Sentence Extraction via Document / HTML / Text Parser
            prose_count_before = len(all_extracted_items)
            for block in doc.text_blocks:
                sentences = re.split(r'(?<=[.!?])\s+', block.text.strip())
                for line_idx, sent in enumerate(sentences, start=1):
                    clean_sent = sent.strip()
                    if len(clean_sent) >= 12:
                        dedup_key = clean_sent.lower()
                        if dedup_key not in seen_texts:
                            seen_texts.add(dedup_key)
                            item = EvidenceItem(
                                evidence_id=f"EV-PRS-{uuid.uuid4().hex[:6].upper()}",
                                source_id=doc.source_id,
                                source_type=doc_src_type,
                                evidence_type=EvidenceType.SENTENCE,
                                text=clean_sent,
                                page_number=block.location.page,
                                section=block.location.section,
                                line_number=block.location.line_start or line_idx,
                                extraction_method=doc_parser_method
                            )
                            all_extracted_items.append(item)

            # 6. Fallback Lightweight LLM Extraction for unstructured content
            if len(all_extracted_items) - prose_count_before < 2 and len(doc.raw_text) > 50:
                try:
                    llm_items = self.llm_extractor.extract(doc)
                    for item in llm_items:
                        dedup_key = item.text.strip().lower()
                        if dedup_key not in seen_texts:
                            seen_texts.add(dedup_key)
                            all_extracted_items.append(item)
                except Exception:
                    pass

        # Build categorized evidence_data structure matching Section 10 contract
        pdf_data: List[str] = []
        pdf_page: Optional[int] = None
        
        url_data: List[str] = []
        text_data: List[str] = []
        llm_data: List[str] = []
        llm_page: Optional[int] = None

        for item in all_extracted_items:
            if item.extraction_method == ExtractionMethod.LLM:
                llm_data.append(item.text)
                if item.page_number and llm_page is None:
                    llm_page = item.page_number
            elif item.source_type == "pdf":
                pdf_data.append(item.text)
                if item.page_number and pdf_page is None:
                    pdf_page = item.page_number
            elif item.source_type == "url":
                url_data.append(item.text)
            else:
                text_data.append(item.text)

        evidence_data: Dict[str, Any] = {
            "pdf": {
                "data": pdf_data,
                "page_number": pdf_page,
                "extraction_method": "document_parser"
            },
            "url": {
                "data": url_data,
                "page_number": None,
                "extraction_method": "html_parser"
            },
            "text": {
                "data": text_data,
                "page_number": None,
                "extraction_method": "text_parser"
            },
            "llm": {
                "data": llm_data,
                "page_number": llm_page,
                "extraction_method": "llm"
            }
        }

        processed_count = sum(1 for s in sources if s.status == SourceStatus.PROCESSED)
        overall_status = (
            "EXTRACTED" if processed_count == len(sources) and sources
            else "PARTIAL" if processed_count > 0
            else "FAILED"
        )

        source_ids_list = [s.source_id for s in sources]

        result = StructuredEvidence(
            product_id=product_id,
            source_ids=source_ids_list,
            evidence_data=evidence_data,
            status=overall_status
        )

        try:
            import os
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            safe_filename = re.sub(r'[^A-Za-z0-9_\-]', '_', str(product_id))
            file_path = OUTPUT_DIR / f"{safe_filename}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(result.model_dump_json(indent=2))
        except Exception as e:
            print(f"Warning: Failed to save Module 3 evidence output file: {e}")

        return result
