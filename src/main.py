"""Agent Utils MCP Server — Swiss-army-knife utilities for AI agents.

Dual interface: MCP (Streamable HTTP) at /mcp + REST API at /api/v1/*.
"""
import os
import json
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Depends
from pydantic import BaseModel
from typing import Optional

from mcp.server.fastmcp import FastMCP
from mcp.server.streamable_http import TransportSecuritySettings

from .tools import (
    json_validate, json_format,
    base64_encode, base64_decode, hash_generate, uuid_generate, jwt_decode,
    text_stats, slug_generate, regex_test,
    url_parse,
    markdown_to_html, html_to_markdown,
    csv_to_json, json_to_csv,
    datetime_convert, cron_parse,
    diff_text,
)
from .middleware import RateLimiter, get_x402_middleware

# ---------------------------------------------------------------------------
# MCP Server (FastMCP — stateless Streamable HTTP)
# ---------------------------------------------------------------------------
PUBLIC_HOST = os.getenv("PUBLIC_HOST", "agent-utils-mcp.onrender.com")

mcp = FastMCP(
    "agent-utils",
    stateless_http=True,
    json_response=True,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False,
    ),
)

@mcp.tool()
def tool_json_validate(json_string: str) -> str:
    """Validate a JSON string. Returns parsed object or detailed error."""
    return json.dumps(json_validate(json_string))

@mcp.tool()
def tool_json_format(json_string: str, minify: bool = False) -> str:
    """Pretty-print or minify a JSON string."""
    return json.dumps(json_format(json_string, minify))

@mcp.tool()
def tool_base64_encode(text: str) -> str:
    """Encode a string to base64."""
    return json.dumps(base64_encode(text))

@mcp.tool()
def tool_base64_decode(encoded: str) -> str:
    """Decode a base64 string."""
    return json.dumps(base64_decode(encoded))

@mcp.tool()
def tool_hash_generate(text: str, algorithm: str = "sha256") -> str:
    """Generate hash (md5, sha256, sha512) of input text."""
    return json.dumps(hash_generate(text, algorithm))

@mcp.tool()
def tool_uuid_generate(version: int = 4) -> str:
    """Generate a UUID (v4 or v7)."""
    return json.dumps(uuid_generate(version))

@mcp.tool()
def tool_url_parse(url: str) -> str:
    """Parse a URL into components (scheme, host, path, params, etc.)."""
    return json.dumps(url_parse(url))

@mcp.tool()
def tool_regex_test(pattern: str, text: str, flags: str = "") -> str:
    """Test a regex pattern against text and return all matches."""
    return json.dumps(regex_test(pattern, text, flags))

@mcp.tool()
def tool_markdown_to_html(md_text: str) -> str:
    """Convert Markdown to HTML."""
    return json.dumps(markdown_to_html(md_text))

@mcp.tool()
def tool_html_to_markdown(html_text: str) -> str:
    """Convert HTML to Markdown."""
    return json.dumps(html_to_markdown(html_text))

@mcp.tool()
def tool_text_stats(text: str) -> str:
    """Compute text statistics: word count, char count, sentences, reading time."""
    return json.dumps(text_stats(text))

@mcp.tool()
def tool_slug_generate(text: str, separator: str = "-") -> str:
    """Generate a URL-safe slug from text."""
    return json.dumps(slug_generate(text, separator))

@mcp.tool()
def tool_datetime_convert(
    dt_string: str,
    from_tz: str = "UTC",
    to_tz: str = "UTC",
    from_format: str | None = None,
    to_format: str | None = None,
) -> str:
    """Convert a datetime between timezones/formats, including Unix timestamps."""
    return json.dumps(datetime_convert(dt_string, from_tz, to_tz, from_format, to_format))

@mcp.tool()
def tool_cron_parse(cron_expression: str, count: int = 5) -> str:
    """Parse a cron expression: human-readable description + next N run times."""
    return json.dumps(cron_parse(cron_expression, count))

@mcp.tool()
def tool_diff_text(text1: str, text2: str, context_lines: int = 3) -> str:
    """Compute a unified diff between two texts."""
    return json.dumps(diff_text(text1, text2, context_lines))

@mcp.tool()
def tool_csv_to_json(csv_text: str, delimiter: str = ",") -> str:
    """Convert CSV text to a JSON array of objects."""
    return json.dumps(csv_to_json(csv_text, delimiter))

@mcp.tool()
def tool_json_to_csv(json_data: str, delimiter: str = ",") -> str:
    """Convert a JSON array to CSV text."""
    return json.dumps(json_to_csv(json_data, delimiter))

@mcp.tool()
def tool_jwt_decode(token: str) -> str:
    """Decode a JWT payload without verification (inspection only)."""
    return json.dumps(jwt_decode(token))


# ---------------------------------------------------------------------------
# REST-only FastAPI app — mounted UNDER the MCP Starlette app
# ---------------------------------------------------------------------------
rate_limiter = RateLimiter(free_limit=100, ttl_seconds=86400)
x402 = get_x402_middleware()

rest_app = FastAPI(
    title="Agent Utils MCP Server",
    description="Swiss-army-knife utility server for AI agents — 17 tools via MCP + REST.",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

async def check_access(request: Request):
    allowed, remaining, reset_at = rate_limiter.check_limit(request)
    if not allowed:
        if x402.check_payment(request):
            return
        return x402.create_payment_required_response()

# --- Health & discovery ---
@rest_app.get("/health")
async def health():
    return {"status": "healthy", "version": "0.1.0", "tools": 17}

@rest_app.get("/.well-known/agent-card.json")
async def agent_card():
    return {
        "name": "Agent Utils",
        "description": "Swiss-army-knife utility server for AI agents",
        "version": "0.1.0",
        "url": os.getenv("PUBLIC_URL", "https://agent-utils-mcp.onrender.com"),
        "capabilities": {"tools": 17},
        "endpoints": {"mcp": "/mcp", "rest": "/api/v1", "openapi": "/docs"},
    }

@rest_app.get("/.well-known/mcp/server-card.json")
async def mcp_server_card():
    return {
        "serverInfo": {"name": "agent-utils", "version": "0.1.0"},
        "tools": [
            {
                "name": "json_validate",
                "description": "Validate a JSON string. Returns parsed object or detailed error.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "json_string": {"type": "string", "description": "JSON string to validate"}
                    },
                    "required": ["json_string"]
                }
            },
            {
                "name": "json_format",
                "description": "Pretty-print or minify a JSON string.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "json_string": {"type": "string", "description": "JSON string to format"},
                        "minify": {"type": "boolean", "description": "Minify instead of prettify", "default": False}
                    },
                    "required": ["json_string"]
                }
            },
            {
                "name": "base64_encode",
                "description": "Encode a string to base64.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Text to encode"}
                    },
                    "required": ["text"]
                }
            },
            {
                "name": "base64_decode",
                "description": "Decode a base64 string.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "encoded": {"type": "string", "description": "Base64 string to decode"}
                    },
                    "required": ["encoded"]
                }
            },
            {
                "name": "hash_generate",
                "description": "Generate hash (md5, sha256, sha512) of input text.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Text to hash"},
                        "algorithm": {"type": "string", "description": "Hash algorithm", "enum": ["md5", "sha256", "sha512"], "default": "sha256"}
                    },
                    "required": ["text"]
                }
            },
            {
                "name": "uuid_generate",
                "description": "Generate a UUID (v4 or v7).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "version": {"type": "integer", "description": "UUID version (4 or 7)", "enum": [4, 7], "default": 4}
                    }
                }
            },
            {
                "name": "url_parse",
                "description": "Parse a URL into components (scheme, host, path, params, etc.).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to parse"}
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "regex_test",
                "description": "Test a regex pattern against text and return all matches.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string", "description": "Regex pattern"},
                        "text": {"type": "string", "description": "Text to test against"},
                        "flags": {"type": "string", "description": "Regex flags (i, m, s, etc.)", "default": ""}
                    },
                    "required": ["pattern", "text"]
                }
            },
            {
                "name": "markdown_to_html",
                "description": "Convert Markdown to HTML.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "md_text": {"type": "string", "description": "Markdown text to convert"}
                    },
                    "required": ["md_text"]
                }
            },
            {
                "name": "html_to_markdown",
                "description": "Convert HTML to Markdown.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "html_text": {"type": "string", "description": "HTML text to convert"}
                    },
                    "required": ["html_text"]
                }
            },
            {
                "name": "text_stats",
                "description": "Compute text statistics: word count, char count, sentences, reading time.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Text to analyze"}
                    },
                    "required": ["text"]
                }
            },
            {
                "name": "slug_generate",
                "description": "Generate a URL-safe slug from text.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Text to convert to slug"},
                        "separator": {"type": "string", "description": "Separator character", "default": "-"}
                    },
                    "required": ["text"]
                }
            },
            {
                "name": "datetime_convert",
                "description": "Convert a datetime between timezones/formats, including Unix timestamps.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "dt_string": {"type": "string", "description": "Datetime string or Unix timestamp"},
                        "from_tz": {"type": "string", "description": "Source timezone", "default": "UTC"},
                        "to_tz": {"type": "string", "description": "Target timezone", "default": "UTC"},
                        "from_format": {"type": "string", "description": "Input datetime format (strptime)"},
                        "to_format": {"type": "string", "description": "Output datetime format (strftime)"}
                    },
                    "required": ["dt_string"]
                }
            },
            {
                "name": "cron_parse",
                "description": "Parse a cron expression: human-readable description + next N run times.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "cron_expression": {"type": "string", "description": "Cron expression (e.g., '0 */6 * * *')"},
                        "count": {"type": "integer", "description": "Number of next run times to return", "default": 5}
                    },
                    "required": ["cron_expression"]
                }
            },
            {
                "name": "diff_text",
                "description": "Compute a unified diff between two texts.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text1": {"type": "string", "description": "First text"},
                        "text2": {"type": "string", "description": "Second text"},
                        "context_lines": {"type": "integer", "description": "Number of context lines", "default": 3}
                    },
                    "required": ["text1", "text2"]
                }
            },
            {
                "name": "csv_to_json",
                "description": "Convert CSV text to a JSON array of objects.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "csv_text": {"type": "string", "description": "CSV text to convert"},
                        "delimiter": {"type": "string", "description": "CSV delimiter", "default": ","}
                    },
                    "required": ["csv_text"]
                }
            },
            {
                "name": "json_to_csv",
                "description": "Convert a JSON array to CSV text.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "json_data": {"type": "string", "description": "JSON array string to convert"},
                        "delimiter": {"type": "string", "description": "CSV delimiter", "default": ","}
                    },
                    "required": ["json_data"]
                }
            },
            {
                "name": "jwt_decode",
                "description": "Decode a JWT payload without verification (inspection only).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "token": {"type": "string", "description": "JWT token to decode"}
                    },
                    "required": ["token"]
                }
            }
        ]
    }

# --- REST endpoints ---
class JsonIn(BaseModel):
    json_string: str
    minify: bool = False

class B64EncIn(BaseModel):
    text: str

class B64DecIn(BaseModel):
    encoded: str

class HashIn(BaseModel):
    text: str
    algorithm: str = "sha256"

class UuidIn(BaseModel):
    version: int = 4

class UrlIn(BaseModel):
    url: str

class RegexIn(BaseModel):
    pattern: str
    text: str
    flags: str = ""

class MdIn(BaseModel):
    md_text: str

class HtmlIn(BaseModel):
    html_text: str

class TextIn(BaseModel):
    text: str
    separator: str = "-"

class DtIn(BaseModel):
    dt_string: str
    from_tz: str = "UTC"
    to_tz: str = "UTC"
    from_format: Optional[str] = None
    to_format: Optional[str] = None

class CronIn(BaseModel):
    cron_expression: str
    count: int = 5

class DiffIn(BaseModel):
    text1: str
    text2: str
    context_lines: int = 3

class CsvIn(BaseModel):
    csv_text: str
    delimiter: str = ","

class JsonCsvIn(BaseModel):
    json_data: str
    delimiter: str = ","

class JwtIn(BaseModel):
    token: str

@rest_app.post("/api/v1/json_validate", dependencies=[Depends(check_access)])
async def r_json_validate(r: JsonIn): return json_validate(r.json_string)

@rest_app.post("/api/v1/json_format", dependencies=[Depends(check_access)])
async def r_json_format(r: JsonIn): return json_format(r.json_string, r.minify)

@rest_app.post("/api/v1/base64_encode", dependencies=[Depends(check_access)])
async def r_b64enc(r: B64EncIn): return base64_encode(r.text)

@rest_app.post("/api/v1/base64_decode", dependencies=[Depends(check_access)])
async def r_b64dec(r: B64DecIn): return base64_decode(r.encoded)

@rest_app.post("/api/v1/hash_generate", dependencies=[Depends(check_access)])
async def r_hash(r: HashIn): return hash_generate(r.text, r.algorithm)

@rest_app.post("/api/v1/uuid_generate", dependencies=[Depends(check_access)])
async def r_uuid(r: UuidIn): return uuid_generate(r.version)

@rest_app.post("/api/v1/url_parse", dependencies=[Depends(check_access)])
async def r_url(r: UrlIn): return url_parse(r.url)

@rest_app.post("/api/v1/regex_test", dependencies=[Depends(check_access)])
async def r_regex(r: RegexIn): return regex_test(r.pattern, r.text, r.flags)

@rest_app.post("/api/v1/markdown_to_html", dependencies=[Depends(check_access)])
async def r_md2html(r: MdIn): return markdown_to_html(r.md_text)

@rest_app.post("/api/v1/html_to_markdown", dependencies=[Depends(check_access)])
async def r_html2md(r: HtmlIn): return html_to_markdown(r.html_text)

@rest_app.post("/api/v1/text_stats", dependencies=[Depends(check_access)])
async def r_stats(r: TextIn): return text_stats(r.text)

@rest_app.post("/api/v1/slug_generate", dependencies=[Depends(check_access)])
async def r_slug(r: TextIn): return slug_generate(r.text, r.separator)

@rest_app.post("/api/v1/datetime_convert", dependencies=[Depends(check_access)])
async def r_dt(r: DtIn): return datetime_convert(r.dt_string, r.from_tz, r.to_tz, r.from_format, r.to_format)

@rest_app.post("/api/v1/cron_parse", dependencies=[Depends(check_access)])
async def r_cron(r: CronIn): return cron_parse(r.cron_expression, r.count)

@rest_app.post("/api/v1/diff_text", dependencies=[Depends(check_access)])
async def r_diff(r: DiffIn): return diff_text(r.text1, r.text2, r.context_lines)

@rest_app.post("/api/v1/csv_to_json", dependencies=[Depends(check_access)])
async def r_csv2json(r: CsvIn): return csv_to_json(r.csv_text, r.delimiter)

@rest_app.post("/api/v1/json_to_csv", dependencies=[Depends(check_access)])
async def r_json2csv(r: JsonCsvIn): return json_to_csv(r.json_data, r.delimiter)

@rest_app.post("/api/v1/jwt_decode", dependencies=[Depends(check_access)])
async def r_jwt(r: JwtIn): return jwt_decode(r.token)


# ---------------------------------------------------------------------------
# Compose: MCP Starlette app is primary, REST FastAPI mounted inside it
# ---------------------------------------------------------------------------
# Add custom routes to the MCP starlette app before it's built
from starlette.routing import Mount as StarletteMount
mcp._custom_starlette_routes.append(StarletteMount("/", app=rest_app))

# The final ASGI app
app = mcp.streamable_http_app()
