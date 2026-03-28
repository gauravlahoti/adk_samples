# Resend MCP Server

A standalone MCP (Model Context Protocol) server for email functionality via [Resend](https://resend.com), deployed on Google Cloud Run.

This server exposes the Resend email API as an MCP endpoint that agents can connect to via Streamable HTTP transport.

---

## Features

- 📧 Send emails via Resend API
- 🔗 Streamable HTTP transport for MCP
- ☁️ Deployable on Cloud Run
- 🔄 Reusable by multiple agents

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

### 2. Set environment variables

```bash
cp .env.example .env
# Edit .env with your RESEND_API_KEY
```

### 3. Run locally

```bash
npm run dev
```

Server will be available at `http://localhost:3000/mcp`

---

## Deploy to Cloud Run

### 1. Navigate to the server folder

```bash
cd /path/to/adk-samples/resend_mcp_server
```

### 2. Set environment variables

```bash
export GOOGLE_CLOUD_PROJECT="gcp-experiments-490306"
export GOOGLE_CLOUD_LOCATION="us-central1"
export RESEND_API_KEY="your_resend_api_key"
export SENDER_EMAIL_ADDRESS="onboarding@resend.dev"
```

### 3. Deploy directly (no Dockerfile needed)

```bash
gcloud run deploy resend-mcp-server \
  --source . \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=$GOOGLE_CLOUD_LOCATION \
  --allow-unauthenticated \
  --set-env-vars="RESEND_API_KEY=$RESEND_API_KEY,SENDER_EMAIL_ADDRESS=$SENDER_EMAIL_ADDRESS"
```

### 3. Get the service URL

After deployment, note the URL (e.g., `https://resend-mcp-server-xxxxx-uc.a.run.app`).

The MCP endpoint will be at: `https://resend-mcp-server-xxxxx-uc.a.run.app/mcp`

---

## Using with Agents

Add this URL to your agent's `.env` file:

```bash
RESEND_MCP_URL=https://resend-mcp-server-xxxxx-uc.a.run.app/mcp
```

Then connect via Streamable HTTP in your agent:

```python
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

resend_mcp_url = os.environ.get("RESEND_MCP_URL")

resend_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=resend_mcp_url
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
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=$GOOGLE_CLOUD_LOCATION \
  --quiet
```

---

## Security Notes

- The MCP server authenticates to Resend using the `RESEND_API_KEY` environment variable
- On Resend's free tier with `onboarding@resend.dev`, emails can only be sent to your registered email
- To send to any recipient, [verify a custom domain](https://resend.com/domains)
