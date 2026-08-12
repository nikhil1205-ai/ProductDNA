from typing import Dict, Any
from ..schemas.response_schema import (
    StandardProductInput,
    ProductIdentity,
    ProductMetadata,
    ProductContent
)

def build_standard_product_input(
    request_id: str,
    input_type: str,
    identity_data: Dict[str, Any],
    metadata_data: Dict[str, Any],
    content_data: Dict[str, Any],
    status: str = "READY_FOR_RESOLUTION"
) -> StandardProductInput:
    """
    Construct the standardized Product Input Object from identity, metadata, and content dictionaries.
    """
    identity_obj = ProductIdentity(**identity_data)
    metadata_obj = ProductMetadata(**metadata_data)
    
    # Format content fields cleanly
    content_obj = ProductContent(
        text=content_data.get("text"),
        title=content_data.get("title"),
        tables=content_data.get("tables", []),
        structured_data=content_data.get("structured_data"),
        page_count=content_data.get("page_count"),
        row_count=content_data.get("row_count"),
        column_count=content_data.get("column_count")
    )

    return StandardProductInput(
        request_id=request_id,
        input_type=input_type,
        identity=identity_obj,
        metadata=metadata_obj,
        content=content_obj,
        status=status
    )
