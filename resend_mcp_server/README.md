# Resend MCP Server

A standalone MCP (Model Context Protocol) server for email functionality via [Resend](https://resend.com), deployed on Google Cloud Run.

This server exposes the Resend email API as an MCP endpoint that agents can connect to via Streamable HTTP transport.

---

## Features

- 📧 Send emails via Resend API
- 🔗 Streamable HTTP transport for MCP
- ☁️ Deployable on Cloud Run (with proxy wrapper to bypass host validation)
- 🔄 Reusable by multiple agents
- 🔐 API key passed via Authorization Bearer header (no secrets on server)

---

## Architecture

```
Client (Agent)
    │
    │ Authorization: Bearer <RESEND_API_KEY>
    ▼
Cloud Run (server.js - proxy)
    │
    │ Host: 127.0.0.1:3001
    ▼
Internal resend-mcp server (port 3001)
```

The proxy wrapper rewrites the `Host` header to localhost, bypassing resend-mcp's host validation.

---

## Prerequisites

- [Resend](https://resend.com) account and API key
- Google Cloud project with Cloud Run enabled
- `gcloud` CLI installed and configured

---

## Local Development

### 1. Install dependencies

```bash
npm install
```

### 2. Run locally

```bash
npm run dev
```

Server will be available at `http://localhost:3000/mcp`

### 3. Test with MCP Inspector

1. Run: `npx @modelcontextprotocol/inspector`
2. Transport: **Streamable HTTP**
3. URL: `http://127.0.0.1:3000/mcp`
4. Add header: `Authorization: Bearer <your-resend-api-key>`
5. Click Connect

---

## Deploy to Cloud Run

### 1. Navigate to the server folder

```bash
cd /path/to/adk-samples/resend_mcp_server
```

### 2. Deploy (no env vars needed - API key is passed by client)

```bash
gcloud run deploy resend-mcp-server \
  --source . \
  --project=gcp-experiments-490306 \
  --region=us-central1 \
  --allow-unauthenticated
```

### 3. Get the service URL

After deployment, note the URL (e.g., `https://resend-mcp-server-xxxxx-uc.a.run.app`).

The MCP endpoint will be at: `https://resend-mcp-server-xxxxx-uc.a.run.app/mcp`

---

## Using with Agents

Add these to your agent's `.env` file:

```bash
RESEND_MCP_URL=https://resend-mcp-server-xxxxx-uc.a.run.app/mcp
RESEND_API_KEY=re_xxxxxxxxxxxx
SENDER_EMAIL_ADDRESS=onboarding@resend.dev
```

Then connect via Streamable HTTP in your agent:

```python
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

resend_mcp_url = os.environ.get("RESEND_MCP_URL")
resend_api_key = os.environ.get("RESEND_API_KEY")

resend_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=resend_mcp_url,
        headers={
            "Authorization": f"Bearer {resend_api_key}"
        }
    ),
    tool_filter=['send-email']
)
```

---

## MCP Tools Exposed

| Tool | Description |
|------|-------------|
| `send-email` | Send an email via Resend |

---

## Undeploy

```bash
gcloud run services delete resend-mcp-server \
  --project=gcp-experiments-490306 \
  --region=us-central1 \
  --quiet
```

---

## Security Notes

- API key is passed via `Authorization: Bearer` header by the client (agent)
- No secrets stored on the MCP server itself
- On Resend's free tier with `onboarding@resend.dev`, emails can only be sent to your registered email
- To send to any recipient, [verify a custom domain](https://resend.com/domains)
