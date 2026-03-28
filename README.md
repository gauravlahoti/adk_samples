# ADK Samples

A collection of agent samples built with [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/) and powered by Gemini.

---

## Structure

```
adk-samples/
├── weather_eats_agent/     # AI-powered restaurant discovery agent
└── email_triage_agent/     # AI-powered email triage agent
```

---

## Samples

| Agent | Description | Tools |
|-------|-------------|-------|
| [weather_eats_agent](weather_eats_agent/) | Recommends restaurants based on live weather and location. Combines Google Maps MCP for weather/places lookup with Resend MCP for email delivery. | MCP (Google Maps, Resend) |
| [email_triage_agent](email_triage_agent/) | Automated first-pass triage layer for business inboxes. Classifies, prioritizes, detects escalation risks, and routes emails to the right team. | Custom Python tools |

---

## Getting Started

Each agent is a self-contained project with its own:
- `pyproject.toml` — project configuration
- `README.md` — setup and usage instructions
- `.env.example` — environment variable template

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
cp .env.example .env
# Edit .env with your values

# Run the agent
adk web
```

Then open [http://localhost:8000](http://localhost:8000) and select the agent.

---

## Prerequisites

- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) package manager
- Google Cloud project with Vertex AI enabled
- `gcloud auth application-default login` for authentication

---