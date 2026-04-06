# ADK Samples

A collection of agent samples built with [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/) and powered by Gemini.

---

## Structure

```
adk-samples/
├── error-lens-mas/              # Multi-agent GCP error triage system (ErrorLens)
├── error-kb-agent/              # Error knowledge bank agent with A2A support
├── error-kb-toolbox/            # MCP Toolbox for Databases (AlloyDB + pgvector)
├── weather_eats_agent/          # AI-powered restaurant discovery agent
├── email_triage_agent/          # AI-powered email triage agent
├── legal_case_assistant_agent/  # AI-powered legal research assistant
└── resend_mcp_server/           # Standalone MCP server for email via Resend
```

---

## Samples

| Agent / Service | Description | Tools |
|-----------------|-------------|-------|
| [error-lens-mas](error-lens-mas/) | Multi-agent GCP error triage system. Turns raw errors into structured triage, parallel research, confidence-scored synthesis, and developer-facing responses. | Google Search, Developer Knowledge MCP |
| [error-kb-agent](error-kb-agent/) | Error knowledge bank agent exposed as a remote A2A service. Searches, records, and manages GCP error resolutions from AlloyDB. | ToolboxToolset (MCP Toolbox) |
| [error-kb-toolbox](error-kb-toolbox/) | MCP Toolbox for Databases deployment providing semantic error search, fix tracking, and case management over AlloyDB with pgvector embeddings. | MCP Toolbox for Databases |
| [weather_eats_agent](weather_eats_agent/) | Recommends restaurants based on live weather and location. Combines Google Maps MCP for weather/places lookup with Resend MCP for email delivery. | MCP (Google Maps, Resend) |
| [email_triage_agent](email_triage_agent/) | Automated first-pass triage layer for business inboxes. Classifies, prioritizes, detects escalation risks, and routes emails to the right team. | Custom Python tools |
| [legal_case_assistant_agent](legal_case_assistant_agent/) | Searches Indian civil and family law cases using natural language. Performs semantic similarity search over court judgments in AlloyDB via MCP Toolbox for Databases. | ToolboxToolset (MCP Toolbox) |
| [resend_mcp_server](resend_mcp_server/) | Standalone MCP server exposing the Resend email API over Streamable HTTP. Deployable on Cloud Run; reusable by any agent. | Node.js, Resend API |

---

## Getting Started

Each agent is a self-contained project with its own:
- `pyproject.toml` — project configuration
- `README.md` — setup and usage instructions
- `.env.template` — environment variable template

### Quick Start

```bash
# Navigate to an agent
cd weather_eats_agent  # or email_triage_agent

# Create virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv sync

# Configure environment
cp .env.template .env
# Edit .env with your values

# Run the agent
adk web
```

Then open [http://localhost:8000](http://localhost:8000) and select the agent.

### Quick Start — Resend MCP Server

```bash
cd resend_mcp_server
npm install
npm run dev
```

Server will be available at `http://localhost:3000/mcp`. See the [resend_mcp_server README](resend_mcp_server/) for Cloud Run deployment.

---

## Prerequisites

- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) package manager
- [Node.js](https://nodejs.org/) >= 18 (for `resend_mcp_server`)
- Google Cloud project with Vertex AI enabled
- `gcloud auth application-default login` for authentication

---