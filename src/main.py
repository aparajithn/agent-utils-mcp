"""Main FastAPI application with MCP and REST endpoints."""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
import asyncio

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .tools import (
    json_validate, json_format,
    base64_encode, base64_decode, hash_generate, uuid_generate, jwt_decode,
    text_stats, slug_generate, regex_test,
    url_parse,
    markdown_to_html, html_to_markdown,
    csv_to_json, json_to_csv,
    datetime_convert, cron_parse,
    diff_text
)
from .middleware import RateLimiter, get_x402_middleware


# Initialize middleware
rate_limiter = RateLimiter(free_limit=100, ttl_seconds=86400)
x402 = get_x402_middleware()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager."""
    # Startup: cleanup task for rate limiter
    async def cleanup_task():
        while True:
            await asyncio.sleep(3600)  # Every hour
            rate_limiter.cleanup_expired()
    
    task = asyncio.create_task(cleanup_task())
    
    yield
    
    # Shutdown
    task.cancel()


app = FastAPI(
    title="Agent Utils MCP Server",
    description="Swiss-army-knife utility server for AI agents",
    version="0.1.0",
    lifespan=lifespan
)


# Dependency for rate limiting and payment
async def check_access(request: Request):
    """Check rate limit and payment."""
    # Check rate limit
    allowed, remaining, reset_at = rate_limiter.check_limit(request)
    
    if not allowed:
        # Check if payment provided
        if x402.check_payment(request):
            return  # Payment accepted
        
        # Return 402 Payment Required
        return x402.create_payment_required_response()
    
    # Within free tier
    return


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "mcp_endpoint": "/mcp",
        "api_endpoint": "/api/v1"
    }


# ============================================================================
# REST API Endpoints
# ============================================================================

class JsonValidateRequest(BaseModel):
    json_string: str

class JsonFormatRequest(BaseModel):
    json_string: str
    minify: bool = False

class Base64EncodeRequest(BaseModel):
    text: str

class Base64DecodeRequest(BaseModel):
    encoded: str

class HashGenerateRequest(BaseModel):
    text: str
    algorithm: str = "sha256"

class UuidGenerateRequest(BaseModel):
    version: int = 4

class UrlParseRequest(BaseModel):
    url: str

class RegexTestRequest(BaseModel):
    pattern: str
    text: str
    flags: str = ""

class MarkdownToHtmlRequest(BaseModel):
    md_text: str

class HtmlToMarkdownRequest(BaseModel):
    html_text: str

class TextStatsRequest(BaseModel):
    text: str

class SlugGenerateRequest(BaseModel):
    text: str
    separator: str = "-"

class DatetimeConvertRequest(BaseModel):
    dt_string: str
    from_tz: str = "UTC"
    to_tz: str = "UTC"
    from_format: Optional[str] = None
    to_format: Optional[str] = None

class CronParseRequest(BaseModel):
    cron_expression: str
    count: int = 5

class DiffTextRequest(BaseModel):
    text1: str
    text2: str
    context_lines: int = 3

class CsvToJsonRequest(BaseModel):
    csv_text: str
    delimiter: str = ","

class JsonToCsvRequest(BaseModel):
    json_data: str
    delimiter: str = ","

class JwtDecodeRequest(BaseModel):
    token: str


@app.post("/api/v1/json_validate", dependencies=[Depends(check_access)])
async def api_json_validate(req: JsonValidateRequest):
    return json_validate(req.json_string)

@app.post("/api/v1/json_format", dependencies=[Depends(check_access)])
async def api_json_format(req: JsonFormatRequest):
    return json_format(req.json_string, req.minify)

@app.post("/api/v1/base64_encode", dependencies=[Depends(check_access)])
async def api_base64_encode(req: Base64EncodeRequest):
    return base64_encode(req.text)

@app.post("/api/v1/base64_decode", dependencies=[Depends(check_access)])
async def api_base64_decode(req: Base64DecodeRequest):
    return base64_decode(req.encoded)

@app.post("/api/v1/hash_generate", dependencies=[Depends(check_access)])
async def api_hash_generate(req: HashGenerateRequest):
    return hash_generate(req.text, req.algorithm)

@app.post("/api/v1/uuid_generate", dependencies=[Depends(check_access)])
async def api_uuid_generate(req: UuidGenerateRequest):
    return uuid_generate(req.version)

@app.post("/api/v1/url_parse", dependencies=[Depends(check_access)])
async def api_url_parse(req: UrlParseRequest):
    return url_parse(req.url)

@app.post("/api/v1/regex_test", dependencies=[Depends(check_access)])
async def api_regex_test(req: RegexTestRequest):
    return regex_test(req.pattern, req.text, req.flags)

@app.post("/api/v1/markdown_to_html", dependencies=[Depends(check_access)])
async def api_markdown_to_html(req: MarkdownToHtmlRequest):
    return markdown_to_html(req.md_text)

@app.post("/api/v1/html_to_markdown", dependencies=[Depends(check_access)])
async def api_html_to_markdown(req: HtmlToMarkdownRequest):
    return html_to_markdown(req.html_text)

@app.post("/api/v1/text_stats", dependencies=[Depends(check_access)])
async def api_text_stats(req: TextStatsRequest):
    return text_stats(req.text)

@app.post("/api/v1/slug_generate", dependencies=[Depends(check_access)])
async def api_slug_generate(req: SlugGenerateRequest):
    return slug_generate(req.text, req.separator)

@app.post("/api/v1/datetime_convert", dependencies=[Depends(check_access)])
async def api_datetime_convert(req: DatetimeConvertRequest):
    return datetime_convert(
        req.dt_string,
        req.from_tz,
        req.to_tz,
        req.from_format,
        req.to_format
    )

@app.post("/api/v1/cron_parse", dependencies=[Depends(check_access)])
async def api_cron_parse(req: CronParseRequest):
    return cron_parse(req.cron_expression, req.count)

@app.post("/api/v1/diff_text", dependencies=[Depends(check_access)])
async def api_diff_text(req: DiffTextRequest):
    return diff_text(req.text1, req.text2, req.context_lines)

@app.post("/api/v1/csv_to_json", dependencies=[Depends(check_access)])
async def api_csv_to_json(req: CsvToJsonRequest):
    return csv_to_json(req.csv_text, req.delimiter)

@app.post("/api/v1/json_to_csv", dependencies=[Depends(check_access)])
async def api_json_to_csv(req: JsonToCsvRequest):
    return json_to_csv(req.json_data, req.delimiter)

@app.post("/api/v1/jwt_decode", dependencies=[Depends(check_access)])
async def api_jwt_decode(req: JwtDecodeRequest):
    return jwt_decode(req.token)


# ============================================================================
# MCP Server Setup
# ============================================================================

# Create MCP server instance
mcp_server = Server("agent-utils")


# Define MCP tools
@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="json_validate",
            description="Validate JSON string and return parsed object or error details",
            inputSchema={
                "type": "object",
                "properties": {
                    "json_string": {"type": "string", "description": "JSON string to validate"}
                },
                "required": ["json_string"]
            }
        ),
        Tool(
            name="json_format",
            description="Pretty-print or minify JSON",
            inputSchema={
                "type": "object",
                "properties": {
                    "json_string": {"type": "string", "description": "JSON string to format"},
                    "minify": {"type": "boolean", "description": "Minify instead of pretty-print", "default": False}
                },
                "required": ["json_string"]
            }
        ),
        Tool(
            name="base64_encode",
            description="Encode string to base64",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to encode"}
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="base64_decode",
            description="Decode base64 string",
            inputSchema={
                "type": "object",
                "properties": {
                    "encoded": {"type": "string", "description": "Base64 string to decode"}
                },
                "required": ["encoded"]
            }
        ),
        Tool(
            name="hash_generate",
            description="Generate hash of input text (MD5, SHA256, SHA512)",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to hash"},
                    "algorithm": {"type": "string", "description": "Hash algorithm", "enum": ["md5", "sha256", "sha512"], "default": "sha256"}
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="uuid_generate",
            description="Generate UUID (v4 or v7)",
            inputSchema={
                "type": "object",
                "properties": {
                    "version": {"type": "number", "description": "UUID version (4 or 7)", "enum": [4, 7], "default": 4}
                }
            }
        ),
        Tool(
            name="url_parse",
            description="Parse URL into components (scheme, host, path, params, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to parse"}
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="regex_test",
            description="Test regex pattern against text and return matches",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Regex pattern"},
                    "text": {"type": "string", "description": "Text to test against"},
                    "flags": {"type": "string", "description": "Regex flags (i, m, s)", "default": ""}
                },
                "required": ["pattern", "text"]
            }
        ),
        Tool(
            name="markdown_to_html",
            description="Convert markdown to HTML",
            inputSchema={
                "type": "object",
                "properties": {
                    "md_text": {"type": "string", "description": "Markdown text"}
                },
                "required": ["md_text"]
            }
        ),
        Tool(
            name="html_to_markdown",
            description="Convert HTML to markdown",
            inputSchema={
                "type": "object",
                "properties": {
                    "html_text": {"type": "string", "description": "HTML text"}
                },
                "required": ["html_text"]
            }
        ),
        Tool(
            name="text_stats",
            description="Calculate text statistics (word count, char count, sentences, reading time)",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to analyze"}
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="slug_generate",
            description="Generate URL-safe slug from text",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to slugify"},
                    "separator": {"type": "string", "description": "Separator character", "default": "-"}
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="datetime_convert",
            description="Convert datetime between timezones and formats, including Unix timestamps",
            inputSchema={
                "type": "object",
                "properties": {
                    "dt_string": {"type": "string", "description": "Datetime string to convert"},
                    "from_tz": {"type": "string", "description": "Source timezone", "default": "UTC"},
                    "to_tz": {"type": "string", "description": "Target timezone", "default": "UTC"},
                    "from_format": {"type": "string", "description": "Source format (strptime)"},
                    "to_format": {"type": "string", "description": "Target format (strftime)"}
                },
                "required": ["dt_string"]
            }
        ),
        Tool(
            name="cron_parse",
            description="Parse cron expression and show next run times with human-readable description",
            inputSchema={
                "type": "object",
                "properties": {
                    "cron_expression": {"type": "string", "description": "Cron expression"},
                    "count": {"type": "number", "description": "Number of next runs to show", "default": 5}
                },
                "required": ["cron_expression"]
            }
        ),
        Tool(
            name="diff_text",
            description="Compute unified diff between two text inputs",
            inputSchema={
                "type": "object",
                "properties": {
                    "text1": {"type": "string", "description": "First text"},
                    "text2": {"type": "string", "description": "Second text"},
                    "context_lines": {"type": "number", "description": "Number of context lines", "default": 3}
                },
                "required": ["text1", "text2"]
            }
        ),
        Tool(
            name="csv_to_json",
            description="Convert CSV to JSON array",
            inputSchema={
                "type": "object",
                "properties": {
                    "csv_text": {"type": "string", "description": "CSV text"},
                    "delimiter": {"type": "string", "description": "CSV delimiter", "default": ","}
                },
                "required": ["csv_text"]
            }
        ),
        Tool(
            name="json_to_csv",
            description="Convert JSON array to CSV",
            inputSchema={
                "type": "object",
                "properties": {
                    "json_data": {"type": "string", "description": "JSON array string"},
                    "delimiter": {"type": "string", "description": "CSV delimiter", "default": ","}
                },
                "required": ["json_data"]
            }
        ),
        Tool(
            name="jwt_decode",
            description="Decode JWT payload (no verification, for inspection only)",
            inputSchema={
                "type": "object",
                "properties": {
                    "token": {"type": "string", "description": "JWT token"}
                },
                "required": ["token"]
            }
        ),
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute MCP tool."""
    # Map tool names to functions
    tool_map = {
        "json_validate": lambda: json_validate(arguments["json_string"]),
        "json_format": lambda: json_format(arguments["json_string"], arguments.get("minify", False)),
        "base64_encode": lambda: base64_encode(arguments["text"]),
        "base64_decode": lambda: base64_decode(arguments["encoded"]),
        "hash_generate": lambda: hash_generate(arguments["text"], arguments.get("algorithm", "sha256")),
        "uuid_generate": lambda: uuid_generate(arguments.get("version", 4)),
        "url_parse": lambda: url_parse(arguments["url"]),
        "regex_test": lambda: regex_test(arguments["pattern"], arguments["text"], arguments.get("flags", "")),
        "markdown_to_html": lambda: markdown_to_html(arguments["md_text"]),
        "html_to_markdown": lambda: html_to_markdown(arguments["html_text"]),
        "text_stats": lambda: text_stats(arguments["text"]),
        "slug_generate": lambda: slug_generate(arguments["text"], arguments.get("separator", "-")),
        "datetime_convert": lambda: datetime_convert(
            arguments["dt_string"],
            arguments.get("from_tz", "UTC"),
            arguments.get("to_tz", "UTC"),
            arguments.get("from_format"),
            arguments.get("to_format")
        ),
        "cron_parse": lambda: cron_parse(arguments["cron_expression"], arguments.get("count", 5)),
        "diff_text": lambda: diff_text(arguments["text1"], arguments["text2"], arguments.get("context_lines", 3)),
        "csv_to_json": lambda: csv_to_json(arguments["csv_text"], arguments.get("delimiter", ",")),
        "json_to_csv": lambda: json_to_csv(arguments["json_data"], arguments.get("delimiter", ",")),
        "jwt_decode": lambda: jwt_decode(arguments["token"]),
    }
    
    if name not in tool_map:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    result = tool_map[name]()
    
    # Convert result to JSON string for MCP response
    import json
    return [TextContent(type="text", text=json.dumps(result))]


# Mount MCP server to FastAPI
@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """MCP endpoint (Streamable HTTP transport)."""
    # This is a placeholder - actual MCP HTTP transport integration
    # would require more setup. For now, return tool list
    return {
        "success": True,
        "message": "MCP endpoint - use MCP client for full protocol support",
        "tools": [tool.name for tool in await list_tools()]
    }


# ============================================================================
# Discovery Endpoints
# ============================================================================

@app.get("/.well-known/agent-card.json")
async def agent_card():
    """Google A2A agent card."""
    return {
        "name": "Agent Utils",
        "description": "Swiss-army-knife utility server for AI agents",
        "version": "0.1.0",
        "capabilities": {
            "tools": [
                "json_validate", "json_format",
                "base64_encode", "base64_decode",
                "hash_generate", "uuid_generate",
                "url_parse", "regex_test",
                "markdown_to_html", "html_to_markdown",
                "text_stats", "slug_generate",
                "datetime_convert", "cron_parse",
                "diff_text", "csv_to_json", "json_to_csv",
                "jwt_decode"
            ]
        },
        "endpoints": {
            "mcp": "/mcp",
            "rest_api": "/api/v1",
            "openapi": "/docs"
        }
    }


@app.get("/.well-known/mcp/server-card.json")
async def mcp_server_card():
    """MCP server card for Smithery."""
    tools = await list_tools()
    return {
        "name": "@aparajithn/agent-utils",
        "description": "Swiss-army-knife utility server for AI agents",
        "version": "0.1.0",
        "protocol": "mcp",
        "transport": "http",
        "endpoint": "/mcp",
        "tools": [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema
            }
            for tool in tools
        ]
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
