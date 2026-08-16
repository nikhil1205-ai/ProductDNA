import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class LLMConfig:
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
    llm_model: str = os.getenv("LLM_MODEL", "gemini-1.5-flash")
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.0"))
    enable_llm_fallback: bool = os.getenv("ENABLE_LLM_FALLBACK", "True").lower() in ("true", "1", "yes")

llm_config = LLMConfig()
