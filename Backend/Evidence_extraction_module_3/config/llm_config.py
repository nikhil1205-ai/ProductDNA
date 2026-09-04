"""
LLM Configuration Module for Evidence Extraction (Module 3)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from Backend directory if present
backend_env = Path(__file__).resolve().parent.parent.parent / ".env"
if backend_env.exists():
    load_dotenv(backend_env)
else:
    load_dotenv()

class LLMConfig:
    """
    Configuration model for Gemini LLM API interactions.
    """
    def __init__(self):
        self.gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
        self.llm_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        try:
            self.llm_temperature: float = float(os.getenv("GEMINI_TEMPERATURE", "0.0"))
        except ValueError:
            self.llm_temperature = 0.0

llm_config = LLMConfig()
