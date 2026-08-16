"""
Module 4 URL Collector
"""

import hashlib
from typing import Optional
from urllib.parse import urlparse
import requests

from .base import BaseSourceCollector
from ..models.source_models import SourceInput, Source, SourceMetadata, SourceType, SourceStatus, SourceOrigin

DEFAULT_REQUEST_TIMEOUT = 15
USER_AGENT = "ProductDNA-EvidenceExtractor/1.0 (+https://productdna.ai)"
class URLCollector(BaseSourceCollector):
    """
    Intake collector for URL / Website sources.
    Fetches URL, handles redirects, errors, timeouts, and computes content hash.
    """
    
    def collect(self, source_input: SourceInput, source_id: str) -> Source:
        raw_url = source_input.value.strip()
        
        # Validate URL format
        parsed = urlparse(raw_url)
        if not parsed.scheme or not parsed.netloc:
            return Source(
                source_id=source_id,
                source_type=SourceType.URL,
                source_subtype=source_input.subtype or "website",
                source_name=source_input.name or raw_url,
                origin=SourceOrigin.USER_PROVIDED,
                status=SourceStatus.FAILED,
                error_message=f"Invalid URL format: '{raw_url}'",
                metadata=SourceMetadata(url=raw_url)
            )

        # Attempt HTTP fetch
        headers = {"User-Agent": USER_AGENT}
        try:
            response = requests.get(raw_url, headers=headers, timeout=DEFAULT_REQUEST_TIMEOUT, allow_redirects=True)
            response.raise_for_status()
            
            final_url = response.url
            content_bytes = response.content
            content_hash = hashlib.sha256(content_bytes).hexdigest()
            content_type = response.headers.get("content-type", "text/html")
            
            metadata = SourceMetadata(
                url=final_url,
                content_type=content_type,
                size_bytes=len(content_bytes),
                content_hash=content_hash
            )
            
            # Save raw bytes on source_input for processor
            source_input.file_bytes = content_bytes
            
            return Source(
                source_id=source_id,
                source_type=SourceType.URL,
                source_subtype=source_input.subtype or "website",
                source_name=source_input.name or parsed.netloc,
                origin=SourceOrigin.USER_PROVIDED,
                status=SourceStatus.RECEIVED,
                metadata=metadata
            )
            
        except requests.exceptions.Timeout:
            return Source(
                source_id=source_id,
                source_type=SourceType.URL,
                source_subtype=source_input.subtype or "website",
                source_name=source_input.name or raw_url,
                origin=SourceOrigin.USER_PROVIDED,
                status=SourceStatus.FAILED,
                error_message=f"Request timed out fetching URL: {raw_url}",
                metadata=SourceMetadata(url=raw_url)
            )
        except requests.exceptions.RequestException as e:
            return Source(
                source_id=source_id,
                source_type=SourceType.URL,
                source_subtype=source_input.subtype or "website",
                source_name=source_input.name or raw_url,
                origin=SourceOrigin.USER_PROVIDED,
                status=SourceStatus.FAILED,
                error_message=f"HTTP request failed for URL '{raw_url}': {str(e)}",
                metadata=SourceMetadata(url=raw_url)
            )
