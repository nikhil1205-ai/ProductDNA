import re

def normalize_text(text: str) -> str:
    """Normalizes identifiers by lowercasing and removing non-alphanumeric characters."""
    if not text:
        return ""
    return re.sub(r'[^a-z0-9]', '', str(text).lower())

def normalize_fuzzy(text: str) -> str:
    """Normalizes text for fuzzy matching by lowercasing and standardizing whitespace."""
    if not text:
        return ""
    return " ".join(str(text).lower().split())
