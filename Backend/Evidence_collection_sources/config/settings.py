"""
Module 4 Settings Configuration
"""

import os
from pydantic import BaseModel, Field

class Module4Settings(BaseModel):
    # Source Processing Settings
    default_request_timeout: int = Field(default=15, description="Timeout in seconds for URL fetching")
    max_file_size_bytes: int = Field(default=50 * 1024 * 1024, description="Max allowed file size (50MB)")
    user_agent: str = Field(
        default="ProductDNA-EvidenceExtractor/1.0 (+https://productdna.ai)",
        description="HTTP User-Agent for web scrapers"
    )
    
    # LLM Extractor Settings
    gemini_api_key: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY", "")))
    llm_model: str = Field(default="gemini-1.5-flash", description="Default Gemini model identifier")
    llm_temperature: float = Field(default=0.0, description="Temperature for extraction (0.0 for deterministic)")
    enable_llm_fallback: bool = Field(default=True, description="Enable NLP/pattern fallback when LLM API key missing")

    # Content Deduplication
    enable_hash_deduplication: bool = Field(default=True, description="Enable SHA256 content deduplication")

settings = Module4Settings()
