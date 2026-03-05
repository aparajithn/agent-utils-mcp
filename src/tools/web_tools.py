"""Web utility tools."""
from urllib.parse import urlparse, parse_qs, urlunparse
from typing import Any, Dict


def url_parse(url: str) -> Dict[str, Any]:
    """Parse URL into components (scheme, host, path, params, etc.)."""
    try:
        parsed = urlparse(url)
        
        # Parse query parameters
        query_params = parse_qs(parsed.query)
        # Convert lists to single values where possible
        query_params = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}
        
        return {
            "success": True,
            "result": {
                "scheme": parsed.scheme,
                "netloc": parsed.netloc,
                "hostname": parsed.hostname,
                "port": parsed.port,
                "path": parsed.path,
                "params": parsed.params,
                "query": parsed.query,
                "query_params": query_params,
                "fragment": parsed.fragment,
                "username": parsed.username,
                "password": parsed.password
            }
        }
    except Exception as e:
        return {"success": False, "error": f"Error parsing URL: {str(e)}"}
