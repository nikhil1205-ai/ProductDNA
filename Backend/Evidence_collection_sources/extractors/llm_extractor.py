"""
Module 4 LLM Evidence Extractor Implementation
"""

import json
from typing import List, Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

from .base import BaseExtractor, LLMExtractionProvider
from ..models.document_models import Document
from ..config.llm_config import llm_config

class LLMExtractionProviderImpl(LLMExtractionProvider):
    """
    LLM Extraction Provider using Google Gemini REST API or SDK.
    Extracts semantic prose and text evidence statements without hallucination.
    """
    
    SYSTEM_PROMPT = """
You are a specialized product data evidence extraction engine.
Your task is to extract explicit semantic evidence statements and sentences describing the product from the provided document text.

STRICT EXTRACTION RULES:
1. Extract ONLY information explicitly supported by the provided source text.
2. NEVER invent, hallucinate, or assume missing information.
3. Return evidence as plain text statements/sentences.
4. Extract any meaningful product information (applications, mounting, operating conditions, features, etc.) regardless of product category.
5. Preserve source wording as closely as practical.

Return JSON in this format:
{
  "extractor_data": [
    "The product is suitable for pumps, fans and conveyors.",
    "The mounting type is wall-mounted."
  ]
}
"""

    def extract_semantic_evidence(
        self,
        document_text: str,
        source_id: str,
        product_context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        api_key = llm_config.gemini_api_key
        
        if api_key:
            try:
                extracted = self._call_langchain_api(document_text, api_key)
                if extracted:
                    return extracted
            except Exception as e:
                print(f"LLM Evidence Extraction failed: {e}")
                pass

        return []

    def _call_langchain_api(self, text: str, api_key: str) -> List[str]:
        llm = ChatGoogleGenerativeAI(
            model=llm_config.llm_model,
            google_api_key=api_key,
            temperature=llm_config.llm_temperature
        )
        
        prompt_template = PromptTemplate.from_template(
            "{system_prompt}\n\nDOCUMENT CONTENT:\n{text}"
        )
        
        chain = prompt_template | llm
        truncated_text = text[:6000]
        
        response = chain.invoke({
            "system_prompt": self.SYSTEM_PROMPT,
            "text": truncated_text
        })
        
        raw_json_str = response.content
        if raw_json_str.startswith("```json"):
            raw_json_str = raw_json_str[7:]
        if raw_json_str.endswith("```"):
            raw_json_str = raw_json_str[:-3]
            
        parsed = json.loads(raw_json_str.strip())
        
        results: List[str] = []
        if isinstance(parsed, dict):
            items = parsed.get("extractor_data") or parsed.get("evidence", [])
            for item in items:
                if isinstance(item, str) and item.strip():
                    results.append(item.strip())
        elif isinstance(parsed, list):
            for item in parsed:
                if isinstance(item, str) and item.strip():
                    results.append(item.strip())

        return results

class LLMExtractor(BaseExtractor):
    """
    Extractor wrapper around LLMExtractionProvider.
    Passes processed Document content into provider.
    """
    
    def __init__(self, provider: Optional[LLMExtractionProvider] = None):
        self.provider = provider or LLMExtractionProviderImpl()

    def extract(self, document: Document) -> List[str]:
        if not document.raw_text or len(document.raw_text.strip()) < 10:
            return []

        return self.provider.extract_semantic_evidence(
            document_text=document.raw_text,
            source_id=document.source_id
        )

