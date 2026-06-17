# FortiAppSec MCP Server

MCP server for managing Fortinet FortiAppSec (WAF as a Service) via AI agents. Built with FastMCP, deployed as a container.

## Tools

| Tool | Description |
|------|-------------|
| `waf_list_applications` | List all WAF applications |
| `waf_get_application` | Get details of a specific WAF application |
| `waf_create_application` | Create a new WAF application |
| `waf_delete_application` | Delete a WAF application |
| `waf_list_templates` | List available WAF templates |

Every tool accepts an optional `appsec_api_key` parameter. If not provided, the server reads from the `FORTINET_APPSEC_API_KEY` environment variable. Per-call parameter overrides the environment variable.

## Connect from Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "fortiappsec": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp-fortiappsec.fortidemoscloud.com/mcp"
      ]
    }
  }
}
```

## Connect from Gemini CLI

Add to your Gemini settings (`~/.gemini/settings.json`):

```json
{
  "mcpServers": {
    "fortiappsec": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp-fortiappsec.fortidemoscloud.com/mcp"
      ]
    }
  }
}
```

## Connect from Kiro / VS Code

Add to `.kiro/settings/mcp.json` or equivalent:

```json
{
  "mcpServers": {
    "fortiappsec": {
      "url": "https://mcp-fortiappsec.fortidemoscloud.com/mcp"
    }
  }
}
```

## Test with curl

```bash
# 1. Initialize session and capture Mcp-Session-Id from headers
export SESSION_ID=$(curl -s -i -X POST https://mcp-fortiappsec.fortidemoscloud.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test-curl","version":"1.0"}}}' \
  | grep -i "mcp-session-id" | awk '{print $2}' | tr -d '\r')

echo "Session ID: $SESSION_ID"

# 2. List tools using the captured Session ID
curl -s -X POST https://mcp-fortiappsec.fortidemoscloud.com/mcp \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'

# 3. Call a tool (list WAF applications)
curl -s -X POST https://mcp-fortiappsec.fortidemoscloud.com/mcp \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"waf_list_applications","arguments":{"appsec_api_key":"YOUR_API_KEY"}}}'
```

## Run locally

```bash
# Docker (with API key from environment)
export FORTINET_APPSEC_API_KEY="your_api_key_here"
docker-compose up --build -d

# Or directly
uv sync
FORTINET_APPSEC_API_KEY="your_api_key_here" uv run uvicorn app.server:app --host 0.0.0.0 --port 8000
```

Server available at `http://localhost:8000/mcp` with health check at `/health`.

## Deploy to Kubernetes

```bash
kubectl apply -f k8s-deployment.yaml
```

Exposes on NodePort 30082. Image: `jviguerasfortinet/mcp-fortiappsec-server:v1.0.0`

## Tool Parameters

### waf_create_application

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `app_name` | Yes | — | Application name |
| `domain_name` | Yes | — | Primary domain name |
| `server_address` | Yes | — | Backend server address |
| `appsec_api_key` | No | "" | FortiAppSec API key (uses env var if not provided) |
| `server_port` | No | 80 | Backend server port |
| `extra_domains` | No | "" | Additional domains (comma-separated) |
| `custom_port_http` | No | 80 | HTTP listening port |
| `custom_port_https` | No | 443 | HTTPS listening port |
| `cdn_status` | No | 0 | CDN status (0=disabled, 1=enabled) |
| `region` | No | eu-west-1 | Cloud region |
| `platform` | No | AWS | Platform type |
| `block_mode` | No | 1 | Block mode (0=monitor, 1=block) |
| `service` | No | http,https | Services (comma-separated) |
| `server_type` | No | http | Server type |
| `server_country` | No | Ireland | Server country |
| `template_id` | No | 355e3ce6-... | Template ID |

### waf_list_applications / waf_list_templates

| Parameter | Required | Description |
|-----------|----------|-------------|
| `appsec_api_key` | No | FortiAppSec API key (uses `FORTINET_APPSEC_API_KEY` env var if not provided) |

### waf_get_application / waf_delete_application

| Parameter | Required | Description |
|-----------|----------|-------------|
| `app_id` | Yes | Application ID |
| `appsec_api_key` | No | FortiAppSec API key (uses `FORTINET_APPSEC_API_KEY` env var if not provided) |

## License

MIT
