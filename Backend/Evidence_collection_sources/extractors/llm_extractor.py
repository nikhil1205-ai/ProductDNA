"""
Module 4 LLM & NLP Extractor Implementation
"""

import json
from typing import List, Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

from .base import BaseExtractor, LLMExtractionProvider
from ..models.document_models import Document
from ..models.extraction_models import ExtractedAttribute, ExtractionMethod
from ..mapping.attribute_mapper import AttributeMapper
from ..config.llm_config import llm_config

class LLMExtractionProviderImpl(LLMExtractionProvider):
    """
    LLM Extraction Provider using Google Gemini REST API or SDK.
    Enforces strict structured extraction and zero hallucination principles.
    """
    
    SYSTEM_PROMPT = """
You are a specialized industrial product data extraction engine.
Your task is to extract structured technical product attributes from the provided document text.

STRICT EXTRACTION RULES:
1. Extract ONLY information explicitly supported by the provided source text.
2. NEVER invent, hallucinate, or assume missing values.
3. NEVER infer technical specifications that are not explicitly written.
4. Extract ANY meaningful product attribute present in the document regardless of product category.
5. Preserve the exact attribute name as it appears in the text as 'raw_attribute_name'.
6. Separate value and unit whenever possible.
7. For every attribute, preserve the exact snippet of text as 'evidence_text'.
8. Set extraction confidence between 0.85 and 1.0 based on clarity in source.
9. If an attribute is missing or ambiguous, omit it completely.

Return JSON in this format:
{
  "attributes": [
    {
      "attribute": "material",
      "raw_attribute_name": "Housing Material",
      "value": "Stainless Steel",
      "unit": null,
      "page": 1,
      "section": "Specifications",
      "evidence_text": "Housing Material: Stainless Steel",
      "extraction_confidence": 0.95
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
        api_key = llm_config.gemini_api_key
        
        # If API key is available, call Gemini API via Langchain
        if api_key:
            try:
                extracted = self._call_langchain_api(document_text, source_id, api_key)
                if extracted:
                    return extracted
            except Exception as e:
                # Fail gracefully
                print(f"LLM Extraction failed: {e}")
                pass

        return []

    def _call_langchain_api(self, text: str, source_id: str, api_key: str) -> List[ExtractedAttribute]:
        llm = ChatGoogleGenerativeAI(
            model=llm_config.llm_model,
            google_api_key=api_key,
            temperature=llm_config.llm_temperature
        )
        
        prompt_template = PromptTemplate.from_template(
            "{system_prompt}\n\nDOCUMENT CONTENT:\n{text}"
        )
        
        chain = prompt_template | llm
        
        # Truncate text to avoid token limits if necessary
        truncated_text = text[:6000]
        
        response = chain.invoke({
            "system_prompt": self.SYSTEM_PROMPT,
            "text": truncated_text
        })
        
        # Extract JSON from response. Sometimes LLMs return markdown code blocks.
        raw_json_str = response.content
        if raw_json_str.startswith("```json"):
            raw_json_str = raw_json_str[7:]
        if raw_json_str.endswith("```"):
            raw_json_str = raw_json_str[:-3]
            
        parsed = json.loads(raw_json_str.strip())
        
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
