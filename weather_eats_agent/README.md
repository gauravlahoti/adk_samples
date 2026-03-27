# WeatherEats Agent 🍽️🌤️

An AI-powered restaurant discovery agent that combines **live weather data** and **real-time places search** to deliver context-aware dining recommendations — and optionally emails them to you.

Built with [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/) and powered by Gemini, it connects to external services exclusively through **Model Context Protocol (MCP)** servers.

---

## Features

- 🌦️ **Live weather lookup** before every restaurant search — recommendations adapt to current conditions (rain → indoor, sunny → rooftop, etc.)
- 🗺️ **Real-time restaurant search** via Google Maps Places — no hallucinated data, only live results
- 📧 **Email delivery** of recommendations via Resend
- 🔁 **Follow-up queries** — refine by cuisine, budget, or preference without re-entering your location
- 🛡️ **Safety guardrails** — content filtering enabled across all harm categories

---

## Architecture

```
User
 │
 ▼
WeatherEats Agent  (Google ADK LlmAgent — Gemini)
 ├── MCP Toolset: Google Maps MCP  (Streamable HTTP)
 │    ├── lookup_weather
 │    └── search_places
 └── MCP Toolset: Resend MCP       (stdio / npx)
      └── send-email
```

---

## MCP Servers

### 1. Google Maps MCP (`mapstools.googleapis.com/mcp`)

| Detail | Value |
|---|---|
| Transport | Streamable HTTP |
| Auth | `X-Goog-Api-Key` header |
| Tools used | `lookup_weather`, `search_places` |

Provides live weather conditions and nearby restaurant data. The agent always calls `lookup_weather` first to determine the dining context (indoor/outdoor suitability), then calls `search_places` to retrieve real restaurant listings.

### 2. Resend MCP (`resend-mcp` via npx)

| Detail | Value |
|---|---|
| Transport | stdio |
| Package | [`resend-mcp`](https://www.npmjs.com/package/resend-mcp) |
| Tools used | `send-email` |

Handles email delivery of recommendations. Launched as a child process via `npx -y resend-mcp`, with `RESEND_API_KEY` and `SENDER_EMAIL_ADDRESS` injected via environment variables.

> **Note:** On Resend's free tier with `onboarding@resend.dev` as the sender, emails can only be delivered to the address registered with your Resend account. To send to any recipient, [verify a custom domain](https://resend.com/domains) and update `SENDER_EMAIL_ADDRESS`.

---

## Prerequisites

- Python ≥ 3.14
- Node.js + `npx` (for the Resend MCP server)
- A Google Cloud project with Vertex AI enabled
- A [Google Maps API key](https://console.cloud.google.com/google/maps-apis) with Maps and Places APIs enabled
- A [Resend](https://resend.com) account and API key

---

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd weather_eats_agent
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

Create a `.env` file in this directory with the following variables
(use `.env.example` as a reference):

```bash
cp .env.example .env
# Then open .env and fill in your actual values
```

`.env` variables:

| Variable | Description |
|---|---|
| `GOOGLE_GENAI_USE_VERTEXAI` | Set to `1` to use Vertex AI |
| `GOOGLE_CLOUD_PROJECT` | Your GCP project ID |
| `GOOGLE_CLOUD_LOCATION` | GCP region (e.g. `us-central1`) |
| `MODEL` | Gemini model name (e.g. `gemini-2.5-flash-lite`) |
| `GOOGLE_MAPS_API_KEY` | Google Maps API key |
| `MAPS_MCP_URL` | Google Maps MCP endpoint URL |
| `RESEND_API_KEY` | Resend API key |
| `SENDER_EMAIL_ADDRESS` | Sender email address for Resend |

### 5. Authenticate with Google Cloud

```bash
gcloud auth application-default login
```

---

## Running the Agent

Start the ADK web interface:

```bash
adk web
```

Then open [http://localhost:8000](http://localhost:8000) in your browser and select **weather_eats_agent**.

---

## Example Interactions

```
User: Suggest dining options in Connaught Place, New Delhi.

Agent: The weather in Connaught Place is cloudy at 23.8°C — all dining
       settings are suitable.

       1. The Imperial Spice — 4.5 stars | ₹1800/person | Indoor | 12:00–23:30
          Fine dining experience well-suited for a pleasant cloudy evening.
       ...

       Would you like me to send these recommendations to your email?
```

```
User: Show me only vegetarian options under ₹500.

Agent: [calls search_places with refined filters, returns fresh results]
```

---

## Project Structure

```
Track_2/
├── weather_eats_agent/
│   ├── __init__.py
│   ├── agent.py          # Agent definition, MCP toolset wiring
│   └── prompts.py        # System instruction for the LLM
├── .env.example          # Environment variable template
├── .gitignore
├── pyproject.toml
└── README.md
```

---

## Security

- `.env` is excluded from version control via `.gitignore`
- API keys are read from environment variables — never hardcoded
- All four Gemini harm categories are blocked at `BLOCK_LOW_AND_ABOVE`
- Restaurant data is sourced exclusively from live tool calls — the LLM is explicitly prohibited from using training knowledge for place data
