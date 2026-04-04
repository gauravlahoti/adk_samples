# Legal Case Assistant Agent

An AI-powered legal research assistant that searches **Indian civil and family law cases** using natural language queries. It performs semantic similarity search over court judgments stored in AlloyDB via [MCP Toolbox for Databases](https://github.com/googleapis/genai-toolbox).

Built with [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/) and powered by Gemini.

---

## The Problem

Legal professionals and individuals often need to research past court judgments to understand precedents, outcomes, and legal reasoning. Manually searching through thousands of case records across different courts and states is time-consuming, requires specialized knowledge of legal databases, and often misses relevant cases due to keyword limitations.

---

## What This Agent Solves

The Legal Case Assistant Agent provides **instant natural language search** over a database of Indian legal cases. Ask a question in plain English and get relevant case precedents with full details.

| Capability | Description |
|------------|-------------|
| **Semantic Search** | Finds cases by meaning, not just keywords |
| **Case Types** | Eviction orders, partition cases, divorce decrees, rent revision |
| **Structured Results** | Case details, court, parties, outcome, summary |
| **Relevance Scoring** | Ranks results by semantic similarity |
| **Research Disclaimers** | Always reminds users to consult a qualified advocate |

---

## Features

- **Natural language queries** — describe a legal situation in plain English
- **Semantic similarity search** — powered by `text-embedding-005` embeddings in AlloyDB
- **Structured case presentation** — case title, court, parties, outcome, summary, relevance score
- **Domain-focused** — Indian civil and family law (eviction, partition, divorce, rent revision)
- **Safety guardrails** — never provides legal advice, always recommends professional consultation
- **Cloud Logging** — structured logs with `LEGAL_CASE_AGENT:` prefix for monitoring

---

## Architecture

```
User
 |
 v
Legal Case Assistant Agent  (Google ADK LlmAgent - Gemini)
 |
 +-- ToolboxToolset (MCP Toolbox for Databases)
       |
       +-- Tool: search-legal-cases
             |
             v
           AlloyDB (PostgreSQL)
             - legal_cases table
             - text-embedding-005 vector embeddings
             - pgvector similarity search
```

### How It Works

1. User asks a legal question in natural language
2. Agent calls `search-legal-cases` via MCP Toolbox
3. Toolbox executes a semantic similarity search in AlloyDB using `text-embedding-005`
4. Top 5 most relevant cases are returned with similarity scores
5. Agent presents results in a structured format with disclaimers

---

## Tools

### search-legal-cases (via MCP Toolbox)

| Detail | Value |
|--------|-------|
| Purpose | Search Indian legal cases using natural language |
| Source | AlloyDB (PostgreSQL) via MCP Toolbox |
| Input | `query` (string) — natural language search query |
| Output | Top 5 matching cases with similarity scores |

**Fields returned per case:**
- `case_id`, `case_type`, `case_title`
- `court_name`, `state`, `judgment_date`
- `petitioner`, `respondent`
- `outcome`, `case_summary`
- `similarity_score` (0-1, higher = more relevant)

---

## Prerequisites

- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) package manager
- A Google Cloud project with Vertex AI enabled
- AlloyDB instance with the `legal_cases` table and vector embeddings
- [MCP Toolbox for Databases](https://github.com/googleapis/genai-toolbox) binary

---

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd legal_case_assistant_agent
```

### 2. Create and activate a virtual environment

```bash
uv venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
uv sync
```

### 4. Configure environment variables

Edit `legal_case_assistant_agent/.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_GENAI_USE_VERTEXAI` | Set to `1` to use Vertex AI | `1` |
| `GOOGLE_CLOUD_PROJECT` | Your GCP project ID | — |
| `GOOGLE_CLOUD_LOCATION` | GCP region | `us-central1` |
| `TOOLBOX_URL` | MCP Toolbox server URL | `http://127.0.0.1:5000` |
| `MODEL` | Gemini model name | `gemini-2.5-flash` |

### 5. Start MCP Toolbox for Databases

In a separate terminal, navigate to the `mcp-toolbox/` directory:

```bash
cd mcp-toolbox
source .env
./toolbox --config "tools.yaml" --ui --enable-api
```

The toolbox server will start at `http://127.0.0.1:5000`. You can verify tools at `http://127.0.0.1:5000/ui`.

### 6. Authenticate with Google Cloud

```bash
gcloud auth application-default login
```

---

## Running the Agent

### ADK Web Interface

```bash
adk web
```

Open [http://localhost:8000](http://localhost:8000) and select **legal_case_assistant_agent**.

### ADK CLI

```bash
adk run legal_case_assistant_agent
```

### Example Queries

- "Find eviction cases in Maharashtra"
- "Show me divorce cases involving child custody"
- "Partition cases related to ancestral property in Delhi"
- "Rent revision disputes where the tenant won"
- "Cases about illegal occupancy by tenants"

---

## Deploying to Cloud Run

### 1. Set environment variables

```bash
source mcp-toolbox/.env
export SERVICE_NAME="legal-case-toolbox"
export IMAGE="us-central1-docker.pkg.dev/database-toolbox/toolbox/toolbox:v0.31.0"
```

### 2. Create a Secret in Secret Manager for tools.yaml

```bash
gcloud secrets create tools \
    --project=$PROJECT_ID \
    --data-file=tools.yaml
```

> **Note:** Each MCP Toolbox deployment should use its own secret. If you are
> deploying multiple toolbox instances (e.g. `legal-case-toolbox` and
> `error-kb-toolbox`), create separate secrets with distinct names and
> reference them in `--set-secrets` accordingly.

### 3. Deploy MCP Toolbox to Cloud Run

> **Toolbox v0.31.0+ Breaking Change:** The REST API (`/api/toolset/...`) is
> disabled by default. You **must** pass `--enable-api` in `--args` for the
> UI and API endpoints to work.

```bash
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE \
    --service-account $SERVICE_ACCOUNT \
    --region $REGION \
    --project $PROJECT_ID \
    --set-secrets "/app/tools.yaml=tools:latest" \
    --set-env-vars "PROJECT_ID=$PROJECT_ID,REGION=$REGION,CLUSTER_NAME=$CLUSTER_NAME,INSTANCE_NAME=$INSTANCE_NAME,DATABASE_NAME=$DATABASE_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,ALLOYDB_PUBLIC_IP=$ALLOYDB_PUBLIC_IP" \
    --args="--config=/app/tools.yaml,--address=0.0.0.0,--port=8080,--ui,--enable-api" \
    --port=8080 \
    --allow-unauthenticated
```

### 4. Deploy the Agent to Cloud Run

> **Important:** The agent source directory must contain a `requirements.txt` listing
> extra dependencies (`toolbox-adk`, `toolbox-core`, etc.) — the ADK-generated
> Dockerfile only installs `google-adk` by default.

```bash
adk deploy cloud_run \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=$GOOGLE_CLOUD_LOCATION \
  --service_name=legal-case-assistant-agent \
  --with_ui \
  ./legal_case_assistant_agent
```

**Parameters:**

| Parameter | Description |
|-----------|-------------|
| `--project` | Your Google Cloud project |
| `--region` | Deployment region (e.g., `us-central1`) |
| `--service_name` | Name for Cloud Run service |
| `--with_ui` | Include web interface (optional but recommended) |
| `./legal_case_assistant_agent` | Your agent directory |

After deployment completes, the CLI will output a URL like:
```
https://legal-case-assistant-agent-xxxxxx-uc.a.run.app
```

Open the URL in your browser to access the ADK Web UI.

### 5. Undeploy the agent

To delete the Cloud Run service:

```bash
source legal_case_assistant_agent/.env
gcloud run services delete legal-case-assistant-service \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=$GOOGLE_CLOUD_LOCATION \
  --quiet
```

### 6. View logs in Cloud Logging

```
resource.type="cloud_run_revision"
resource.labels.service_name="legal-case-assistant-service"
jsonPayload.message=~"LEGAL_CASE_AGENT"
```

**Log prefixes:**

| Prefix | Description |
|--------|-------------|
| `LEGAL_CASE_AGENT:STARTUP` | Agent initialization |
| `LEGAL_CASE_AGENT:CONFIG` | Configuration details |
| `LEGAL_CASE_AGENT:INPUT` | User prompts |
| `LEGAL_CASE_AGENT:OUTPUT` | Agent responses |
| `LEGAL_CASE_AGENT:SUMMARY` | Request/response summary |

---

## Project Structure

```
legal_case_assistant_agent/
├── legal_case_assistant_agent/     # Agent package
│   ├── __init__.py                 # Package init
│   ├── agent.py                    # Main agent definition
│   ├── prompts.py                  # Instruction prompts
│   ├── tools.py                    # Toolbox connection setup
│   ├── requirements.txt            # Extra pip deps for Cloud Run
│   └── .env                        # Agent environment variables
├── mcp-toolbox/                    # MCP Toolbox configuration
│   ├── toolbox                     # Toolbox binary (darwin/arm64)
│   ├── tools.yaml                  # Source, tool, and toolset definitions
│   └── .env                        # Toolbox environment variables
└── README.md
```

---

## Agent Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `temperature` | 0.4 | Low temperature for factual, consistent legal research output |
| `top_k` | 20 | Focused token selection for precise legal terminology |
| `top_p` | 0.85 | Conservative nucleus sampling for reliable results |
| `max_output_tokens` | 4000 | Sufficient for detailed multi-case presentation |
| Safety settings | `BLOCK_ONLY_HIGH` | Permissive threshold since legal content may contain sensitive topics (disputes, custody, eviction) |

---

## Changelog

### v0.1.0

- Initial release
- Semantic search over Indian legal cases via MCP Toolbox for Databases
- Support for eviction, partition, divorce, and rent revision case types
- Structured case presentation with relevance scoring
- Cloud Logging integration with structured log prefixes
