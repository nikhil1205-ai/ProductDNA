# Module 4: Evidence Collection & Structured Extraction Engine

**ProductDNA — AI-Powered Product Intelligence Engine for Industrial Commerce**

Module 4 is the core **Evidence Collection & Structured Extraction Engine** of ProductDNA. It receives resolved product identity from Module 2 (handling `MATCHED`, `AMBIGUOUS`, or `NOT_FOUND` statuses), ingests user-provided multi-sources (PDF datasheets, Web URLs, plain text documents), cleans and normalizes content, performs hybrid attribute extraction (Regex patterns + Tabular key-values + LLM/NLP semantic extraction), maps extracted attribute labels to canonical names, validates output schemas using Pydantic, and returns traceable **Structured Evidence** for downstream evidence assessment (Module 6).

---

## 1. Architecture & Internal Pipeline

Module 4 executes a strict 8-step internal pipeline:

```
[Module 2 Output / Product Identity] + [User Product Sources]
                            ↓
                    1. Source Intake
                            ↓
                  2. Source Processing
                            ↓
                    3. Data Processing
                            ↓
               4. Content Normalization
                            ↓
              5. Document Understanding
                            ↓
               6. Structured Extraction (Hybrid)
                            ↓
                    7. Schema Mapping
                            ↓
               8. Pydantic Validation
                            ↓
                 [STRUCTURED EVIDENCE]
```

---

## 2. Directory Structure

```
Backend/Evidence_collection_sources/
├── __init__.py
├── api/
│   ├── __init__.py
│   └── routes.py                      # FastAPI endpoint (/api/evidence/extract)
├── config/
│   ├── __init__.py
│   └── settings.py                    # Module 4 settings & LLM configuration
├── models/
│   ├── __init__.py
│   ├── source_models.py               # Source, SourceMetadata, SourceType, SourceStatus
│   ├── document_models.py             # Document, LocationInfo, TextBlock, Table, Section
│   ├── extraction_models.py           # ExtractedAttribute, ExtractionMethod
│   └── response_models.py             # StructuredEvidence, Module4Request, Module4Response
├── collectors/
│   ├── __init__.py
│   ├── base.py                        # BaseSourceCollector & Future RAG Interfaces
│   ├── url_collector.py               # HTTP fetch, redirect & timeout handling
│   ├── pdf_collector.py               # PDF byte loading, page count & checksum
│   └── text_collector.py              # Text document reader
├── processors/
│   ├── __init__.py
│   ├── base.py                        # BaseProcessor interface
│   ├── url_processor.py               # HTML cleaning, nav removal & title/table parsing
│   ├── pdf_processor.py               # Page-by-page text & table extraction (PyMuPDF & pdfplumber)
│   ├── text_processor.py              # Section header segmentation & text cleaning
│   └── content_cleaner.py             # Whitespace cleanup & content hash deduplication
├── extractors/
│   ├── __init__.py
│   ├── base.py                        # BaseExtractor & LLMExtractionProvider
│   ├── pattern_extractor.py           # Regex rules for voltage, power, current, IP rating, SKU, etc.
│   ├── table_extractor.py             # Direct key-value table attribute extractor
│   └── llm_extractor.py               # Gemini SDK structured output with NLP fallback
├── mapping/
│   ├── __init__.py
│   ├── canonical_attributes.py        # Canonical attribute definitions & category schemas
│   └── attribute_mapper.py            # Synonyms & fuzzy canonical attribute mapping
├── schemas/
│   ├── __init__.py
│   └── structured_evidence.py         # Primary Pydantic export schemas
├── services/
│   ├── __init__.py
│   └── evidence_extraction_service.py # Core Orchestrator
├── tests/                             # Unit & Integration Test Suite
│   ├── test_url_processing.py
│   ├── test_pdf_processing.py
│   ├── test_text_processing.py
│   ├── test_extraction.py
│   ├── test_mapping.py
│   └── test_end_to_end.py
└── README.md
```

---

## 3. Supported Source Types

Module 4 supports three primary source types:
1. **URL / Website**: Web pages, product specification web pages.
2. **PDF Document**: Technical datasheets, product catalogs, engineering manuals (with page-level provenance tracking).
3. **Plain Text**: Raw technical specifications, plain text notes, markdown documents.

---

## 4. Input & Output Schemas

### Example Input (Module 2 Output + Sources)
```json
{
  "request_id": "REQ-20260816-5D846135",
  "identity": {
    "product_name": "ABB ACS880 Industrial Drive",
    "brand": "ABB",
    "manufacturer": "ABB",
    "model": "ACS880-01-145A-3",
    "sku": "ACS880-01-145A-3",
    "category": "Industrial Drives"
  },
  "status": "AMBIGUOUS",
  "sources": [
    {
      "type": "pdf",
      "value": "acs880_datasheet.pdf",
      "name": "ACS880 Datasheet",
      "subtype": "technical_datasheet"
    },
    {
      "type": "text",
      "value": "Technical Notes: Mains frequency 50/60 Hz.",
      "name": "technical_notes.txt"
    }
  ]
}
```

### Example Output (Structured Evidence)
```json
{
  "request_id": "REQ-20260816-5D846135",
  "product_identity": {
    "product_name": "ABB ACS880 Industrial Drive",
    "brand": "ABB",
    "manufacturer": "ABB",
    "model": "ACS880-01-145A-3",
    "sku": "ACS880-01-145A-3",
    "category": "Industrial Drives"
  },
  "sources": [
    {
      "source_id": "SRC-001",
      "source_type": "pdf",
      "source_name": "ACS880 Datasheet",
      "origin": "user_provided",
      "status": "processed"
    }
  ],
  "attributes": [
    {
      "attribute": "voltage",
      "raw_attribute_name": "Input Voltage",
      "value": "380-480",
      "unit": "V",
      "source_id": "SRC-001",
      "page": 1,
      "section": "Electrical Characteristics",
      "evidence_text": "Input voltage: 380-480 V",
      "extraction_method": "pattern_regex",
      "extraction_confidence": 0.99
    }
  ],
  "processing_summary": {
    "sources_received": 2,
    "sources_processed": 2,
    "attributes_extracted": 6,
    "warnings": [],
    "processing_time_seconds": 0.042
  },
  "status": "SUCCESS"
}
```

---

## 5. API Usage

FastAPI Endpoint:
`POST /api/evidence/extract`

Supports both `application/json` payloads and `multipart/form-data` file uploads.

---

## 6. Future RAG Extension

While RAG, Vector Search, and Knowledge Graphs are excluded from the current prototype phase, clean abstraction interfaces (`BaseRetrievalService`, `VectorRetrievalService`, `RAGRetrievalService`) are provided in `collectors/base.py`. Future developers can implement vector indexing without altering extraction, canonical mapping, or Pydantic validation logic.
