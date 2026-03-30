# Agent Utils MCP Server 🛠️

A Swiss-army-knife utility server for AI agents — 18 tools via MCP (Streamable HTTP) + REST API.

[![Smithery](https://smithery.ai/badge/@aparajithn/agent-utils-mcp)](https://smithery.ai/server/@aparajithn/agent-utils-mcp)
[![Glama](https://glama.ai/badge/mcp/agent-utils-mcp)](https://glama.ai/mcp/servers/agent-utils-mcp)

**Live at:** https://agent-utils-mcp.onrender.com

## Add to Your MCP Client

### Claude Desktop / Cursor / Windsurf

Add to your MCP config:

```json
{
  "mcpServers": {
    "agent-utils": {
      "url": "https://agent-utils-mcp.onrender.com/mcp"
    }
  }
}
```

### Smithery

```bash
smithery mcp add aparajithn/agent-utils
```

## Tools (18)

| Tool | Description |
|------|-------------|
| `tool_json_validate` | Validate JSON string, return parsed or error |
| `tool_json_format` | Pretty-print or minify JSON |
| `tool_base64_encode` | Encode string to base64 |
| `tool_base64_decode` | Decode base64 string |
| `tool_hash_generate` | MD5, SHA256, SHA512 hash |
| `tool_uuid_generate` | UUID v4 or v7 |
| `tool_url_parse` | Parse URL into components |
| `tool_regex_test` | Test regex pattern, return matches |
| `tool_markdown_to_html` | Markdown → HTML |
| `tool_html_to_markdown` | HTML → Markdown |
| `tool_text_stats` | Word count, char count, reading time |
| `tool_slug_generate` | URL-safe slug from text |
| `tool_datetime_convert` | Convert between timezones/formats/Unix timestamps |
| `tool_cron_parse` | Human-readable cron description + next N runs |
| `tool_diff_text` | Unified diff between two texts |
| `tool_csv_to_json` | CSV → JSON array |
| `tool_json_to_csv` | JSON array → CSV |
| `tool_jwt_decode` | Decode JWT payload (no verification) |

## REST API

All tools also available as REST endpoints at `/api/v1/{tool_name}`.

```bash
# Hash a string
curl -X POST https://agent-utils-mcp.onrender.com/api/v1/hash_generate \
  -H "Content-Type: application/json" \
  -d '{"text": "hello world", "algorithm": "sha256"}'

# Generate UUID
curl -X POST https://agent-utils-mcp.onrender.com/api/v1/uuid_generate \
  -H "Content-Type: application/json" \
  -d '{"version": 4}'

# Convert datetime
curl -X POST https://agent-utils-mcp.onrender.com/api/v1/datetime_convert \
  -H "Content-Type: application/json" \
  -d '{"dt_string": "2025-01-01 12:00", "from_tz": "UTC", "to_tz": "America/New_York"}'
```

OpenAPI docs: https://agent-utils-mcp.onrender.com/docs

## Discovery

- **Google A2A:** `/.well-known/agent-card.json`
- **Smithery:** `/.well-known/mcp/server-card.json`
- **OpenAPI:** `/openapi.json`

## Pricing

- **Free tier:** 100 requests per IP per 24 hours
- **Paid tier:** x402 protocol — $0.001/request in USDC (coming soon)

## Tech Stack

- Python 3.11 + FastAPI + MCP SDK (Streamable HTTP)
- Deployed on Render (auto-scaling)
- GitHub: https://github.com/aparajithn/agent-utils-mcp

## License

MIT

## Hosted deployment

A hosted deployment is available on [Fronteir AI](https://fronteir.ai/mcp/aparajithn-agent-utils-mcp).

