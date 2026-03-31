"""
Legal Case Assistant Agent - Main Agent Definition

An AI-powered legal research assistant that searches Indian legal cases
using semantic similarity search over an AlloyDB database via MCP Toolbox
for Databases.

Built with Google Agent Development Kit (ADK) and powered by Gemini.
"""

import os
import logging
import google.cloud.logging
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from typing import Optional
from google.genai.types import (
    GenerateContentConfig,
    SafetySetting,
    HarmCategory,
    HarmBlockThreshold,
)

from legal_case_assistant_agent.prompts import AGENT_INSTRUCTION
from legal_case_assistant_agent.tools import legal_toolset

# --- Setup Cloud Logging ---
cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()

# --- Logging Constants ---
LOG_PREFIX = "LEGAL_CASE_AGENT"

logging.info(f"{LOG_PREFIX}:STARTUP - Legal Case Assistant Agent initializing...")

load_dotenv()

gemini_model = os.environ.get("MODEL", "gemini-2.0-flash")
logging.info(f"{LOG_PREFIX}:CONFIG - model={gemini_model}")


# --- Agent Callbacks for Input/Output Logging ---

def before_agent_callback(callback_context: CallbackContext) -> Optional[dict]:
    """
    Called before the agent processes a request.
    Logs the user's input prompt.
    """
    user_message = callback_context.user_content
    session_id = callback_context.state.get("session_id", "unknown")

    if hasattr(user_message, "parts"):
        prompt_text = " ".join(
            [p.text for p in user_message.parts if hasattr(p, "text")]
        )
    else:
        prompt_text = str(user_message)

    logging.info(
        f"{LOG_PREFIX}:INPUT - session={session_id} | prompt={prompt_text[:500]}"
    )
    callback_context.state["current_prompt"] = prompt_text

    return None


def after_agent_callback(
    callback_context: CallbackContext,
) -> Optional[LlmResponse]:
    """
    Called after the agent generates a response.
    Logs the final agent response.
    """
    session_id = callback_context.state.get("session_id", "unknown")
    prompt = callback_context.state.get("current_prompt", "unknown")

    if (
        hasattr(callback_context, "agent_response")
        and callback_context.agent_response
    ):
        response_text = str(callback_context.agent_response)
    else:
        response_text = "(response captured in event stream)"

    logging.info(
        f"{LOG_PREFIX}:OUTPUT - session={session_id} | response={response_text[:500]}"
    )
    logging.info(
        f"{LOG_PREFIX}:SUMMARY - session={session_id} | input_length={len(prompt)} | output_length={len(response_text)}"
    )

    return None


# --- Root Agent ---
root_agent = LlmAgent(
    model=gemini_model,
    name="legal_case_assistant",
    description=(
        "An AI legal research assistant that searches Indian civil and family "
        "law cases including eviction orders, partition cases, divorce decrees, "
        "and rent revision cases using semantic search over a legal case database."
    ),
    instruction=AGENT_INSTRUCTION,
    tools=[legal_toolset],
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
    generate_content_config=GenerateContentConfig(
        temperature=.4,
        top_k=20,
        top_p=0.85,
        max_output_tokens=4000,
        safety_settings=[
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=HarmBlockThreshold.BLOCK_ONLY_HIGH,
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=HarmBlockThreshold.BLOCK_ONLY_HIGH,
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=HarmBlockThreshold.BLOCK_ONLY_HIGH,
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=HarmBlockThreshold.BLOCK_ONLY_HIGH,
            ),
        ],
    ),
)
