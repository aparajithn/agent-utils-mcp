"""JSON utility tools."""
import json
import orjson
from typing import Any, Dict


def json_validate(json_string: str) -> Dict[str, Any]:
    """Validate JSON string and return parsed object or error details."""
    try:
        parsed = orjson.loads(json_string)
        return {"success": True, "result": parsed}
    except orjson.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Invalid JSON: {str(e)}",
            "details": {"line": e.pos if hasattr(e, 'pos') else None}
        }
    except Exception as e:
        return {"success": False, "error": f"Error parsing JSON: {str(e)}"}


def json_format(json_string: str, minify: bool = False) -> Dict[str, Any]:
    """Pretty-print or minify JSON."""
    try:
        parsed = orjson.loads(json_string)
        if minify:
            formatted = orjson.dumps(parsed).decode('utf-8')
        else:
            formatted = orjson.dumps(
                parsed,
                option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS
            ).decode('utf-8')
        return {"success": True, "result": formatted}
    except Exception as e:
        return {"success": False, "error": f"Error formatting JSON: {str(e)}"}
