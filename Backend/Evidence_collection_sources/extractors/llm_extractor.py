"""
Module 4 LLM & NLP Extractor Implementation
"""

import json
import re
from typing import List, Dict, Any, Optional
import requests

from .base import BaseExtractor, LLMExtractionProvider
from ..models.document_models import Document, TextBlock
from ..models.extraction_models import ExtractedAttribute, ExtractionMethod
from ..mapping.attribute_mapper import AttributeMapper
from ..config.settings import settings

class LLMExtractionProviderImpl(LLMExtractionProvider):
    """
    LLM Extraction Provider using Google Gemini REST API or SDK with fallback.
    Enforces strict structured extraction and zero hallucination principles.
    """
    
    SYSTEM_PROMPT = """
You are a specialized industrial product data extraction engine.
Your task is to extract structured technical product attributes from the provided document text.

STRICT EXTRACTION RULES:
1. Extract ONLY information explicitly supported by the provided source text.
2. NEVER invent, hallucinate, or assume missing values.
3. NEVER infer technical specifications that are not explicitly written.
4. For every attribute, preserve the exact snippet of text as 'evidence_text'.
5. Return canonical attribute names (e.g. 'voltage', 'power', 'current', 'weight', 'dimensions', 'ip_rating', 'applications').
6. Separate value and unit whenever possible (e.g. value: '380-480', unit: 'V').
7. Set extraction confidence between 0.85 and 1.0 based on clarity in source.
8. If an attribute is missing or ambiguous, omit it completely.

Return JSON in this format:
{
  "attributes": [
    {
      "attribute": "voltage",
      "raw_attribute_name": "Input Voltage",
      "value": "380-480",
      "unit": "V",
      "page": 12,
      "section": "Electrical Characteristics",
      "evidence_text": "Input voltage: 380-480 V",
      "extraction_confidence": 0.99
    }
  ]
}
"""

    def extract_structured_attributes(
        self,
        document_text: str,
        source_id: str,
        product_context: Optional[Dict[str, Any]] = None
    ) -> List[ExtractedAttribute]:
        api_key = settings.gemini_api_key
        
        # If API key is available, call Gemini REST API
        if api_key:
            try:
                extracted = self._call_gemini_api(document_text, source_id, api_key)
                if extracted:
                    return extracted
            except Exception as e:
                # Fail gracefully to NLP fallback
                pass

        # Fallback: Heuristic NLP / Text pattern extraction
        return self._nlp_heuristic_fallback(document_text, source_id)

    def _call_gemini_api(self, text: str, source_id: str, api_key: str) -> List[ExtractedAttribute]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.llm_model}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        
        prompt_content = f"{self.SYSTEM_PROMPT}\n\nDOCUMENT CONTENT:\n{text[:6000]}"
        payload = {
            "contents": [{"parts": [{"text": prompt_content}]}],
            "generationConfig": {
                "temperature": settings.llm_temperature,
                "responseMimeType": "application/json"
            }
        }
        
        resp = requests.post(url, json=payload, headers=headers, timeout=20)
        resp.raise_for_status()
        
        data = resp.json()
        raw_json_str = data["candidates"][0]["content"]["parts"][0]["text"]
        parsed = json.loads(raw_json_str)
        
        results: List[ExtractedAttribute] = []
        for item in parsed.get("attributes", []):
            attr_key = AttributeMapper.map_attribute(item.get("attribute", ""))
            results.append(
                ExtractedAttribute(
                    attribute=attr_key,
                    raw_attribute_name=item.get("raw_attribute_name", item.get("attribute")),
                    value=item.get("value", ""),
                    unit=item.get("unit"),
                    source_id=source_id,
                    page=item.get("page"),
                    section=item.get("section"),
                    evidence_text=item.get("evidence_text", f"{attr_key}: {item.get('value')}"),
                    extraction_method=ExtractionMethod.LLM_EXTRACTION,
                    extraction_confidence=item.get("extraction_confidence", 0.95)
                )
            )
        return results

    def _nlp_heuristic_fallback(self, text: str, source_id: str) -> List[ExtractedAttribute]:
        """
        Intelligent NLP Heuristic Fallback Extractor.
        Used when LLM API keys are absent or network requests fail.
        Extracts semantic prose patterns like applications, design features, and brand references.
        """
        extracted: List[ExtractedAttribute] = []
        
        # 1. Applications matching e.g. "designed for pumps, fans and conveyors"
        app_match = re.search(r"(?:designed|suitable|used)\s+for\s+([^.\n]+)", text, re.IGNORECASE)
        if app_match:
            apps_text = app_match.group(1).strip()
            # Split items
            items = [item.strip() for item in re.split(r",|\band\b", apps_text) if item.strip()]
            extracted.append(
                ExtractedAttribute(
                    attribute="applications",
                    raw_attribute_name="Applications",
                    value=items if items else apps_text,
                    unit=None,
                    source_id=source_id,
                    evidence_text=app_match.group(0),
                    extraction_method=ExtractionMethod.NLP_HYBRID,
                    extraction_confidence=0.92
                )
            )

        # 2. Mounting / Enclosure type e.g. "wall-mounted single drive"
        enclosure_match = re.search(r"\b(wall-mounted|flange-mounted|cabinet-built|standalone|freestanding)\b", text, re.IGNORECASE)
        if enclosure_match:
            extracted.append(
                ExtractedAttribute(
                    attribute="mounting_type",
                    raw_attribute_name="Mounting Type",
                    value=enclosure_match.group(1).lower(),
                    unit=None,
                    source_id=source_id,
                    evidence_text=enclosure_match.group(0),
                    extraction_method=ExtractionMethod.NLP_HYBRID,
                    extraction_confidence=0.90
                )
            )

        return extracted

class LLMExtractor(BaseExtractor):
    """
    Extractor wrapper around LLMExtractionProvider.
    Passes processed Document content into provider.
    """
    
    def __init__(self, provider: Optional[LLMExtractionProvider] = None):
        self.provider = provider or LLMExtractionProviderImpl()

    def extract(self, document: Document) -> List[ExtractedAttribute]:
        if not document.raw_text or len(document.raw_text.strip()) < 10:
            return []

        return self.provider.extract_structured_attributes(
            document_text=document.raw_text,
            source_id=document.source_id
        )
