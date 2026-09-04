"""
Module 3 Constrained LLM Evidence Extractor Implementation (Fallback Extractor)
"""

import json
import uuid
from typing import List, Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

from .base import BaseExtractor, LLMExtractionProvider
from ..models.document_models import Document
from ..models.extraction_models import EvidenceItem, EvidenceType, ExtractionMethod
from ..config.llm_config import llm_config

class LLMExtractionProviderImpl(LLMExtractionProvider):
    """
    Constrained LLM Extraction Provider using Google Gemini API.
    Extracts raw, verbatim evidence sentences from complex/unstructured text without paraphrasing or hallucination.
    """
    
    SYSTEM_PROMPT = """
You are a constrained evidence sentence extraction filter.
Your task is to identify and extract explicit, verbatim evidence sentences describing the product from the provided text.

STRICT RULES:
1. Extract ONLY statements explicitly written in the source text.
2. PRESERVE exact source wording. DO NOT paraphrase or rewrite.
3. NEVER invent, assume, or infer unstated information.
4. DO NOT transform sentences into key-value pairs or canonical attributes (e.g. DO NOT turn "This phone has 250 GB storage." into "Storage = 250 GB").
5. DO NOT perform unit conversions or attribute normalization.
6. If no clear evidence sentences exist, return an empty array [].

Return JSON format:
{
  "evidence_sentences": [
    "The rugged device continues to operate reliably in temperatures ranging from -20°C to 60°C."
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
        
        if not api_key:
            return []

        try:
            return self._call_langchain_api(document_text, api_key)
        except Exception as e:
            print(f"LLM Evidence Extraction fallback gracefully skipped: {e}")
            return []

    def _call_langchain_api(self, text: str, api_key: str) -> List[str]:
        llm = ChatGoogleGenerativeAI(
            model=llm_config.llm_model,
            google_api_key=api_key,
            temperature=0.0  # Zero temperature for deterministic adherence
        )
        
        prompt_template = PromptTemplate.from_template(
            "{system_prompt}\n\nSOURCE DOCUMENT CONTENT:\n{text}"
        )
        
        chain = prompt_template | llm
        truncated_text = text[:6000]
        
        response = chain.invoke({
            "system_prompt": self.SYSTEM_PROMPT,
            "text": truncated_text
        })
        
        raw_json_str = str(response.content).strip()
        if raw_json_str.startswith("```json"):
            raw_json_str = raw_json_str[7:]
        if raw_json_str.startswith("```"):
            raw_json_str = raw_json_str[3:]
        if raw_json_str.endswith("```"):
            raw_json_str = raw_json_str[:-3]
            
        parsed = json.loads(raw_json_str.strip())
        
        results: List[str] = []
        if isinstance(parsed, dict):
            items = parsed.get("evidence_sentences") or parsed.get("extractor_data") or parsed.get("evidence", [])
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
    Constrained LLM Extractor Wrapper.
    Runs LLM fallback extraction on unstructured text content and returns EvidenceItem objects.
    """
    
    def __init__(self, provider: Optional[LLMExtractionProvider] = None):
        self.provider = provider or LLMExtractionProviderImpl()

    def extract(self, document: Document) -> List[EvidenceItem]:
        if not document.raw_text or len(document.raw_text.strip()) < 15:
            return []

        sentences = self.provider.extract_semantic_evidence(
            document_text=document.raw_text,
            source_id=document.source_id
        )

        extracted: List[EvidenceItem] = []
        seen: set = set()

        source_type = document.metadata.get("source_type", "text")

        for sent in sentences:
            clean_sent = sent.strip()
            if clean_sent and clean_sent.lower() not in seen:
                seen.add(clean_sent.lower())
                item = EvidenceItem(
                    evidence_id=f"EV-LLM-{uuid.uuid4().hex[:6].upper()}",
                    source_id=document.source_id,
                    source_type=str(source_type),
                    evidence_type=EvidenceType.SENTENCE,
                    text=clean_sent,
                    extraction_method=ExtractionMethod.LLM
                )
                extracted.append(item)

        return extracted
