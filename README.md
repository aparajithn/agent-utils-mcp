# Agent Utils MCP Server

A Swiss-army-knife utility server for AI agents. Provides 17+ essential micro-tools via both MCP (Model Context Protocol) and REST API.

## 🚀 Features

- **Dual Protocol Support**: MCP for AI agents + REST API for everything else
- **17 Utility Tools**: JSON, base64, hashing, UUID, URL parsing, regex, markdown, datetime, cron, diff, CSV, JWT, and more
- **x402 Payment Integration**: Free tier (100 requests/IP) + optional paid tier
- **Auto-scaling**: Deploys to Fly.io with scale-to-zero
- **Production Ready**: Health checks, rate limiting, OpenAPI docs

## 📦 Available Tools

| Tool | Description |
|------|-------------|
| `json_validate` | Validate JSON string, return parsed or error details |
| `json_format` | Pretty-print or minify JSON |
| `base64_encode` | Encode string to base64 |
| `base64_decode` | Decode base64 string |
| `hash_generate` | Generate MD5, SHA256, or SHA512 hash |
| `uuid_generate` | Generate UUID v4 or v7 |
| `url_parse` | Parse URL into components |
| `regex_test` | Test regex pattern against text |
| `markdown_to_html` | Convert markdown to HTML |
| `html_to_markdown` | Convert HTML to markdown |
| `text_stats` | Calculate word/char/sentence count, reading time |
| `slug_generate` | Generate URL-safe slugs |
| `datetime_convert` | Convert between timezones, formats, Unix timestamps |
| `cron_parse` | Parse cron expressions, show next runs |
| `diff_text` | Compute unified diff between texts |
| `csv_to_json` | Convert CSV to JSON |
| `json_to_csv` | Convert JSON to CSV |
| `jwt_decode` | Decode JWT payload (no verification) |

## 🔧 Quick Start

### Using with Claude Desktop (MCP)

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "agent-utils": {
      "url": "https://agent-utils-mcp.fly.dev/mcp"
    }
  }
}
```

### Using with Cursor / VS Code

Install via MCP:

```bash
npx @anthropic-ai/smithery install @aparajithn/agent-utils
```

### Using the REST API

```bash
# JSON validation
curl -X POST https://agent-utils-mcp.fly.dev/api/v1/json_validate \
  -H "Content-Type: application/json" \
  -d '{"json_string": "{\"key\": \"value\"}"}'

# Base64 encoding
curl -X POST https://agent-utils-mcp.fly.dev/api/v1/base64_encode \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello World"}'

# Generate UUID
curl -X POST https://agent-utils-mcp.fly.dev/api/v1/uuid_generate \
  -H "Content-Type: application/json" \
  -d '{"version": 4}'

# Parse URL
curl -X POST https://agent-utils-mcp.fly.dev/api/v1/url_parse \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/path?key=value"}'

# Datetime conversion
curl -X POST https://agent-utils-mcp.fly.dev/api/v1/datetime_convert \
  -H "Content-Type: application/json" \
  -d '{"dt_string": "2024-01-01 12:00:00", "from_tz": "UTC", "to_tz": "America/New_York"}'
```

## 💰 Pricing & x402 Payment

- **Free Tier**: First 100 requests per IP (resets after 24h)
- **Paid Tier**: $0.001 per request via x402 protocol

When the free tier is exhausted, you'll receive a `402 Payment Required` response with payment instructions.

### Using x402 Payments

```bash
curl -X POST https://agent-utils-mcp.fly.dev/api/v1/json_validate \
  -H "Content-Type: application/json" \
  -H "X-Payment: <payment-proof>" \
  -d '{"json_string": "{}"}'
```

## 📚 API Documentation

Interactive OpenAPI docs available at:
- **Swagger UI**: https://agent-utils-mcp.fly.dev/docs
- **ReDoc**: https://agent-utils-mcp.fly.dev/redoc

## 🔍 Discovery Endpoints

- **Health Check**: `/health`
- **Google A2A Agent Card**: `/.well-known/agent-card.json`
- **MCP Server Card**: `/.well-known/mcp/server-card.json`

## 🛠️ Development

### Local Setup

```bash
# Clone repository
git clone https://github.com/aparajithn/agent-utils-mcp.git
cd agent-utils-mcp

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Start server
python -m uvicorn src.main:app --reload
```

Server will be available at `http://localhost:8000`

### Environment Variables

- `PORT`: Server port (default: 8000)
- `X402_WALLET_ADDRESS`: Crypto wallet for x402 payments (optional, no paywall if not set)

## 🚢 Deployment

### Deploy to Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Deploy
flyctl deploy

# Set wallet address (optional)
flyctl secrets set X402_WALLET_ADDRESS=your_wallet_address
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Test specific tool
pytest tests/test_tools.py::test_json_validate
```

## 📖 Examples

### MCP Client (Python)

```python
from mcp import ClientSession
import asyncio

async def main():
    async with ClientSession("https://agent-utils-mcp.fly.dev/mcp") as session:
        result = await session.call_tool("json_validate", {
            "json_string": '{"key": "value"}'
        })
        print(result)

asyncio.run(main())
```

### REST Client (Python)

```python
import requests

response = requests.post(
    "https://agent-utils-mcp.fly.dev/api/v1/json_validate",
    json={"json_string": '{"key": "value"}'}
)
print(response.json())
```

### REST Client (JavaScript)

```javascript
const response = await fetch('https://agent-utils-mcp.fly.dev/api/v1/json_validate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ json_string: '{"key": "value"}' })
});

const result = await response.json();
console.log(result);
```

## 📝 Response Format

All endpoints return JSON with a consistent schema:

```json
{
  "success": true,
  "result": { ... }
}
```

Or on error:

```json
{
  "success": false,
  "error": "Error message"
}
```

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🔗 Links

- **Live Server**: https://agent-utils-mcp.fly.dev
- **GitHub**: https://github.com/aparajithn/agent-utils-mcp
- **Smithery**: Coming soon

## 💬 Support

For issues, questions, or feature requests, please open a GitHub issue.

---

Made with ❤️ by [Abu](https://github.com/aparajithn)
