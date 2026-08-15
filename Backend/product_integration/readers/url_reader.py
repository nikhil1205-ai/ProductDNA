import requests
from bs4 import BeautifulSoup
from typing import Dict, Any

def read_url(url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Fetch webpage content from a URL using requests and BeautifulSoup.
    Extracts title, visible body text, and URL metadata.
    """
    if not url or not (url.startswith("http://") or url.startswith("https://")):
        raise ValueError(f"Invalid URL format: '{url}'. Must start with http:// or https://")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 ProductDNA-Intake/1.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")
        if "text/html" not in content_type and "application/xhtml+xml" not in content_type and "text/plain" not in content_type:
            raise ValueError(f"URL returned non-text Content-Type: '{content_type}'")

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script and style elements
        for script_or_style in soup(["script", "style", "noscript", "header", "footer", "nav"]):
            script_or_style.decompose()

        # Get page title
        title = soup.title.string.strip() if (soup.title and soup.title.string) else ""

        # Extract text content
        text_content = soup.get_text(separator=" ", strip=True)

        return {
            "url": url,
            "title": title,
            "text": text_content,
            "status_code": response.status_code,
            "mime_type": content_type.split(";")[0].strip()
        }
    except requests.exceptions.Timeout:
        raise ValueError(f"Connection timeout while attempting to fetch URL '{url}' after {timeout} seconds.")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to fetch content from URL '{url}': {str(e)}")
