import json
from typing import Dict, Any, Union

def read_json(raw_input: Union[str, bytes, Dict[str, Any], list]) -> Dict[str, Any]:
    """
    Parse and validate arbitrary JSON input (string, bytes, or parsed dict/list).
    Preserves original structured key-value data.
    """
    parsed_data: Any = None

    if isinstance(raw_input, (dict, list)):
        parsed_data = raw_input
    elif isinstance(raw_input, (str, bytes)):
        if isinstance(raw_input, bytes):
            try:
                raw_str = raw_input.decode('utf-8')
            except UnicodeDecodeError:
                raw_str = raw_input.decode('latin-1')
        else:
            raw_str = raw_input

        if not raw_str.strip():
            raise ValueError("Empty JSON payload provided.")

        try:
            parsed_data = json.loads(raw_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON syntax: {str(e)}")
    else:
        raise ValueError("Unsupported data type for JSON reader.")

    # Create textual representation from key-values for identity extractor
    text_lines = []
    if isinstance(parsed_data, dict):
        for key, val in parsed_data.items():
            if isinstance(val, (dict, list)):
                text_lines.append(f"{key}: {json.dumps(val)}")
            else:
                text_lines.append(f"{key}: {val}")
    elif isinstance(parsed_data, list):
        for idx, item in enumerate(parsed_data):
            text_lines.append(f"Item {idx + 1}: {json.dumps(item)}")

    summary_text = "\n".join(text_lines)

    return {
        "structured_data": parsed_data if isinstance(parsed_data, dict) else {"items": parsed_data},
        "text": summary_text
    }
